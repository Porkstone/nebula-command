#!/usr/bin/env python3
"""Bounded, private-input Windows sign-in session over the pinned KVM API."""

import argparse
import hashlib
import json
from pathlib import Path
import queue
import sys
import threading
import time
from urllib.parse import urlencode
import uuid

from fleet_secrets import ROOT, ERROR_CODES, KvmClient, SecretError, Store, consume_input
from dependabot_deploy import windows_command
from windows_ssh_setup import windows_command as ssh_setup_command


def jpeg_size(data):
    """Read JPEG SOF dimensions without decoding/storing any credentials."""
    if not data.startswith(b"\xff\xd8"):
        raise SecretError("invalid_snapshot")
    offset = 2
    try:
        while offset < len(data):
            if data[offset] != 255:
                raise ValueError()
            while data[offset] == 255:
                offset += 1
            marker = data[offset]
            offset += 1
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            size = int.from_bytes(data[offset:offset + 2], "big")
            if size < 2 or offset + size > len(data):
                raise ValueError()
            if marker in (0xC0, 0xC1, 0xC2):
                height = int.from_bytes(data[offset + 3:offset + 5], "big")
                width = int.from_bytes(data[offset + 5:offset + 7], "big")
                if not 0 < width <= 8192 or not 0 < height <= 8192:
                    raise ValueError()
                return width, height
            offset += size
    except (IndexError, ValueError):
        pass
    raise SecretError("invalid_snapshot")


class ConsoleSession:
    def __init__(self, kvm, windows, pin, output_directory, client_factory=KvmClient, clock=time.monotonic, pause=time.sleep, allow_dependabot_install=False, allow_ssh_setup=False):
        if (kvm.get("kind", "kvm") != "kvm" or windows.get("kind") != "windows-console"
                or kvm["machine_id"] != windows["machine_id"]
                or windows["origin"] != f"console://{kvm['machine_id']}" or not pin):
            raise SecretError("console_binding_mismatch")
        self.client = client_factory(kvm["origin"], None, pin)
        self.kvm = kvm
        self.windows = windows
        self.output = Path(output_directory)
        self.output.mkdir(parents=True, exist_ok=False)
        self.clock, self.pause = clock, pause
        self.expires = clock() + 600
        self.token = None
        self.frame = None
        self.frame_number = 0
        self.password_attempted = False
        self.allow_dependabot_install = allow_dependabot_install
        self.allow_ssh_setup = allow_ssh_setup
        self.installer_kind = None
        self.installer_opened = False
        self.install_attempted = False

    def login(self):
        result = self.client.request("POST", "/api/auth/login", urlencode({
            "user": self.kvm["username"], "passwd": self.kvm["password"], "expire": "600",
        }).encode())
        self.kvm = None
        if result.get("two_step_required"):
            raise SecretError("kvm_operator_confirmation_required")
        token = result.get("token")
        import re
        if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,512}", token):
            raise SecretError("kvm_session_not_established")
        self.token = token

    def request(self, method, path, body=None, **kwargs):
        if self.clock() >= self.expires:
            raise SecretError("console_session_expired")
        return self.client.request(method, path, body=body, token=self.token, **kwargs)

    def snapshot(self):
        data = self.request("GET", "/api/streamer/snapshot", response_type="jpeg")
        width, height = jpeg_size(data)
        self.frame_number += 1
        path = self.output / f"screen-{self.frame_number:03d}.jpg"
        path.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        self.frame = {"sha256": digest, "width": width, "height": height, "at": self.clock()}
        return {"ok": True, "status": "snapshot", "path": str(path.resolve()),
                "sha256": digest, "width": width, "height": height}

    def key(self, key, state=None):
        if state is None:
            try:
                self.key(key, True)
                self.pause(0.08)
            finally:
                self.key(key, False)
            return
        query = {"key": key}
        if state is not None:
            query["state"] = "1" if state else "0"
        self.request("POST", "/api/hid/events/send_key?" + urlencode(query))

    def chord(self, keys):
        pressed = []
        try:
            for key in keys:
                pressed.append(key)
                self.key(key, True)
                self.pause(0.08)
        finally:
            for key in reversed(pressed):
                self.key(key, False)

    def check_frame(self, command):
        if (not self.frame or self.clock() - self.frame["at"] > 60
                or command.get("sha256") != self.frame["sha256"]):
            raise SecretError("console_snapshot_required")

    def click(self, command):
        self.check_frame(command)
        x, y = command.get("x"), command.get("y")
        if (type(x) is not int or type(y) is not int
                or not 0 <= x < self.frame["width"] or not 0 <= y < self.frame["height"]):
            raise SecretError("console_command_rejected")
        to_x = round(x * 65535 / max(1, self.frame["width"] - 1)) - 32768
        to_y = round(y * 65535 / max(1, self.frame["height"] - 1)) - 32768
        self.request("POST", "/api/hid/events/send_mouse_move?" + urlencode({"to_x": to_x, "to_y": to_y}))
        self.request("POST", "/api/hid/events/send_mouse_button?button=left")
        self.pause(0.2)

    def command(self, command):
        if not isinstance(command, dict):
            raise SecretError("console_command_rejected")
        operation = command.get("operation")
        if operation == "snapshot":
            return self.snapshot()
        if operation in ("open-dependabot-installer", "install-dependabot", "open-ssh-setup", "setup-ssh"):
            ssh_mode = operation in ("open-ssh-setup", "setup-ssh")
            allowed = self.allow_ssh_setup if ssh_mode else self.allow_dependabot_install
            kind = 'ssh' if ssh_mode else 'dependabot'
            if not allowed or self.install_attempted:
                raise SecretError("console_command_rejected")
            self.check_frame(command)
            if operation in ("open-dependabot-installer", "open-ssh-setup"):
                if self.installer_opened or command.get("desktop_confirmed") is not True:
                    raise SecretError("console_command_rejected")
                self.installer_opened = True
                self.installer_kind = kind
                self.chord(["MetaLeft", "KeyR"])
                self.pause(1)
                text = "powershell -NoProfile -NoExit"
            else:
                if not self.installer_opened or self.installer_kind != kind or command.get("shell_confirmed") is not True:
                    raise SecretError("console_command_rejected")
                text = ssh_setup_command() if ssh_mode else windows_command()
                self.install_attempted = True
                # Clear any unsubmitted input in the visually confirmed shell.
                self.chord(["ControlLeft", "KeyC"])
            # Slow HID entry of a whole script can exceed the HTTPS timeout.
            # Never retry an ambiguous chunk or press Enter after a failed one.
            for offset in range(0, len(text), 96):
                self.request("POST", "/api/hid/print?limit=128&slow=true", body=text[offset:offset + 96].encode("utf-8"),
                             content_type="text/plain; charset=utf-8")
            self.key("Enter")
            self.pause(3)
            return self.snapshot()
        if self.password_attempted:
            raise SecretError("console_attempt_already_used")
        if operation == "unlock":
            self.chord(["ControlLeft", "AltLeft", "Delete"])
        elif operation == "key" and command.get("key") in ("Tab", "Enter", "Escape"):
            self.key(command["key"])
        elif operation == "click":
            self.click(command)
        elif operation in ("username", "submit-password"):
            self.check_frame(command)
            if command.get("field_confirmed") is not True:
                raise SecretError("console_command_rejected")
            self.click(command)
            self.chord(["ControlLeft", "KeyA"])
            if operation == "submit-password":
                # Set before transmitting: an ambiguous result must not be retried.
                self.password_attempted = True
            text = self.windows["username" if operation == "username" else "password"]
            self.request("POST", "/api/hid/print?limit=4096&slow=true", body=text.encode("utf-8"),
                         content_type="text/plain; charset=utf-8")
            if operation == "submit-password":
                self.key("Enter")
        else:
            raise SecretError("console_command_rejected")
        self.pause(1.5)
        return self.snapshot()

    def close(self):
        try:
            if self.token:
                self.client.request("POST", "/api/auth/logout", token=self.token)
        except Exception:
            raise SecretError("kvm_logout_unconfirmed") from None
        finally:
            self.token = None
            self.windows = None
            self.kvm = None


def emit(value):
    print(json.dumps(value), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", required=True, type=Path, help="Disposable T3 private key input; consumed")
    parser.add_argument("--allow-dependabot-install", action="store_true", help="Enable fixed, visually gated Dependabot installation on win-srv-01")
    parser.add_argument("--allow-ssh-setup", action="store_true", help="Enable fixed, visually gated OpenSSH bootstrap on win-srv-01")
    args = parser.parse_args(argv)
    session = None
    try:
        private = consume_input(args.input_file)
        store = Store()
        target, _ = store.target("win-srv-01-kvm")
        kvm = store.decrypt("win-srv-01-kvm", private)
        windows = store.decrypt("win-srv-01-console", private)
        del private
        session = ConsoleSession(kvm, windows, target.get("tls_pin_sha256"),
                                 ROOT / ".local/kvm-console" / uuid.uuid4().hex,
                                 allow_dependabot_install=args.allow_dependabot_install,
                                 allow_ssh_setup=args.allow_ssh_setup)
        session.login()
        emit(session.snapshot())
        commands = queue.Queue()

        def read_commands():
            for line in sys.stdin:
                commands.put(line)
            commands.put(None)

        threading.Thread(target=read_commands, daemon=True).start()
        while True:
            try:
                line = commands.get(timeout=max(0.01, session.expires - session.clock()))
            except queue.Empty:
                raise SecretError("console_session_expired") from None
            if line is None:
                break
            try:
                command = json.loads(line)
            except ValueError:
                raise SecretError("console_command_rejected") from None
            if command == {"operation": "finish"}:
                break
            emit(session.command(command))
        session.close()
        session = None
        emit({"ok": True, "status": "console_closed_and_kvm_logged_out"})
        return 0
    except SecretError as exc:
        emit({"ok": False, "code": str(exc) if str(exc) in ERROR_CODES else "operation_failed"})
        return 1
    except KeyboardInterrupt:
        emit({"ok": False, "code": "interrupted"})
        return 130
    except Exception:
        emit({"ok": False, "code": "operation_failed"})
        return 1
    finally:
        if session:
            try:
                session.close()
            except Exception:
                emit({"ok": False, "code": "kvm_logout_unconfirmed"})


if __name__ == "__main__":
    sys.exit(main())
