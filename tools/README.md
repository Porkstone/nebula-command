# Local tools

These tools do not enroll machines, change tailnet policy, or dispatch managed agent work remotely. Explicitly requested bounded KVM operations can deploy Dependabot or bootstrap OpenSSH on win-srv-01.

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

The KVM credential is enrolled with an operator-approved exact certificate pin. The bounded KVM authentication adapter does login/check/logout. Each use requires a fresh private age key submission through T3. This workflow does not isolate secrets from unrestricted processes under the same OS account.

The Windows server account is separately enrolled as `win-srv-01-console` with kind `windows-console`. It supports `seal` and `verify`; KVM appliance login operations refuse this credential. `kvm_console.py` provides a separately authorized, ten-minute console operation with screenshots, limited sign-in navigation, and at most one visually gated password submission. It stores no persistent token and logs out of the KVM on completion. See the operator workflow before using it; it provides no power or arbitrary shell-command control.

Its opt-in `--allow-dependabot-install` mode adds a fixed, visually gated installer for Administrator on win-srv-01. Start `python -u tools/dependabot_deploy.py` first on Trigbotic: this serves only the installer and four non-secret skill files to win-srv-01 over Tailscale for up to ten minutes. Stop the transfer process after use. The installer and every skill file are hash-checked, differing installations are preserved, and the destination is the user-wide `.agents/skills` directory. See the operator workflow for screenshot confirmation and result verification.

## Extending tools

For an operator-requested SSH bootstrap on win-srv-01, `windows_ssh_setup.py` serves one fixed, hash-verified installer over Tailscale port 49219 to that worker only. Use `kvm_console.py --allow-ssh-setup` with a fresh private age submission and visual desktop/shell confirmation. The script configures the OpenSSH service, a commander-scoped firewall rule, and the dedicated public key in `config/ssh/trigbotic-win-srv-01.pub`. It backs up prior service/firewall/key-file settings locally on the server and prints the host fingerprint for verification through the pinned console. The SSH private key stays in the commander's user `.ssh` directory and is never transferred. Stop the transfer process after use. See the [operator workflow](../docs/runbooks/operator-secrets.md).

Use `adapters/README.md` for the future remote-execution contract. Provisioning, skill synchronization, health probes, and automated scheduling remain future work. Add platform-specific setup tools only when their target state and rollback behavior are known.
