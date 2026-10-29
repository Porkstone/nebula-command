"""Verify the bounded installer cannot run without explicit visual gating."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from dependabot_deploy import windows_command, windows_installer, FILES
import test_kvm_console


class DependabotDeployTests(unittest.TestCase):
    setUp = test_kvm_console.ConsoleTests.setUp
    command = test_kvm_console.ConsoleTests.command
    def test_install_is_disabled_without_explicit_session_option(self):
        frame = self.command("snapshot")
        with self.assertRaisesRegex(Exception, "console_command_rejected"):
            self.command("open-dependabot-installer", sha256=frame["sha256"], desktop_confirmed=True)

    def test_shell_and_desktop_confirmation_and_single_attempt(self):
        self.session.allow_dependabot_install = True
        frame = self.command("snapshot")
        with self.assertRaisesRegex(Exception, "console_command_rejected"):
            self.command("install-dependabot", sha256=frame["sha256"], shell_confirmed=True)
        with self.assertRaisesRegex(Exception, "console_command_rejected"):
            self.command("open-dependabot-installer", sha256=frame["sha256"])
        frame = self.command("open-dependabot-installer", sha256=frame["sha256"], desktop_confirmed=True)
        with self.assertRaisesRegex(Exception, "console_command_rejected"):
            self.command("install-dependabot", sha256=frame["sha256"])
        frame = self.command("install-dependabot", sha256=frame["sha256"], shell_confirmed=True)
        with self.assertRaisesRegex(Exception, "console_command_rejected"):
            self.command("install-dependabot", sha256=frame["sha256"], shell_confirmed=True)
        sent = [call[2] for call in self.calls if call[2] and '/api/hid/print?' in call[1]]
        self.assertEqual(b''.join(sent[1:]), windows_command().encode())
        self.assertTrue(all(len(chunk) <= 96 for chunk in sent))
        self.assertNotIn(self.windows["password"].encode(), sent)

    def test_command_checks_all_hashes_and_fixed_machine_account(self):
        text = windows_command()
        self.assertNotIn('\n', text)
        installer = windows_installer()
        self.assertIn("'win-srv-01'", installer)
        self.assertIn("'Administrator'", installer)
        for name, digest in FILES.items():
            self.assertIn(name, installer)
            self.assertIn(digest, installer)

    def test_failed_chunk_never_submits_enter_or_retries(self):
        self.session.allow_dependabot_install = True
        frame = self.command('snapshot')
        frame = self.command('open-dependabot-installer', sha256=frame['sha256'], desktop_confirmed=True)
        original = self.session.client.request
        before = len(self.calls)
        def fail(method, path, body=None, **kwargs):
            if body:
                raise RuntimeError('Ambiguous HID delivery')
            return original(method, path, body=body, **kwargs)
        self.session.client.request = fail
        with self.assertRaisesRegex(RuntimeError, 'Ambiguous HID delivery'):
            self.command('install-dependabot', sha256=frame['sha256'], shell_confirmed=True)
        self.assertFalse(any('key=Enter' in call[1] for call in self.calls[before:]))
        with self.assertRaisesRegex(Exception, 'console_command_rejected'):
            self.command('install-dependabot', sha256=frame['sha256'], shell_confirmed=True)


if __name__ == "__main__":
    unittest.main()
