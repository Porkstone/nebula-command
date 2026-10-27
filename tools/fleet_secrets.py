#!/usr/bin/env python3
"""Use operator-supplied age keys without returning secret values to the caller."""

import argparse
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import ssl
import stat
import subprocess
import sys
from urllib.parse import urlencode, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 65536
IDENTITY = re.compile(r"AGE-SECRET-KEY-(?:PQ-)?1[0-9A-Z]+")
BECH32 = "023456789acdefghjklmnpqrstuvwxyz"
RECIPIENT = re.compile(rf"(?:age1[{BECH32}]{{58}}|age1pq1[{BECH32}]{{1000,4000}})")
ERROR_CODES = frozenset({
    "unsafe_input_file", "input_read_or_cleanup_failed", "invalid_input_size",
    "age_not_installed", "age_execution_failed", "age_operation_failed", "invalid_age_output",
    "invalid_json", "invalid_catalog", "unsafe_ciphertext_path",
    "invalid_catalog_or_unknown_credential", "credential_already_exists",
    "invalid_public_recipient", "invalid_password_input", "invalid_username",
    "credential_missing_or_too_large", "invalid_identity_input", "invalid_credential_payload",
    "credential_binding_mismatch", "kvm_rate_limited", "kvm_redirect_refused",
    "kvm_request_rejected", "invalid_kvm_response", "kvm_certificate_untrusted",
    "kvm_connection_failed", "kvm_operator_confirmation_required",
    "kvm_session_not_established", "kvm_logout_unconfirmed",
})


class SecretError(Exception):
    """Only fixed, nonsecret codes may reach CLI output."""


def consume_input(path, root=ROOT):
    """Read and remove a disposable T3 input file, never a durable identity file."""
    source = Path(path)
    if not source.is_absolute() or source.is_symlink():
        raise SecretError("unsafe_input_file")
    try:
        resolved = source.resolve(strict=True)
        if resolved.is_relative_to(root.resolve()) or not stat.S_ISREG(resolved.stat().st_mode):
            raise SecretError("unsafe_input_file")
        try:
            with resolved.open("rb") as handle:
                value = handle.read(LIMIT + 1)
        finally:
            # A supplied input is disposable, including on failure. Never pass a
            # LastPass export or the operator's original recovery-key file here.
            resolved.unlink()
    except SecretError:
        raise
    except OSError:
        raise SecretError("input_read_or_cleanup_failed") from None
    if not value or len(value) > LIMIT:
        raise SecretError("invalid_input_size")
    return value


def age_binary(root=ROOT):
    local = root / ".local" / "tools" / "age" / "age" / "age.exe"
    found = str(local) if os.name == "nt" and local.is_file() else shutil.which("age")
    if not found:
        raise SecretError("age_not_installed")
    return found


def run_age(arguments, value, root=ROOT):
    try:
        result = subprocess.run(
            [age_binary(root), *arguments], input=value,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=30, check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise SecretError("age_execution_failed") from None
    if result.returncode:
        raise SecretError("age_operation_failed")
    if not result.stdout or len(result.stdout) > LIMIT:
        raise SecretError("invalid_age_output")
    return result.stdout


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def parse_json(value):
    try:
        return json.loads(value, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError):
        raise SecretError("invalid_json") from None


class Store:
    def __init__(self, root=ROOT):
        self.root = root.resolve()

    def target(self, credential):
        try:
            catalog = parse_json((self.root / "secrets/catalog.json").read_bytes())
            if set(catalog) != {"version", "credentials"} or type(catalog["version"]) is not int or catalog["version"] != 1:
                raise SecretError("invalid_catalog")
            item = catalog["credentials"][credential]
            if set(item) != {"machine_id", "origin", "ciphertext"}:
                raise SecretError("invalid_catalog")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", credential):
                raise SecretError("invalid_catalog")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["machine_id"]):
                raise SecretError("invalid_catalog")
            url = urlsplit(item["origin"])
            if (url.scheme != "https" or not url.hostname or url.username or url.password
                    or url.port not in (None, 443) or url.path or url.query or url.fragment):
                raise SecretError("invalid_catalog")
            name = item["ciphertext"]
            if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*\.age", name):
                raise SecretError("invalid_catalog")
            path = self.root / "secrets" / name
            if path.is_symlink() or not path.resolve().is_relative_to(self.root / "secrets"):
                raise SecretError("unsafe_ciphertext_path")
            return item, path
        except (OSError, KeyError, TypeError, ValueError):
            raise SecretError("invalid_catalog_or_unknown_credential") from None

    def seal(self, credential, password_input, username, recipient, replace=False):
        item, path = self.target(credential)
        if path.exists() and not replace:
            raise SecretError("credential_already_exists")
        if not RECIPIENT.fullmatch(recipient):
            raise SecretError("invalid_public_recipient")
        try:
            password = password_input.decode("utf-8-sig")
        except UnicodeError:
            raise SecretError("invalid_password_input") from None
        # Preserve spaces exactly. Reject multiline paste mistakes; never trim.
        if not password or len(password_input) > 4096 or any(c in password for c in "\x00\r\n"):
            raise SecretError("invalid_password_input")
        if not re.fullmatch(r"[A-Za-z0-9_.@-]{1,128}", username):
            raise SecretError("invalid_username")
        payload = {
            "version": 1, "credential_id": credential, "machine_id": item["machine_id"],
            "origin": item["origin"], "username": username, "password": password,
        }
        encrypted = run_age(["--encrypt", "--armor", "--recipient", recipient],
                            json.dumps(payload).encode("utf-8"), self.root)
        # age has finished successfully before any credential file is written.
        if replace:
            import tempfile
            fd, temporary = tempfile.mkstemp(dir=path.parent, suffix=".age.tmp")
            try:
                with os.fdopen(fd, "wb") as output:
                    output.write(encrypted)
                os.replace(temporary, path)
            finally:
                Path(temporary).unlink(missing_ok=True)
        else:
            with path.open("xb") as output:
                output.write(encrypted)

    def decrypt(self, credential, identity_input):
        item, path = self.target(credential)
        if not path.is_file() or path.stat().st_size > LIMIT:
            raise SecretError("credential_missing_or_too_large")
        try:
            lines = [line.strip() for line in identity_input.decode("utf-8-sig").splitlines()
                     if line.strip() and not line.lstrip().startswith("#")]
        except UnicodeError:
            raise SecretError("invalid_identity_input") from None
        # Native identities only: no plugins, SSH keys, passphrases, or prompts.
        if len(lines) != 1 or not IDENTITY.fullmatch(lines[0]):
            raise SecretError("invalid_identity_input")
        key_input = (lines[0] + "\n").encode("ascii")
        plaintext = run_age(["--decrypt", "--identity", "-", str(path)], key_input, self.root)
        payload = parse_json(plaintext)
        expected = {"version", "credential_id", "machine_id", "origin", "username", "password"}
        if not isinstance(payload, dict) or set(payload) != expected:
            raise SecretError("invalid_credential_payload")
        if (type(payload["version"]) is not int or payload["version"] != 1
                or payload["credential_id"] != credential
                or payload["machine_id"] != item["machine_id"] or payload["origin"] != item["origin"]):
            raise SecretError("credential_binding_mismatch")
        if (not isinstance(payload["username"], str)
                or not re.fullmatch(r"[A-Za-z0-9_.@-]{1,128}", payload["username"])
                or not isinstance(payload["password"], str) or not payload["password"]
                or len(payload["password"].encode("utf-8")) > 4096
                or any(c in payload["password"] for c in "\x00\r\n")):
            raise SecretError("invalid_credential_payload")
        return payload


class KvmClient:
    """Fixed HTTPS operations; no proxies, redirects, debug logs, or token output."""

    def __init__(self, origin, ca_file=None):
        self.host = urlsplit(origin).hostname
        self.context = ssl.create_default_context(cafile=ca_file)

    def request(self, method, path, body=None, token=None):
        headers = {"User-Agent": "Nebula-credential-check/1"}
        if body is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if token:
            headers["Token"] = token
        connection = http.client.HTTPSConnection(self.host, 443, timeout=10, context=self.context)
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            raw = response.read(LIMIT + 1)
            if response.status == 429:
                raise SecretError("kvm_rate_limited")
            if 300 <= response.status < 400:
                raise SecretError("kvm_redirect_refused")
            if not 200 <= response.status < 300:
                raise SecretError("kvm_request_rejected")
            if len(raw) > LIMIT:
                raise SecretError("invalid_kvm_response")
            data = parse_json(raw)
            if not isinstance(data, dict) or data.get("ok") is not True or not isinstance(data.get("result"), dict):
                raise SecretError("invalid_kvm_response")
            return data["result"]
        except ssl.SSLCertVerificationError:
            raise SecretError("kvm_certificate_untrusted") from None
        except (OSError, http.client.HTTPException):
            raise SecretError("kvm_connection_failed") from None
        finally:
            connection.close()


def kvm_auth_check(payload, ca_file=None, client_factory=KvmClient):
    client = client_factory(payload["origin"], ca_file)
    result = client.request("POST", "/api/auth/login", urlencode({
        "user": payload["username"], "passwd": payload["password"], "expire": "60",
    }).encode("utf-8"))
    if result.get("two_step_required"):
        raise SecretError("kvm_operator_confirmation_required")
    token = result.get("token")
    if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,512}", token):
        raise SecretError("kvm_session_not_established")
    try:
        client.request("GET", "/api/auth/check", token=token)
    finally:
        # A failed logout is reported as a failure, never as clean success.
        try:
            client.request("POST", "/api/auth/logout", token=token)
        except Exception:
            raise SecretError("kvm_logout_unconfirmed") from None


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "seal", "verify", "kvm-auth-check"):
        command = commands.add_parser(name)
        command.add_argument("--credential", required=True)
        if name != "status":
            command.add_argument("--input-file", required=True, type=Path,
                                 help="DISPOSABLE private T3 input; consumed and deleted")
        if name == "seal":
            command.add_argument("--username", required=True)
            command.add_argument("--recipient", required=True, help="public age recipient")
            command.add_argument("--replace", action="store_true")
        if name == "kvm-auth-check":
            command.add_argument("--ca-file", type=Path, help="independently verified PEM CA certificate")
    args = parser.parse_args(argv)
    try:
        # Consume the private input even if later preflight/configuration fails.
        private = consume_input(args.input_file, root) if args.command != "status" else None
        store = Store(root)
        _, path = store.target(args.credential)
        if args.command == "status":
            state = "sealed" if path.is_file() else "not_enrolled"
        elif args.command == "seal":
            store.seal(args.credential, private, args.username, args.recipient, args.replace)
            state = "sealed"
        else:
            payload = store.decrypt(args.credential, private)
            state = "verified"
            if args.command == "kvm-auth-check":
                kvm_auth_check(payload, args.ca_file)
                state = "authenticated_and_logged_out"
        print(json.dumps({"ok": True, "credential": args.credential, "status": state}))
        return 0
    except SecretError as exc:
        code = str(exc) if str(exc) in ERROR_CODES else "operation_failed"
        print(json.dumps({"ok": False, "code": code}), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('{"ok":false,"code":"interrupted"}', file=sys.stderr)
        return 130
    except Exception:
        # Never include exception repr, subprocess stderr, device body, or locals.
        print('{"ok":false,"code":"operation_failed"}', file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
