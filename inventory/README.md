# Machine inventory

`fleet.json` is the live inventory. `examples/fleet.example.json` contains fictional machines and must never be used as a dispatch target list.

## Registered machines

- [Macbotic](machines/macbotic.md): selected commander; macOS, SSH, workspace, commander skills, and local Codex execution verified; enabled with one local task slot.
- [Trigbotic](machines/trigbotic.md): worker; Windows 11 Pro confirmed locally.
- [win-srv-01](machines/win-srv-01.md): worker; Windows Server 2025 Standard Evaluation observed through the KVM; Windows console sign-in verified.
- [ubuntu-srv1](machines/ubuntu-srv1.md): worker; Ubuntu reported by the operator.

Macbotic is the selected commander, enabled for local work with capacity 1. Tailscale endpoints for all four machines are stored in `fleet.json`. Trigbotic is enabled with capacity 1 after an isolated T3/Codex task/result round trip on 2026-11-09; current reservations are recorded in `operations/tasks/`. Its proposal-document-pack PR merged on 2026-11-10 and that reservation was reconciled and released before the next assignment. Assign Trigbotic through its verified T3 service, not SSH: incoming SSH from Macbotic remains unverified. The two server workers remain staged with assignment disabled and capacity 0. Macbotic's GitHub CLI authentication and remaining worker access still need configuration; see its machine record. OpenSSH/port 22 are inventory defaults; service verification and any selected harness interface are recorded per machine.

Create a detail record at `machines/<id>.md` from [the machine template](../templates/machine.md). Keep routing values in `fleet.json` and detailed hardware/configuration evidence in the record. Review the diff before enabling a machine.

## Version 1 contract

Top-level keys are `version` (integer `1`), `commander` (machine ID or `null`), and `machines` (array). Unknown keys are rejected to catch misspellings.

| Machine field | Meaning |
| --- | --- |
| `id` | Unique lowercase slug, e.g. `worker-01` |
| `role` | `commander` or `worker` |
| `enabled` | Whether this machine may receive work; boolean |
| `os` | `windows`, `linux`, or `macos`; refers to the execution environment |
| `host` | Unique SSH hostname or IP, without a user, port, or URL; `null` until known |
| `ssh_user` | Login account; `null` until known |
| `ssh_port` | Integer 1–65535; Tailscale SSH uses 22 |
| `transport` | `openssh` or `tailscale-ssh` |
| `workspace_root` | Absolute path in the execution environment; `null` until known |
| `max_parallel_tasks` | Nonnegative integer; 0 temporarily prevents assignment |
| `capabilities` | Unique strings used for task routing |
| `harnesses` | Unique identifiers for installed/configured harnesses |

All machine fields are required, even when nullable. With no selected commander, no machine may have the commander role. With a selected commander, exactly one machine must have that role and its ID must match. The commander can be disabled while the fleet is staged, but `--ready` rejects that state.

Normal validation permits an empty inventory and incomplete staged records. `--ready` additionally requires a selected enabled commander and complete host, account, workspace, positive capacity, and at least one harness for every enabled machine. A Windows environment cannot use Tailscale SSH as its server transport. WSL is a separate Linux execution target; document its network endpoint and service lifecycle explicitly.

Validation is structural. It does not confirm hostname resolution, SSH identity, installations, permissions, capacity, or recent health. Record those checks in each machine's verification history before real dispatch.
