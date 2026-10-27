"""Exercise commander selection, staged records, and activation rejection."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("inventory_tool", ROOT / "tools" / "inventory.py")
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.fleet = json.loads((ROOT / "inventory/examples/fleet.example.json").read_text())

    def test_empty_scaffold_is_valid_but_cannot_activate(self):
        fleet = {"version": 1, "commander": None, "machines": []}
        self.assertEqual(inventory.validate(fleet), [])
        self.assertTrue(inventory.validate(fleet, ready=True))

    def test_example_can_activate_with_staged_worker(self):
        worker = self.fleet["machines"][1]
        worker.update(host=None, ssh_user=None, workspace_root=None, harnesses=[])
        self.assertEqual(inventory.validate(self.fleet, ready=True), [])

    def test_enabled_worker_needs_activation_fields(self):
        self.fleet["machines"][1].update(enabled=True, host=None)
        self.assertTrue(inventory.validate(self.fleet, ready=True))

    def test_commander_selection_must_match_single_role(self):
        for commander, role in (("missing", "worker"), (None, "commander"), ("worker-01", "commander")):
            with self.subTest(commander=commander, role=role):
                fleet = copy.deepcopy(self.fleet)
                fleet["commander"] = commander
                fleet["machines"][1]["role"] = role
                self.assertTrue(inventory.validate(fleet))

    def test_disabled_commander_cannot_activate(self):
        self.fleet["machines"][0]["enabled"] = False
        self.assertEqual(inventory.validate(self.fleet), [])
        self.assertTrue(inventory.validate(self.fleet, ready=True))

    def test_duplicate_ids_and_case_insensitive_hosts_are_rejected(self):
        for field in ("id", "host"):
            with self.subTest(field=field):
                fleet = copy.deepcopy(self.fleet)
                value = fleet["machines"][0][field]
                fleet["machines"][1][field] = value.upper() + "." if field == "host" else value
                self.assertTrue(inventory.validate(fleet))

    def test_paths_follow_execution_os(self):
        for index, path in ((0, "/srv/work"), (1, "C:\\work"), (1, "relative/work")):
            with self.subTest(index=index, path=path):
                fleet = copy.deepcopy(self.fleet)
                fleet["machines"][index]["workspace_root"] = path
                self.assertTrue(inventory.validate(fleet))

    def test_unsupported_ssh_transport_is_rejected(self):
        self.fleet["machines"][0]["transport"] = "tailscale-ssh"
        self.assertTrue(inventory.validate(self.fleet))
        self.fleet["machines"][0]["os"] = "linux"
        self.fleet["machines"][0]["workspace_root"] = "/srv/work"
        self.assertEqual(inventory.validate(self.fleet), [])
        self.fleet["machines"][0]["ssh_port"] = 2222
        self.assertTrue(inventory.validate(self.fleet))

    def test_bad_types_missing_and_unknown_fields_are_rejected_without_crashing(self):
        for field, value in (("max_parallel_tasks", True), ("ssh_port", 65536),
                             ("enabled", "false"), ("capabilities", [{}]),
                             ("host", "ssh://somewhere"), ("os", "unknown"),
                             ("id", []), ("ssh_user", "name;command")):
            with self.subTest(field=field):
                fleet = copy.deepcopy(self.fleet)
                fleet["machines"][0][field] = value
                self.assertTrue(inventory.validate(fleet))
        self.fleet["machines"][0]["enabld"] = True
        del self.fleet["machines"][0]["enabled"]
        self.assertTrue(inventory.validate(self.fleet))
        for value in (None, [], {"machines": [None]}, {"machines": {}}):
            self.assertTrue(inventory.validate(value))

    def test_cli_reports_distinct_failure_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "fleet.json"
            for content, expected in (("not json", 2), ('{"version":1,"version":1}', 2), ("{}", 1)):
                target.write_text(content)
                result = subprocess.run(
                    [sys.executable, str(ROOT / "tools/inventory.py"), "--file", str(target), "validate"],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_default_inventory_path_does_not_depend_on_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/inventory.py"), "list"],
                cwd=directory, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            live = json.loads((ROOT / "inventory/fleet.json").read_text())
            for machine in live["machines"]:
                self.assertIn(machine["id"], result.stdout)
            if not live["machines"]:
                self.assertIn("No machines registered", result.stdout)


if __name__ == "__main__":
    unittest.main()
