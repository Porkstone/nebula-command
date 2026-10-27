#!/usr/bin/env python3
"""Inspect the curated Nebula inventory. Never connects to a machine."""

import argparse
import ipaddress
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys

DEFAULT_FILE = Path(__file__).resolve().parents[1] / "inventory" / "fleet.json"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
FIELDS = {
    "id", "role", "enabled", "os", "host", "ssh_user", "ssh_port",
    "transport", "workspace_root", "max_parallel_tasks", "capabilities", "harnesses",
}


def nonempty(value):
    return (isinstance(value, str) and bool(value.strip())
            and value == value.strip() and not any(ord(c) < 32 for c in value))


def valid_host(value):
    if not nonempty(value):
        return False
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return len(value) <= 253 and all(
            re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
            for label in value.rstrip(".").split(".")
        )


def validate(data, ready=False):
    """Return contract errors; an empty list means structurally valid."""
    errors = []
    if not isinstance(data, dict):
        return ["inventory must be an object"]
    if set(data) != {"version", "commander", "machines"}:
        errors.append("top-level keys must be exactly version, commander, machines")
    if type(data.get("version")) is not int or data["version"] != 1:
        errors.append("version must be integer 1")
    commander = data.get("commander")
    if commander is not None and (
        not isinstance(commander, str) or not SLUG.fullmatch(commander)
    ):
        errors.append("commander must be a machine ID or null")
    machines = data.get("machines")
    if not isinstance(machines, list):
        return errors + ["machines must be an array"]
    ids, hosts, leaders = set(), set(), []
    for index, machine in enumerate(machines):
        prefix = f"machines[{index}]"
        if not isinstance(machine, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if set(machine) != FIELDS:
            missing = sorted(FIELDS - set(machine))
            unknown = sorted(set(machine) - FIELDS)
            errors.append(f"{prefix}: missing keys {missing}; unknown keys {unknown}")
        machine_id = machine.get("id")
        if not isinstance(machine_id, str) or not SLUG.fullmatch(machine_id):
            errors.append(f"{prefix}.id must be a lowercase slug")
        elif machine_id in ids:
            errors.append(f"{prefix}: duplicate id {machine_id}")
        else:
            ids.add(machine_id)
        for field, choices in (
            ("role", ("commander", "worker")),
            ("os", ("windows", "linux", "macos")),
            ("transport", ("openssh", "tailscale-ssh")),
        ):
            if machine.get(field) not in choices:
                errors.append(f"{prefix}.{field} must be one of {choices}")
        if machine.get("role") == "commander":
            leaders.append(machine)
        if type(machine.get("enabled")) is not bool:
            errors.append(f"{prefix}.enabled must be boolean")
        for field, minimum, maximum in (
            ("ssh_port", 1, 65535), ("max_parallel_tasks", 0, None),
        ):
            value = machine.get(field)
            if type(value) is not int or value < minimum or (
                maximum is not None and value > maximum
            ):
                errors.append(f"{prefix}.{field} has an invalid integer value")
        host = machine.get("host")
        if host is not None:
            if not valid_host(host):
                errors.append(f"{prefix}.host must be a bare hostname/IP or null")
            elif host.rstrip(".").lower() in hosts:
                errors.append(f"{prefix}: duplicate host {host}")
            else:
                hosts.add(host.rstrip(".").lower())
        user = machine.get("ssh_user")
        if user is not None and (
            not nonempty(user) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.@\\$-]*", user)
        ):
            errors.append(f"{prefix}.ssh_user must be an account name or null")
        root = machine.get("workspace_root")
        if root is not None:
            path_type = PureWindowsPath if machine.get("os") == "windows" else PurePosixPath
            if not nonempty(root) or not path_type(root).is_absolute():
                errors.append(f"{prefix}.workspace_root must be absolute for its OS or null")
        for field in ("capabilities", "harnesses"):
            values = machine.get(field)
            if not isinstance(values, list) or not all(nonempty(v) for v in values):
                errors.append(f"{prefix}.{field} must be an array of nonempty strings")
            elif len(set(values)) != len(values):
                errors.append(f"{prefix}.{field} must contain unique strings")
        if machine.get("transport") == "tailscale-ssh":
            if machine.get("os") == "windows":
                errors.append(f"{prefix}: Windows cannot serve Tailscale SSH")
            if machine.get("ssh_port") != 22:
                errors.append(f"{prefix}: Tailscale SSH requires port 22")
        if ready and machine.get("enabled") is True:
            for field in ("host", "ssh_user", "workspace_root"):
                if not machine.get(field):
                    errors.append(f"{prefix}.{field} is required for enabled machines")
            capacity = machine.get("max_parallel_tasks")
            if type(capacity) is int and capacity == 0:
                errors.append(f"{prefix}: enabled machine needs positive capacity for --ready")
            if not machine.get("harnesses"):
                errors.append(f"{prefix}: enabled machine needs at least one harness")
    if commander is None:
        if leaders:
            errors.append("commander is null but a machine has the commander role")
        if ready:
            errors.append("select an enabled commander before activation")
    elif len(leaders) != 1 or leaders[0].get("id") != commander:
        errors.append("commander must select the single machine with the commander role")
    elif ready and leaders[0].get("enabled") is not True:
        errors.append("selected commander must be enabled")
    return errors


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("validate", help="check inventory structure")
    check.add_argument("--ready", action="store_true", help="check activation fields too")
    commands.add_parser("list", help="list configured machines; no network probes")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.file.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)
    except (OSError, ValueError) as exc:
        print(f"Cannot read inventory: {exc}", file=sys.stderr)
        return 2
    errors = validate(data, ready=getattr(args, "ready", False))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.command == "validate":
        mode = "activation fields" if args.ready else "structure"
        print(f"Valid inventory ({mode}): {len(data['machines'])} machine(s). No hosts probed.")
    elif not data["machines"]:
        print("No machines registered. Commander: unassigned.")
    else:
        print("ID\tROLE\tENABLED\tOS\tHOST\tCAPACITY")
        for machine in data["machines"]:
            print("\t".join(str(machine[key]) for key in (
                "id", "role", "enabled", "os", "host", "max_parallel_tasks",
            )))
    return 0


if __name__ == "__main__":
    sys.exit(main())
