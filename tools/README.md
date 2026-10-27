# Local tools

No tools here install software, enroll machines, change tailnet policy, or dispatch work remotely.

## Inventory CLI

Requires Python 3.11+ with no third-party packages. Paths default to this repository's live inventory even when run from another directory.

```sh
python tools/inventory.py validate
python tools/inventory.py validate --ready
python tools/inventory.py list
python tools/inventory.py --file inventory/examples/fleet.example.json validate --ready
```

Exit codes: 0 = valid/success, 1 = invalid inventory or incomplete ready check, 2 = file/JSON/argument error. `list` validates structure before displaying machine roles, enabled state, endpoints, and capacity. Output is descriptive; capacity is the configured ceiling, not a live reservation count.

`validate --ready` checks enabled records for required fields and commander selection. It does not contact machines, verify machine-detail files, inspect installed harnesses, or test authentication. See `inventory/README.md` for the contract.

## Windows hardware snapshot

```powershell
New-Item -ItemType Directory -Force .local | Out-Null
./tools/Get-LocalMachineInfo.ps1 | Set-Content -Encoding UTF8 .local/machine-snapshot.json
```

Requires Windows PowerShell 5.1+ and CIM access. Reads hostname, OS/version/architecture, CPU, RAM, GPU names, and fixed-disk size/free space. Prints JSON to stdout. Does not collect serial numbers, network peers, environment variables, credentials, or Tailscale state. Curate facts into a machine record and keep the raw snapshot ignored.

## Operator-supplied encrypted credentials

`fleet_secrets.py` seals privately submitted passwords and uses encrypted credentials with a fresh operator-supplied age key for each operation. T3 Code delivers the secret through a private temporary file; the helper consumes/deletes the submitted file and returns sanitized status only. Requires age in addition to Python. See [the operator workflow](../docs/runbooks/operator-secrets.md) for enrollment, exact T3 invocation, cleanup, and access limitations.

```sh
python tools/fleet_secrets.py status --credential win-srv-01-kvm
```

The live KVM credential has not been enrolled. The bounded KVM authentication adapter does login/check/logout; it does not provide browser or power control. This workflow does not isolate secrets from unrestricted processes under the same OS account.

## Extending tools

Use `adapters/README.md` for the future remote-execution contract. Provisioning, skill synchronization, health probes, and automated scheduling remain future work. Add platform-specific setup tools only when their target state and rollback behavior are known.
