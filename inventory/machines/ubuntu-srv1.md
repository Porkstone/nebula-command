# Machine: ubuntu-srv1

Inventory ID: `ubuntu-srv1`. Current role and Tailscale endpoint are authoritative in [fleet.json](../fleet.json). The operator designated this PC as a worker.

## Identity and ownership

- Execution environment: Ubuntu Linux, as reported by the operator; version and native/VM/WSL status pending confirmation.
- Purpose: engineering worker.
- Owner, location, account, shell, and availability: pending confirmation.

## Hardware

CPU, RAM, GPU, storage headroom, and power/sleep behavior have not been inventoried.

## Configuration

- The operator supplied the Tailscale IP; enrollment, tags, and network reachability have not been verified.
- OpenSSH on port 22 is the scaffold's proposed default, not a verified service configuration. Tailscale SSH has not been selected or verified.
- SSH account, host identity, workspace root, harnesses, authentication, session lifecycle, and recovery access remain unverified.
- Assignment is disabled and capacity is 0 pending setup verification. Capability labels remain empty until verified.

## Deployed skills and instructions

No deployments have been verified or recorded. Use [the skill deployment guide](../../skills/README.md).

## Verification history

| Date | Source / verifier | Evidence | Limitations |
| --- | --- | --- | --- |
| 2026-10-27 | Operator | Machine name, worker role, Ubuntu OS family, and Tailscale IP supplied | No connectivity or execution checks performed |

## Configuration changes

Registered inventory and detail record only. Follow [worker setup](../../docs/setup/worker.md) and [Linux setup](../../docs/setup/linux.md) to complete activation.
