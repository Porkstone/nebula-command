import hashlib
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import windows_ssh_setup
import test_kvm_console


class SshSetupTests(unittest.TestCase):
    setUp = test_kvm_console.ConsoleTests.setUp
    command = test_kvm_console.ConsoleTests.command

    def test_setup_requires_explicit_mode_and_matching_visual_gates(self):
        frame = self.command('snapshot')
        with self.assertRaisesRegex(Exception, 'console_command_rejected'):
            self.command('open-ssh-setup', sha256=frame['sha256'], desktop_confirmed=True)
        self.session.allow_ssh_setup = True
        with self.assertRaisesRegex(Exception, 'console_command_rejected'):
            self.command('open-ssh-setup', sha256=frame['sha256'])
        frame = self.command('open-ssh-setup', sha256=frame['sha256'], desktop_confirmed=True)
        self.session.allow_dependabot_install = True
        with self.assertRaisesRegex(Exception, 'console_command_rejected'):
            self.command('install-dependabot', sha256=frame['sha256'], shell_confirmed=True)
        before = len(self.calls)
        self.command('setup-ssh', sha256=frame['sha256'], shell_confirmed=True)
        sent = b''.join(c[2] for c in self.calls[before:] if c[2])
        self.assertEqual(sent, windows_ssh_setup.windows_command().encode())
        with self.assertRaisesRegex(Exception, 'console_command_rejected'):
            self.command('setup-ssh', sha256=frame['sha256'], shell_confirmed=True)

    def test_payload_is_pinned_and_scoped_without_private_key_material(self):
        script = windows_ssh_setup.installer()
        command = windows_ssh_setup.windows_command()
        self.assertIn(hashlib.sha256(script.encode()).hexdigest(), command)
        self.assertIn("-RemoteAddress '100.123.213.15'", script)
        self.assertIn("-LocalAddress '100.121.209.21'", script)
        self.assertIn('from="100.123.213.15",no-agent-forwarding,no-port-forwarding', script)
        self.assertIn('S-1-5-32-544', script)
        self.assertIn('S-1-5-18', script)
        self.assertNotIn('PRIVATE KEY', script)
        self.assertNotIn('Restart-Computer', script)


if __name__ == '__main__': unittest.main()
