# Machine: win-srv-01

Inventory ID: `win-srv-01`. Current role and Tailscale endpoint are authoritative in [fleet.json](../fleet.json). The operator designated this PC as a worker.

## Identity and ownership

- Execution environment: Windows Server, as reported by the operator; edition and version pending confirmation.
- Purpose: engineering worker.
- Owner, location, account, shell, and availability: pending confirmation.

## Hardware

CPU, RAM, GPU, storage headroom, and power/sleep behavior have not been inventoried.

## Configuration

- The operator supplied the Tailscale IP; enrollment, tags, and network reachability have not been verified.
- OpenSSH on port 22 is the scaffold's proposed default, not a verified service configuration.
- SSH account, host identity, workspace root, harnesses, authentication, and session lifecycle remain unverified. The operator-provided KVM recovery access is documented below and has not been tested.
- Assignment is disabled and capacity is 0 pending setup verification. Capability labels remain empty until verified.

## Recovery access: network KVM

- Management URL: [https://100.126.31.7/#/](https://100.126.31.7/#/).
- Hardware/model, as supplied by the operator: GL.iNet GL-RM10 Comet Pro Wi-Fi 6 KVM Touchscreen 4K Passthrough.
- Managed machine: `win-srv-01`.
- Authentication: password required; stored in the operator's LastPass vault. The LastPass item name has not been recorded. Retrieve it from LastPass through an authorized secure workflow when a connection is needed; keep the password out of this repository.
- Encrypted credential slot: `win-srv-01-kvm` in `secrets/catalog.json`; not enrolled yet. [The T3 operator-key workflow](../../docs/runbooks/operator-secrets.md) supports encrypted storage and status-only login checks using a fresh private key submission for each use. Username, public recipient, TLS trust, and actual device compatibility remain to be verified.
- Verification: endpoint reachability, login, console access, and available recovery controls have not been tested.

## Deployed skills and instructions

No deployments have been verified or recorded. Use [the skill deployment guide](../../skills/README.md).

## Verification history

| Date | Source / verifier | Evidence | Limitations |
| --- | --- | --- | --- |
| 2026-10-27 | Operator | Machine name, worker role, Windows Server OS family, and Tailscale IP supplied | No connectivity or execution checks performed |
| 2026-10-27 | Operator | Network KVM URL, hardware/model, and password requirement supplied | No connection or login attempted |
| 2026-10-27 | Operator | KVM password is stored in LastPass | Vault item name and access have not been verified |

## Configuration changes

Registered inventory and detail record only. Follow [worker setup](../../docs/setup/worker.md) and [Windows setup](../../docs/setup/windows.md) to complete activation.
