# Machine: Macbotic

Inventory ID: `macbotic`. Current role and routing are authoritative in [fleet.json](../fleet.json). The operator designated this computer as commander on 2026-11-09.

## Identity and hardware

- Computer name `Macbotic`, verified through authenticated `scutil` output.
- macOS 27.0.1, build 26A434; native Apple Silicon (`arm64`), Apple M1, 16 GiB RAM.
- Account `charlesbarker`, UID 501, home `/Users/charlesbarker`, configured shell `/bin/zsh`; verified on the Mac.
- Data volume approximately 926 GiB, with 465 GiB available at inspection.
- Purpose: human-operated commander. Physical location and expected availability remain unconfirmed.

## Access and workspace

- Tailscale peer identity matches the supplied name and macOS. A direct ping succeeded in 32 ms during setup. Enrollment identity/tags remain unreviewed.
- OpenSSH 10.3p1 / LibreSSL 3.3.6 on port 22. ED25519 fingerprint `SHA256:hn39+m0fkzWPxYvT5F2We6dpOsLIZ7452F1GAgp14rU` was independently supplied from the Mac's local console and matched before authentication.
- Password authentication was verified through disposable private T3 input, which was consumed without password output. Later operations successfully used a dedicated setup key restricted to Trigbotic, with agent, port, and X11 forwarding disabled. Its private identity stays on Trigbotic at `C:\Users\Charl\.ssh\nebula_macbotic_setup`; only its [public counterpart](../../config/ssh/trigbotic-macbotic-setup.pub) is tracked. Fingerprint: `SHA256:DAChBEXTzF26YfQg5JVQLZZiBm2+gP8HLEpl60A06Ps`.
- Operating checkout: `/Users/charlesbarker/development/Nebula/nebula-command`, cloned directly from `https://github.com/Porkstone/nebula-command.git` at commit `9a157e99ef1f648910d21db0522b9bfe68b81ed7`. Git remote access succeeded using the Mac's existing configuration. An initial reviewed inventory patch and plan were applied. No `.git` directory, private identity, or provider login state was copied between machines.
- Workspace is account-owned and writable. T3 Code Nightly, T3 Code Alpha, and Codex desktop apps are installed; GUI operation and T3 private-secret integration remain unverified. This session runs on Trigbotic, where T3 environment listing/linking tools are unavailable. The Mac's operating checkout receives the final setup records through a reviewed Git patch.
- Recovery: SSH from Trigbotic or the operator's local Mac session. No remote console recovery verified.

## Tools, authentication, and skills

Verified tools: Git 2.54.0, ripgrep 15.1.0, Python 3.14.5, Node 26.3.0, pnpm 11.6.0, Homebrew 7.0.6, GitHub CLI 2.94.0, and OpenSSH as above. Installed tmux 3.8 and upgraded Codex CLI from 0.157.1 to 0.167.0 through Homebrew.

The existing `gpt-6.1-sol` setting was preserved. The older CLI rejected it; the upgraded model catalog lists it as the default. Codex's ChatGPT login and local execution are verified: the final isolated test read its input and wrote the exact expected JSON result.

GitHub CLI reports an invalid token, with no `GH_TOKEN`/`GITHUB_TOKEN` environment override. The private card for a Mac-specific replacement token timed out; no replacement was installed. Git remote access succeeds, but GitHub API/PR operations require independent authentication.

Initial setup installed six commander skill folders under `/Users/charlesbarker/.agents/skills`: `fleet-onboard`, `fleet-orchestrate`, `fleet-work`, `fleet-recover`, `dependabot`, and `fleet-secrets`. All nine files match source SHA-256 hashes at commit `9a157e99ef1f648910d21db0522b9bfe68b81ed7`; deployment manifest SHA-256 `add88817290a0b7de1213d8a8fd393e3bff1355b6fde880ab2f2725c4f77d1bd`. Codex app-server discovery returned all six exact global paths with `enabled: true`. Other users and T3 runtime discovery remain unverified; `fleet-secrets` still requires a compatible private-secret runtime.

Added `/start-commander` on 2026-11-09 at `/Users/charlesbarker/.agents/skills/start-commander`, bringing the installed commander set to seven skills. Both canonical files match the current repository source: `SKILL.md` SHA-256 `1feb61f61c1274eeddd26829d2ec1fb861903b0996b2cab837ce033d97e80c72`; `agents/openai.yaml` SHA-256 `b4e902051be04f0814f74f72b526179c9ba86c54b3eacbbe7160487646440483`. Its non-secret `references/machine.json` binds `machine_id: macbotic` to the operating checkout above, SHA-256 `0660e721e253e554fac28514732ca12beccbf8ad535cfd848442535444533dd0`. Codex discovery returned the exact enabled global path; the binding, selected commander role, and referenced context files were checked against the live operating checkout. The discovery process was stopped. Installation did not start a commander service or dispatch work.

## Commander-to-worker access

- Generated the Mac's own worker identity at `/Users/charlesbarker/.ssh/nebula_workers`; only its [public key](../../config/ssh/macbotic-workers.pub) was transferred. Fingerprint: `SHA256:01nQwGfZlyJIyMQ4H5l/EaUahm83sZI+aoJ2sBfU0qw`.
- Dedicated aliases are in `~/.ssh/nebula-workers.config`, included by the user's SSH config. Windows and Ubuntu server keys matched the previously operator-verified fingerprints before enrollment. Existing configuration/access was preserved.
- Windows: authorized the Mac key with source restriction and forwarding disabled; added Macbotic alongside Trigbotic in the SSH firewall rule. Strict-host-checking batch SSH from Macbotic returned `win-srv-01\administrator`.
- Ubuntu: port 22 is reachable and host identity matches, but the Mac key is not authorized. No worker password was requested or copied.
- Trigbotic: port 22 was unreachable or filtered from the Mac. Incoming worker access remains unconfigured/unverified.
- Workers remain disabled. No worker task was dispatched or activated by these checks.

## Sessions, power, and validation

Supervised tmux sessions under `charlesbarker` survived the initiating SSH connection closing; panes and receipts were retrieved through later connections. This verifies terminal persistence, not an automatic dispatcher or managed agent service. Host-local test artifacts remain in the operating checkout's ignored `.local/smoke/` directory.

| Attempt | Outcome and retained evidence |
| --- | --- |
| 1 | `macbotic-commander-20261109`: old CLI rejected the model; dead pane retained in session `nebula-macbotic-smoke-20261109` |
| 2 | Suffix `-attempt2`: CLI 0.167.0 returned exit 0 but wrote no required result and reported local execution timeouts. Acceptance **failed**. Codex receipt `01a1c0fd-69d0-7bf1-8d95-3774c9767f06`; dead pane retained in session `nebula-macbotic-smoke-20261109-attempt2` |
| 3 | Suffix `-attempt3`: reconciled after reconnecting; exit 0 and the exact required `result.json` verified. Acceptance **passed**. Codex receipt `01a1c102-a607-77f0-9f5f-2c32d8e8e858`. The per-invocation feature flag is reported as removed; no user configuration was changed. The earlier timeout's cause was not established |

All three diagnostic tmux sessions were confirmed finished and removed; their host-local receipts/results remain for reference. For future supervised sessions, reconnect as the same account, inspect `/opt/homebrew/bin/tmux list-sessions`, and attach to the exact task session. Stop only identified sessions after establishing their outcome. tmux does not automatically survive reboot or logout.

Existing system idle sleep is 1 minute on both battery and AC; wake on network is enabled on AC. No global power settings were changed. Installed the user LaunchAgent `~/Library/LaunchAgents/com.nebula.commander-awake.plist`, service `gui/501/com.nebula.commander-awake`, running `/usr/bin/caffeinate -s`. Its running state and `PreventSystemSleep` assertion were verified on AC power. It prevents system idle sleep while plugged in and logged in, without changing battery or display settings; lid closure, logout, reboot, and network continuity remain unverified. To undo, boot out that exact launch service and remove its exact plist. Test jobs also used lifetime-scoped `caffeinate -i`.

Repository validation on Macbotic passed: valid inventory and 37 unit tests, with one skip. Final Codex 0.167.0 discovery returned all six enabled skills, and local task execution passed. Macbotic is enabled with one local task slot to reserve capacity for the operator. Worker assignment remains disabled; GitHub API operations need the independent login described above.

## Verification history and next steps

Later on 2026-11-09, the operator requested a worker thread for a proposal document-pack feature. Trigbotic passed an isolated T3/Codex task/result round trip and was enabled with one reserved slot. The operator's current T3 service runs on Trigbotic; it is the selected interface for this assignment. Trigbotic's incoming SSH remains unverified, and both server workers remain disabled. See [the task ledger](../../operations/tasks/nestra-proposal-document-pack-20261109.md). This supersedes the earlier all-workers-disabled setup state above; Macbotic remains commander and no leader handover occurred.

All observations above were made on 2026-11-09 during operator-authorized setup. Earlier steps included an initial closed SSH port, a verified password login whose helper exited before commands ran, and a private-card timeout; setup later resumed successfully with a fresh private submission. No secret input was retained.

Local commander setup and execution validation are complete. See the [setup plan](../../docs/plans/macbotic-commander-setup.html). GitHub CLI authentication and Ubuntu/Trigbotic worker access remain follow-up items before those operations can be used. The Windows worker's SSH access is verified, but full worker execution and activation remain separate. No diagnostic task remains running, and no worker has been enabled by this setup.
