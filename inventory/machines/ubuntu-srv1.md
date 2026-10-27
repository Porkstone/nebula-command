# Machine: ubuntu-srv1

Inventory ID: `ubuntu-srv1`. Current role and Tailscale endpoint are authoritative in [fleet.json](../fleet.json). The operator designated this PC as a worker.

## Identity and ownership

- Execution environment: Ubuntu Linux, as reported by the operator; version and native/VM/WSL status pending confirmation.
- Purpose: engineering worker.
- Owner, location, account, shell, and availability: pending confirmation.

## Hardware

CPU, RAM, GPU, storage headroom, and power/sleep behavior have not been inventoried.

## Configuration

- The supplied Tailscale endpoint was reachable from Trigbotic on 2026-10-27. Tailscale reported the peer online with hostname `ubuntu-srv1`; a direct Tailscale ping returned in 1 ms. Enrollment identity and policy tags remain unverified.
- TCP port 22 accepted connections and presented `SSH-2.0-OpenSSH_10.2p1 Ubuntu-2ubuntu3.8`. Tailscale SSH has not been selected or verified.
- The OpenSSH client refused to continue because the server host key is not yet trusted. The observed ED25519 fingerprint is `SHA256:+Kf8kYggyQ+6OuSbCFtC1IIxPTO0C/LTNOx2JhtvG9Y`; this network observation is **not independent identity verification**. Compare against the Ubuntu console's host key before enrolling it in known hosts.
- SSH account, host identity, workspace root, harnesses, authentication, session lifecycle, and recovery access remain unverified.
- Assignment is disabled and capacity is 0 pending setup verification. Capability labels remain empty until verified.

## Deployed skills and instructions

No deployments have been verified or recorded. Use [the skill deployment guide](../../skills/README.md).

## Verification history

| Date | Source / verifier | Evidence | Limitations |
| --- | --- | --- | --- |
| 2026-10-27 | Operator | Machine name, worker role, Ubuntu OS family, and Tailscale IP supplied | No connectivity or execution checks performed |
| 2026-10-27 | Read-only checks from Trigbotic | Tailscale peer online; direct ping 1 ms; TCP 22 and SSH banner reachable; ED25519 fingerprint observed | Strict host-key verification blocked login before authentication; correct SSH username remains unconfirmed; no remote command executed |

## Configuration changes

Registered inventory and detail record only. Follow [worker setup](../../docs/setup/worker.md) and [Linux setup](../../docs/setup/linux.md) to complete activation.
