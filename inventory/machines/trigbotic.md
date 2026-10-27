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

No deployments have been verified or recorded. Use [the skill deployment guide](../../skills/README.md).

## Verification history

| Date | Source / verifier | Evidence | Limitations |
| --- | --- | --- | --- |
| 2026-10-27 | Operator | Machine name, commander role, and Tailscale IP supplied | No connectivity or execution checks performed |
| 2026-10-27 | Local read-only inspection | Hostname `TrigBotic`; OS `Microsoft Windows 11 Pro` | Does not verify the supplied Tailscale IP or remote access |

## Configuration changes

Registered inventory and detail record only. Follow [commander setup](../../docs/setup/commander.md) to complete activation.
