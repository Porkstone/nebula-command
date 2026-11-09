# Machine: Macbotic

Inventory ID: `macbotic`. Current role and routing are authoritative in [fleet.json](../fleet.json). The operator designated this computer as commander on 2026-11-09.

## Identity and ownership

- Machine name: `Macbotic`, supplied by the operator and matched to the Tailscale peer's reported hostname on 2026-11-09; authenticated OS-level hostname verification remains pending.
- Owner/operator and physical location: pending confirmation.
- Execution environment: macOS, confirmed by the operator and Tailscale peer data on 2026-11-09; version and architecture remain unverified.
- Shell and execution account: pending confirmation.
- Purpose: human-operated commander coordinating the fleet.
- Availability: pending confirmation.

## Hardware

CPU/architecture, RAM, GPU, storage headroom, and power/sleep/reboot behavior have not been inventoried.

## Configuration

- A refreshed Tailscale peer lookup on 2026-11-09 matched hostname `Macbotic`, reported macOS, and showed the peer online. Its IPv4 endpoint is recorded in `fleet.json`. Enrollment identity/tags, direct connectivity, SSH access, and commander-to-worker access remain unverified; Tailscale online status alone does not establish execution readiness.
- SSH account, host identity, workspace ownership, installed tools, harnesses, local authentication, session lifecycle, and recovery access remain unverified.
- OpenSSH and port 22 are proposed defaults, not verified service settings.
- Commander designation is staged: assignment remains disabled with capacity 0 pending setup verification. No worker dispatch was started.
- The inventory had no selected commander before this addition, all registered machines were disabled with capacity 0, and no task attempts were recorded under `operations/tasks`. This selection does not claim to fence any external controller.
- Configure this machine's own connectivity and provider authentication; do not copy Trigbotic's private SSH identity or provider sessions.

## Deployed skills and instructions

No skill installations or harness discovery have been verified on Macbotic. Select commander skills from [the catalog](../../skills/catalog.json) and follow [the deployment guide](../../skills/README.md).

## Verification history

| Date | Source / verifier | Evidence | Limitations |
| --- | --- | --- | --- |
| 2026-11-09 | Operator | Supplied machine name `Macbotic` and requested commander designation | No endpoint, account, workspace, hardware, or runtime verification supplied |
| 2026-11-09 | Operator | Confirmed macOS; registered `macbotic` with role `commander` and selected it as the inventory commander | macOS version, architecture, connectivity, and execution readiness remain unverified; assignment stays disabled |
| 2026-11-09 | Initial read-only Tailscale peer lookup | No exact hostname or DNS-name match for `Macbotic` in that peer list | No authentication or remote execution attempted; endpoint was unknown at this check |
| 2026-11-09 | Refreshed read-only Tailscale CLI lookup | Matched hostname `Macbotic`, OS `macOS`, IPv4 endpoint, and online status; recorded the observed endpoint in `fleet.json` | No direct connectivity, SSH authentication, or remote execution tested; assignment remains disabled |

## Configuration changes

Added a staged commander record and recorded the Tailscale-observed endpoint at the operator's request. Follow [commander setup](../../docs/setup/commander.md) to configure access, deploy skills, and verify execution before activation.
