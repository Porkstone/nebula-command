"""Real age round trips plus credential-boundary and redaction checks."""

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fleet_secrets", ROOT / "tools/fleet_secrets.py")
secrets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(secrets)


class SecretTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.age = secrets.age_binary()
        except secrets.SecretError:
            raise unittest.SkipTest("Install age to run encryption integration tests")
        keygen = Path(cls.age).with_name("age-keygen.exe" if Path(cls.age).suffix == ".exe" else "age-keygen")
        cls.key = subprocess.run([str(keygen)], capture_output=True, check=True).stdout
        cls.wrong_key = subprocess.run([str(keygen)], capture_output=True, check=True).stdout
        cls.recipient = subprocess.run([str(keygen), "-y"], input=cls.key, capture_output=True, check=True).stdout.decode().strip()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "repo"
        (self.root / "secrets").mkdir(parents=True)
        self.catalog_path = self.root / "secrets/catalog.json"
        self.catalog_path.write_bytes((ROOT / "secrets/catalog.json").read_bytes())
        self.age_patch = patch.object(secrets, "age_binary", return_value=self.age)
        self.age_patch.start()
        self.addCleanup(self.age_patch.stop)
        self.store = secrets.Store(self.root)
        self.credential = "win-srv-01-kvm"
        self.password = " test-only-not-a-real-KVM-password! "

    def call(self, command, private=None, extra=()):
        arguments = [command, "--credential", self.credential, *extra]
        self.input_path = self.base / "private-input"
        if private is not None:
            self.input_path.write_bytes(private)
            arguments.extend(["--input-file", str(self.input_path)])
        output, error = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            code = secrets.main(arguments, root=self.root)
        text = output.getvalue() + error.getvalue()
        self.assertNotIn(self.password, text)
        self.assertNotIn("AGE-SECRET-KEY-", text)
        self.assertNotIn("Traceback", text)
        return code, text

    def seal(self, extra=()):
        code, output = self.call("seal", self.password.encode(),
                                 ("--username", "admin", "--recipient", self.recipient, *extra))
        self.assertEqual(code, 0, output)
        self.assertFalse(self.input_path.exists())
        return self.store.target(self.credential)[1]

    def test_real_age_roundtrip_keeps_output_and_disk_free_of_plaintext(self):
        ciphertext = self.seal()
        self.assertNotIn(self.password.encode(), ciphertext.read_bytes())
        code, output = self.call("verify", self.key)
        self.assertEqual(code, 0, output)
        self.assertEqual(json.loads(output)["status"], "verified")
        self.assertFalse(self.input_path.exists())
        payload = self.store.decrypt(self.credential, self.key)
        self.assertEqual(payload["password"], self.password)  # Spaces preserved.
        self.assertEqual({p.name for p in (self.root / "secrets").iterdir()},
                         {"catalog.json", "win-srv-01-kvm.json.age"})

    def test_incorrect_key_is_consumed_and_error_is_redacted(self):
        self.seal()
        code, output = self.call("verify", self.wrong_key)
        self.assertEqual(code, 1)
        self.assertIn("age_operation_failed", output)
        self.assertFalse(self.input_path.exists())

    def test_tampered_ciphertext_is_rejected(self):
        ciphertext = self.seal()
        ciphertext.write_bytes(ciphertext.read_bytes()[:100])
        code, output = self.call("verify", self.key)
        self.assertEqual(code, 1)
        self.assertIn("age_operation_failed", output)
        self.assertFalse(self.input_path.exists())

    def test_ciphertext_is_bound_to_original_origin(self):
        self.seal()
        catalog = json.loads(self.catalog_path.read_text())
        catalog["credentials"][self.credential]["origin"] = "https://100.100.100.100"
        self.catalog_path.write_text(json.dumps(catalog))
        code, output = self.call("verify", self.key)
        self.assertEqual(code, 1)
        self.assertIn("credential_binding_mismatch", output)

    def test_encrypted_malformed_payload_is_not_reported_as_verified(self):
        _, ciphertext = self.store.target(self.credential)
        encrypted = secrets.run_age(["--encrypt", "--armor", "--recipient", self.recipient], b'{"password":"test"}')
        ciphertext.write_bytes(encrypted)
        code, output = self.call("verify", self.key)
        self.assertEqual(code, 1)
        self.assertIn("invalid_credential_payload", output)

    def test_overwrite_requires_explicit_replace_and_consumes_input(self):
        path = self.seal()
        original = path.read_bytes()
        code, output = self.call("seal", b"another-test-password", ("--username", "admin", "--recipient", self.recipient))
        self.assertEqual(code, 1)
        self.assertIn("credential_already_exists", output)
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(self.input_path.exists())
        self.seal(("--replace",))
        self.assertEqual(self.store.decrypt(self.credential, self.key)["password"], self.password)

    def test_input_inside_repository_is_rejected_without_deleting_it(self):
        path = self.root / "mistaken-input"
        path.write_bytes(b"test-only")
        with self.assertRaisesRegex(secrets.SecretError, "unsafe_input_file"):
            secrets.consume_input(path, self.root)
        self.assertTrue(path.is_file())

    def test_missing_dependency_still_consumes_submitted_input(self):
        with patch.object(secrets, "age_binary", side_effect=secrets.SecretError("age_not_installed")):
            code, output = self.call("seal", self.password.encode(), ("--username", "admin", "--recipient", self.recipient))
        self.assertEqual(code, 1)
        self.assertIn("age_not_installed", output)
        self.assertFalse(self.input_path.exists())

    def test_plugin_identity_is_rejected_before_any_subprocess(self):
        self.seal()
        with patch.object(secrets, "run_age") as run:
            code, output = self.call("verify", b"AGE-PLUGIN-UNTRUSTED-1EXAMPLE")
        self.assertEqual(code, 1)
        self.assertIn("invalid_identity_input", output)
        run.assert_not_called()
        self.assertFalse(self.input_path.exists())

    def test_plugin_recipient_is_rejected_before_any_subprocess(self):
        with patch.object(secrets, "run_age") as run:
            code, output = self.call("seal", self.password.encode(),
                                     ("--username", "admin", "--recipient", "age1yubikey1untrusted"))
        self.assertEqual(code, 1)
        self.assertIn("invalid_public_recipient", output)
        run.assert_not_called()
        self.assertFalse(self.input_path.exists())

    def test_oversized_input_is_deleted_and_rejected(self):
        code, output = self.call("verify", b"x" * (secrets.LIMIT + 1))
        self.assertEqual(code, 1)
        self.assertIn("invalid_input_size", output)
        self.assertFalse(self.input_path.exists())

    def test_unexpected_exception_never_emits_secret_details(self):
        self.seal()
        with patch.object(secrets.Store, "decrypt", side_effect=RuntimeError(self.password)):
            code, output = self.call("verify", self.key)
        self.assertEqual(code, 1)
        self.assertIn("operation_failed", output)
        self.assertFalse(self.input_path.exists())

    def test_unknown_error_code_cannot_be_used_to_emit_a_secret(self):
        self.seal()
        with patch.object(secrets.Store, "decrypt", side_effect=secrets.SecretError(self.password)):
            code, output = self.call("verify", self.key)
        self.assertEqual(code, 1)
        self.assertIn("operation_failed", output)

    def test_child_timeout_with_secret_output_is_redacted(self):
        self.seal()
        with patch.object(secrets.subprocess, "run", side_effect=subprocess.TimeoutExpired(
            "age", 30, output=self.password.encode(), stderr=self.key,
        )):
            code, output = self.call("verify", self.key)
        self.assertEqual(code, 1)
        self.assertIn("age_execution_failed", output)

    def test_unsafe_catalog_destinations_and_paths_are_rejected(self):
        for field, value in (("origin", "http://100.126.31.7"),
                             ("origin", "https://100.126.31.7/elsewhere"),
                             ("origin", "https://user@100.126.31.7"),
                             ("ciphertext", "../outside.age")):
            with self.subTest(field=field, value=value):
                catalog = json.loads((ROOT / "secrets/catalog.json").read_text())
                catalog["credentials"][self.credential][field] = value
                self.catalog_path.write_text(json.dumps(catalog))
                with self.assertRaises(secrets.SecretError):
                    self.store.target(self.credential)

    def test_status_needs_no_key_and_sealing_does_not_claim_authentication(self):
        code, output = self.call("status")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["status"], "not_enrolled")
        self.seal()
        _, output = self.call("status")
        self.assertEqual(json.loads(output)["status"], "sealed")

    def test_cli_auth_check_returns_no_session_or_password(self):
        self.seal()
        with patch.object(secrets, "kvm_auth_check") as check:
            code, output = self.call("kvm-auth-check", self.key)
        check.assert_called_once()
        self.assertEqual(code, 0, output)
        self.assertEqual(json.loads(output)["status"], "authenticated_and_logged_out")
        self.assertFalse(self.input_path.exists())

    def test_windows_console_accounts_roundtrip_with_scope_and_unicode(self):
        self.credential = "win-srv-01-console"
        for username in ("Administrator", r".\Administrator", r"WIN-SRV-01\Administrator",
                         r"DOMAIN\agent", "agent@example.com", "Local User", "Élodie"):
            with self.subTest(username=username):
                code, output = self.call("seal", self.password.encode(),
                                         ("--username", username, "--recipient", self.recipient, "--replace"))
                self.assertEqual(code, 0, output)
                self.assertFalse(self.input_path.exists())
                payload = self.store.decrypt(self.credential, self.key)
                self.assertEqual(payload["kind"], "windows-console")
                self.assertEqual(payload["username"], username)
                self.assertEqual(payload["origin"], "console://win-srv-01")
                self.assertEqual(payload["password"], self.password)

    def test_console_password_cannot_be_sent_to_kvm_login(self):
        self.credential = "win-srv-01-console"
        with patch.object(secrets, "kvm_auth_check") as check:
            code, output = self.call("kvm-auth-check", self.key)
        self.assertEqual(code, 1)
        self.assertIn("credential_action_not_supported", output)
        self.assertFalse(self.input_path.exists())
        check.assert_not_called()

    def test_existing_version_one_kvm_ciphertext_remains_readable(self):
        target, path = self.store.target(self.credential)
        payload = {"version": 1, "credential_id": self.credential,
                   "machine_id": target["machine_id"], "origin": target["origin"],
                   "username": "admin", "password": self.password}
        path.write_bytes(secrets.run_age(["--encrypt", "--armor", "--recipient", self.recipient],
                                        json.dumps(payload).encode()))
        self.assertEqual(self.store.decrypt(self.credential, self.key)["password"], self.password)

    def test_encrypted_credential_kind_mismatch_is_rejected(self):
        path = self.seal()
        payload = self.store.decrypt(self.credential, self.key)
        payload["kind"] = "windows-console"
        path.write_bytes(secrets.run_age(["--encrypt", "--armor", "--recipient", self.recipient],
                                        json.dumps(payload).encode()))
        code, output = self.call("verify", self.key)
        self.assertEqual(code, 1)
        self.assertIn("credential_binding_mismatch", output)

    def test_console_catalog_cannot_route_password_to_http_endpoint(self):
        catalog = json.loads(self.catalog_path.read_text())
        catalog["credentials"]["win-srv-01-console"]["origin"] = "https://100.126.31.7"
        self.catalog_path.write_text(json.dumps(catalog))
        with self.assertRaises(secrets.SecretError):
            self.store.target("win-srv-01-console")

    def test_windows_username_rejects_control_characters_and_malformed_scope(self):
        for username in ("", "Administrator\n", " User", "User ", "\\User", "DOMAIN\\", "A\\B\\C"):
            with self.subTest(username=username):
                self.assertFalse(secrets.valid_username(username, "windows-console"))


class KvmTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"origin": "https://100.126.31.7", "username": "admin", "password": "dummy-for-tests"}
        self.calls = []

    def factory(self, failure=None, two_step=False):
        calls = self.calls

        class Client:
            def request(self, method, path, body=None, token=None):
                calls.append((method, path, body, token))
                if path == failure:
                    raise secrets.SecretError("test_request_failed")
                if path.endswith("login"):
                    return {"two_step_required": True} if two_step else {"token": "a" * 64}
                return {}

        return lambda origin, ca_file, tls_pin_sha256=None: Client()

    def test_login_check_logout_is_bounded_and_has_short_expiry(self):
        secrets.kvm_auth_check(self.payload, client_factory=self.factory())
        self.assertEqual([call[1] for call in self.calls], ["/api/auth/login", "/api/auth/check", "/api/auth/logout"])
        form = parse_qs(self.calls[0][2].decode())
        self.assertEqual(form["passwd"], [self.payload["password"]])
        self.assertEqual(form["expire"], ["60"])
        self.assertEqual(self.calls[1][3], "a" * 64)

    def test_library_auth_check_rejects_windows_credentials_before_connecting(self):
        self.payload["kind"] = "windows-console"
        with self.assertRaisesRegex(secrets.SecretError, "credential_action_not_supported"):
            secrets.kvm_auth_check(self.payload, client_factory=self.factory())
        self.assertEqual(self.calls, [])

    def test_logout_is_attempted_after_auth_check_failure(self):
        with self.assertRaisesRegex(secrets.SecretError, "test_request_failed"):
            secrets.kvm_auth_check(self.payload, client_factory=self.factory(failure="/api/auth/check"))
        self.assertEqual(self.calls[-1][1], "/api/auth/logout")

    def test_failed_logout_does_not_claim_clean_success(self):
        with self.assertRaisesRegex(secrets.SecretError, "kvm_logout_unconfirmed"):
            secrets.kvm_auth_check(self.payload, client_factory=self.factory(failure="/api/auth/logout"))

    def test_two_step_authentication_is_reported_without_retries(self):
        with self.assertRaisesRegex(secrets.SecretError, "kvm_operator_confirmation_required"):
            secrets.kvm_auth_check(self.payload, client_factory=self.factory(two_step=True))
        self.assertEqual(len(self.calls), 1)

    def test_redirect_is_not_followed_and_response_body_is_not_exposed(self):
        from unittest.mock import Mock
        response = Mock(status=302)
        response.read.return_value = b"dummy-secret-response"
        connection = Mock()
        connection.getresponse.return_value = response
        with patch.object(secrets.http.client, "HTTPSConnection", return_value=connection):
            client = secrets.KvmClient(self.payload["origin"])
            with self.assertRaisesRegex(secrets.SecretError, "kvm_redirect_refused"):
                client.request("POST", "/api/auth/login", body=b"dummy")
        self.assertEqual(connection.request.call_count, 1)
        connection.close.assert_called_once()

    def test_tls_verification_failure_is_redacted(self):
        from unittest.mock import Mock
        connection = Mock()
        connection.request.side_effect = secrets.ssl.SSLCertVerificationError("dummy-secret-detail")
        with patch.object(secrets.http.client, "HTTPSConnection", return_value=connection):
            with self.assertRaisesRegex(secrets.SecretError, "kvm_certificate_untrusted"):
                secrets.KvmClient(self.payload["origin"]).request("POST", "/api/auth/login")

    def test_changed_pinned_certificate_prevents_all_http_credential_transmission(self):
        from unittest.mock import Mock
        connection = Mock()
        connection.sock.getpeercert.return_value = b"different-test-certificate"
        with patch.object(secrets.http.client, "HTTPSConnection", return_value=connection):
            client = secrets.KvmClient(self.payload["origin"], tls_pin_sha256="a" * 64)
            with self.assertRaisesRegex(secrets.SecretError, "kvm_certificate_pin_mismatch"):
                client.request("POST", "/api/auth/login", body=b"dummy-private-password")
        connection.connect.assert_called_once()
        connection.request.assert_not_called()
        connection.close.assert_called_once()

    def test_matching_pin_is_verified_before_http_request(self):
        from unittest.mock import Mock
        certificate = b"exact-test-device-certificate"
        pin = secrets.hashlib.sha256(certificate).hexdigest()
        events = []
        connection = Mock()
        connection.connect.side_effect = lambda: events.append("connect")
        connection.sock.getpeercert.side_effect = lambda **kwargs: (events.append("certificate") or certificate)
        connection.request.side_effect = lambda *args, **kwargs: events.append("request")
        response = Mock(status=200)
        response.read.return_value = b'{"ok":true,"result":{}}'
        connection.getresponse.return_value = response
        with patch.object(secrets.http.client, "HTTPSConnection", return_value=connection):
            secrets.KvmClient(self.payload["origin"], tls_pin_sha256=pin).request("GET", "/api/auth/check")
        self.assertEqual(events, ["connect", "certificate", "request"])

    def test_default_tls_keeps_chain_and_hostname_verification_enabled(self):
        client = secrets.KvmClient(self.payload["origin"])
        self.assertTrue(client.context.check_hostname)
        self.assertEqual(client.context.verify_mode, secrets.ssl.CERT_REQUIRED)

    def test_invalid_or_conflicting_pinning_configuration_is_rejected(self):
        for pin, ca_file in (("bad-pin", None), ("a" * 64, "some-ca.pem")):
            with self.subTest(pin=pin, ca_file=ca_file):
                with self.assertRaisesRegex(secrets.SecretError, "invalid_tls_configuration"):
                    secrets.KvmClient(self.payload["origin"], ca_file, pin)


if __name__ == "__main__":
    unittest.main()
