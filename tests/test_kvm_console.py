"""No live HID actions: verify bounded console commands with a fake device."""

from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import kvm_console as console


JPEG = (b"\xff\xd8\xff\xc0\x00\x11\x08" + struct.pack(">HH", 1080, 1920)
        + b"\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00\xff\xd9")


class ConsoleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.calls = []
        self.now = [0.0]
        self.kvm = {"machine_id": "win-srv-01", "origin": "https://100.126.31.7",
                    "username": "admin", "password": "dummy-kvm-only"}
        self.windows = {"kind": "windows-console", "machine_id": "win-srv-01",
                        "origin": "console://win-srv-01", "username": "Administrator",
                        "password": "dummy-windows-only"}
        calls = self.calls

        class Client:
            def request(self, method, path, body=None, token=None, **kwargs):
                calls.append((method, path, body, token, kwargs))
                if path.endswith("login"):
                    return {"token": "a" * 64}
                if kwargs.get("response_type") == "jpeg":
                    return JPEG
                return {}

        self.factory = lambda *args: Client()
        self.session = console.ConsoleSession(self.kvm.copy(), self.windows.copy(), "a" * 64,
                                               Path(self.temporary.name) / "session",
                                               client_factory=self.factory, clock=lambda: self.now[0],
                                               pause=lambda seconds: self.now.__setitem__(0, self.now[0] + seconds))
        self.session.login()

    def command(self, operation, **kwargs):
        return self.session.command({"operation": operation, **kwargs})

    def test_snapshot_dimensions_and_status_do_not_contain_credentials(self):
        frame = self.command("snapshot")
        self.assertEqual((frame["width"], frame["height"]), (1920, 1080))
        self.assertNotIn(self.windows["password"], str(frame))
        self.assertNotIn(self.kvm["password"], str(frame))
        self.assertTrue(Path(frame["path"]).is_file())

    def test_machine_binding_and_verified_pin_are_required(self):
        for machine, pin in (("other-machine", "a" * 64), ("win-srv-01", None)):
            windows = self.windows.copy()
            windows["machine_id"] = machine
            with self.assertRaisesRegex(console.SecretError, "console_binding_mismatch"):
                console.ConsoleSession(self.kvm, windows, pin, Path(self.temporary.name) / "rejected")

    def test_password_is_not_sent_without_recent_confirmed_snapshot(self):
        with self.assertRaisesRegex(console.SecretError, "console_snapshot_required"):
            self.command("submit-password", x=400, y=500, field_confirmed=True)
        frame = self.command("snapshot")
        with self.assertRaisesRegex(console.SecretError, "console_command_rejected"):
            self.command("submit-password", x=400, y=500, sha256=frame["sha256"])
        self.now[0] += 61
        with self.assertRaisesRegex(console.SecretError, "console_snapshot_required"):
            self.command("submit-password", x=400, y=500, sha256=frame["sha256"], field_confirmed=True)
        self.assertFalse(any(call[2] == self.windows["password"].encode() for call in self.calls))

    def test_one_password_submission_with_no_secret_query_or_output(self):
        frame = self.command("snapshot")
        result = self.command("submit-password", x=900, y=520, sha256=frame["sha256"], field_confirmed=True)
        password_calls = [call for call in self.calls if call[2] == self.windows["password"].encode()]
        self.assertEqual(len(password_calls), 1)
        self.assertTrue(password_calls[0][1].startswith("/api/hid/print?"))
        self.assertNotIn(self.windows["password"], password_calls[0][1])
        self.assertNotIn(self.windows["password"], str(result))
        with self.assertRaisesRegex(console.SecretError, "console_attempt_already_used"):
            self.command("submit-password", x=900, y=520, sha256=result["sha256"], field_confirmed=True)
        self.command("snapshot")  # Observation remains available after submission.

    def test_arbitrary_text_commands_and_out_of_frame_clicks_are_rejected(self):
        frame = self.command("snapshot")
        for command in ({"operation": "type", "text": "arbitrary"},
                        {"operation": "key", "key": "KeyR"},
                        {"operation": "click", "sha256": frame["sha256"], "x": 1920, "y": 0}):
            with self.assertRaisesRegex(console.SecretError, "console_command_rejected"):
                self.session.command(command)

    def test_unlock_releases_every_modifier(self):
        self.command("unlock")
        paths = [call[1] for call in self.calls if "send_key?" in call[1]]
        self.assertEqual(len(paths), 6)
        self.assertIn("key=ControlLeft&state=1", paths[0])
        self.assertIn("key=ControlLeft&state=0", paths[-1])

    def test_ambiguous_key_down_still_attempts_release(self):
        original = self.session.client.request

        def request(method, path, **kwargs):
            if "key=Enter&state=1" in path:
                self.calls.append((method, path, None, None, {}))
                raise console.SecretError("kvm_connection_failed")
            return original(method, path, **kwargs)

        self.session.client.request = request
        with self.assertRaisesRegex(console.SecretError, "kvm_connection_failed"):
            self.session.key("Enter")
        self.assertTrue(any("key=Enter&state=0" in call[1] for call in self.calls))

    def test_session_expiry_blocks_commands_and_logout_drops_secrets(self):
        self.now[0] = 601
        with self.assertRaisesRegex(console.SecretError, "console_session_expired"):
            self.command("snapshot")
        self.session.close()
        self.assertEqual(self.calls[-1][1], "/api/auth/logout")
        self.assertIsNone(self.session.windows)
        self.assertIsNone(self.session.token)

    def test_bad_snapshot_is_rejected(self):
        for image in (b"not-jpeg", b"\xff\xd8\xff", b"\xff\xd8\xff\xc0\x00\x00"):
            with self.subTest(image=image):
                with self.assertRaisesRegex(console.SecretError, "invalid_snapshot"):
                    console.jpeg_size(image)


if __name__ == "__main__":
    unittest.main()
