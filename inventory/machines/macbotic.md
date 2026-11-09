# Machine: Macbotic

Inventory ID: `macbotic`. Current role and routing are authoritative in [fleet.json](../fleet.json). The operator designated this computer as commander on 2026-11-09.

## Identity and ownership

- Machine name: `Macbotic`, supplied by the operator; actual hostname not yet verified.
- Owner/operator and physical location: pending confirmation.
- Execution environment: macOS, confirmed by the operator on 2026-11-09; version and architecture remain unverified.
- Shell and execution account: pending confirmation.
- Purpose: human-operated commander coordinating the fleet.
- Availability: pending confirmation.

## Hardware

CPU/architecture, RAM, GPU, storage headroom, and power/sleep/reboot behavior have not been inventoried.

## Configuration

- No exact `Macbotic` hostname or DNS-name match was found in the current Tailscale peer list on 2026-11-09. Enrollment identity, endpoint, tags, and reachability remain unverified; this does not establish that the machine is unenrolled.
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
| 2026-11-09 | Read-only Tailscale peer lookup | No exact hostname or DNS-name match for `Macbotic` in the current peer list | No authentication or remote execution attempted; endpoint remains unknown |

## Configuration changes

Added a staged commander record at the operator's request. Follow [commander setup](../../docs/setup/commander.md) to configure access, deploy skills, and verify execution before activation.
