# Machine: Trigbotic

Inventory ID: `trigbotic`. Current role and Tailscale endpoint are authoritative in [fleet.json](../fleet.json). The operator designated this PC as commander.

## Identity and ownership

- Local hostname observed: `TrigBotic` (case-insensitive match to the supplied name).
- Execution environment: native Windows 11 Pro, confirmed by local OS inspection.
- Purpose: human-operated commander coordinating the fleet.
- Owner, location, account, shell, and availability: pending confirmation.

## Hardware

CPU, RAM, GPU, storage headroom, and power/sleep behavior have not been inventoried.

## Configuration

- The operator supplied the Tailscale IP; enrollment, tags, and network reachability have not been verified.
- OpenSSH on port 22 is the scaffold's proposed default, not a verified service configuration.
- SSH account, host identity, workspace root, harnesses, authentication, session lifecycle, and recovery access remain unverified.
- Assignment is disabled and capacity is 0 pending setup verification. Commander selection records responsibility independently of activation.

## Deployed skills and instructions

- Dependabot: verified on 2026-10-27 at `C:\Users\Charl\.agents\skills\dependabot`, available across projects to the current Codex user. SHA-256 comparisons confirm that `SKILL.md` and all three reference files match the repository sources. This session discovers the installed skill. Other users and harnesses remain unverified.
- Other skill deployments remain unverified. Use [the skill deployment guide](../../skills/README.md).

Commander SSH client configuration: `ssh nebula-win-srv-01` is installed for the current user from [trigbotic.config](../../config/ssh/trigbotic.config). It uses the dedicated local identity `C:\Users\Charl\.ssh\nebula_win_srv_01`; only [its public key](../../config/ssh/trigbotic-win-srv-01.pub) is in the repository. The server's ED25519 host key was compared with the fingerprint displayed through the pinned KVM and enrolled in local known hosts. Strict host checking and batch key authentication succeeded as `win-srv-01\Administrator`. Other users' SSH setup remains unverified.

## Verification history

| Date | Source / verifier | Evidence | Limitations |
| --- | --- | --- | --- |
| 2026-10-27 | Operator | Machine name, commander role, and Tailscale IP supplied | No connectivity or execution checks performed |
| 2026-10-27 | Local read-only inspection | Hostname `TrigBotic`; OS `Microsoft Windows 11 Pro` | Does not verify the supplied Tailscale IP or remote access |

## Configuration changes

Registered inventory and detail record only. Follow [commander setup](../../docs/setup/commander.md) to complete activation.
