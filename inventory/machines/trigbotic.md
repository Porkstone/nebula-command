# Machine: Trigbotic

Inventory ID: `trigbotic`. Current role and Tailscale endpoint are authoritative in [fleet.json](../fleet.json). The operator designated this PC as a worker on 2026-11-09, replacing its previous commander designation.

## Identity and ownership

- Local hostname observed: `TrigBotic` (case-insensitive match to the supplied name).
- Execution environment: native Windows 11 Pro, confirmed by local OS inspection.
- Purpose: human-operated engineering worker.
- Execution account: `trigbotic\charl`, profile `C:\Users\Charl`; PowerShell. Owner and physical location remain unconfirmed.

## Hardware

Verified on 2026-11-09: AMD Ryzen 5 5560U with Radeon Graphics, 31,057,645,568 bytes RAM (approximately 28.9 GiB), approximately 45 GiB free on C:. Windows 11 Pro 10.0.26300, 64-bit. Current power plan is AMD Ryzen Balanced; idle sleep is disabled on AC and configured for 10 minutes on battery. No power configuration was changed; reboot, lid closure and network continuity are not guaranteed.

## Configuration

- Local `tailscale ip -4` confirmed `100.123.213.15` on 2026-11-09. Enrollment identity/tags remain unreviewed.
- OpenSSH on port 22 is the scaffold's proposed default, not a verified service configuration.
- SSH service and server host identity remain unverified. The verified local account is recorded in inventory for identity; that does not establish SSH access.
- Selected assignment interface: existing T3 Code service, environment `092fc721-316b-4b85-a39d-c99f1b65073f`, server `0.1.8-nightly.20261109.4399`, Codex harness. The Macbotic operator's current T3 session uses this host. Incoming SSH from Macbotic is not required by this interface and remains unverified.
- Enabled with capacity 1 for bounded T3/Codex work after the disposable task/result verification below. Default workspace root is `C:\files\development`; actual per-task checkouts are created and bound by T3 under `C:\Users\Charl\.t3\worktrees` and recorded in the task ledger. No live checkout or provider login state was copied.
- Recovery: retain the exact T3 thread and run receipt; read its state/results through the T3 service after reconnecting. Interrupt only the identified top-level thread when authorized. A lost connection is unknown until reconciled; do not launch a duplicate. Automatic resumption after host reboot/service loss has not been verified. Local operator recovery is available.

## T3 worker verification and current reservation

On 2026-11-09 the operator requested a new worker thread for `nestra-config-manager`. This authorized the bounded readiness checks and conservative activation needed for that assignment. The new isolated thread completed a disposable write/read round trip and stopped before feature execution. A separate T3 read retrieved its final result after completion, verifying the service's session/result-return path independently of an SSH shell.

- Thread: <t3-thread://v2/092fc721-316b-4b85-a39d-c99f1b65073f/mcp:launch:51fe4c523f19f11f92249806593fe14d84f6dfe150a7ed61430e1e48255794a1>
- Verification run: `run:thread:mcp%3Alaunch%3A51fe4c523f19f11f92249806593fe14d84f6dfe150a7ed61430e1e48255794a1:ordinal:1`, completed `2026-11-09T19:34:45.260Z`.
- Verified identity `TrigBotic`, `trigbotic\charl`; isolated branch `feat/proposal-document-pack` at `c9c00fd38c62aba5462617e0da5424540925bc32`, matching live `origin/master`.
- Ignored disposable `.local/nebula-preflight/result.json` exactly matched the task/attempt/machine and `result: passed`; tracked checkout remained clean.
- Task tools: Node 26.13.0, project-selected pnpm 10.34.7, .NET SDK 9.0.308, Git 2.56.0.windows.4, gh 2.103.3. Interactive global pnpm reports 12.15.0; use the project's selected version. Local Python and rg are present. Global Codex CLI reports 0.162.1; T3's own provider runtime is separate and successfully ran `gpt-6.1-sol`.
- GitHub API access for `Market-Harborough-Building-Society/nestra-config-manager` verified pull/push and maintainer/admin permissions for the existing machine-local account. This does not establish permissions for other repos or machines.
- The worker successfully read the minimal handoff skill at `C:\files\development\Nebula\nebula-command\skills\fleet-work\SKILL.md` and the explicitly invoked `C:\Users\Charl\.codex\skills\babysit\SKILL.md`. These paths are supplied in the task; this is not a claim of additional global skill installation/discovery.
- Current reservation: one slot for [nestra-proposal-document-pack-20261109](../../operations/tasks/nestra-proposal-document-pack-20261109.md), attempt 1. Commander retains integration and capacity-release decisions.

## Deployed skills and instructions

- `fix-dbot-issues` installed globally for `Charl` at `C:\Users\Charl\.agents\skills\fix-dbot-issues` on 2026-11-09 after the worker designation. Local hostname `TRIGBOTIC` and user profile were checked before installation. Both files match the repository source: `SKILL.md` SHA-256 `62fab0b80ac5e0391f2228235daf3f1a06a1cd5bd8c94b274ced5a7e8a055d75`; `agents/openai.yaml` SHA-256 `c794e62c659478fefde5c686fda7eb80dd4b10d53b77e60e17ca45ffb3259896`. Codex app-server `skills/list` with a forced reload returned the exact global path, `enabled: true`, and display name `Fix Dependabot issues`. The temporary discovery process tree was stopped. Other OS users and harnesses remain unverified.
- Dependabot: verified on 2026-10-27 at `C:\Users\Charl\.agents\skills\dependabot`, available across projects to the current Codex user. SHA-256 comparisons confirm that `SKILL.md` and all three reference files match the repository sources. This session discovers the installed skill. Other users and harnesses remain unverified.
- Other skill deployments remain unverified. Use [the skill deployment guide](../../skills/README.md).

SSH client configuration retained from the former commander role: `ssh nebula-win-srv-01` is installed for the current user from [trigbotic.config](../../config/ssh/trigbotic.config). It uses the dedicated local identity `C:\Users\Charl\.ssh\nebula_win_srv_01`; only [its public key](../../config/ssh/trigbotic-win-srv-01.pub) is in the repository. The server's ED25519 host key was compared with the fingerprint displayed through the pinned KVM and enrolled in local known hosts. Strict host checking and batch key authentication succeeded as `win-srv-01\Administrator`. Other users' SSH setup remains unverified. Retained access does not authorize worker-to-worker assignments.

## Verification history

| Date | Source / verifier | Evidence | Limitations |
| --- | --- | --- | --- |
| 2026-11-09 | Local worker skill installation under the operator's all-workers request | Staged and installed both `fix-dbot-issues` files, verified matching source hashes, and confirmed enabled Codex discovery for `Charl` | Other users and harnesses unverified; no repository scan or fleet activation |
| 2026-11-09 | Operator-requested role change | Changed `trigbotic` from commander to worker and cleared commander selection in the same inventory edit. All machines were already disabled with capacity 0; no task attempts are recorded under `operations/tasks` | Staged inventory change, with no replacement commander or dispatch activation. No live-controller fencing is claimed; existing SSH access retained |
| 2026-10-27 | Operator | Machine name, commander role, and Tailscale IP supplied | No connectivity or execution checks performed |
| 2026-10-27 | Local read-only inspection | Hostname `TrigBotic`; OS `Microsoft Windows 11 Pro` | Does not verify the supplied Tailscale IP or remote access |

## Configuration changes

Reclassified from commander to worker at the operator's request on 2026-11-09. Macbotic was subsequently selected as commander. T3/Codex execution is now enabled with capacity 1 following the evidence above. SSH setup and other harnesses remain outside the verified assignment path.
