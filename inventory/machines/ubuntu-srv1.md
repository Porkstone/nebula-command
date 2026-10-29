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
- The operator independently verified ED25519 fingerprint `SHA256:+Kf8kYggyQ+6OuSbCFtC1IIxPTO0C/LTNOx2JhtvG9Y` on 2026-10-27. A matching live key was enrolled in the commander's current user's known hosts. The installation connection also checked this exact fingerprint before authentication.
- SSH account `charlie` and home `/home/charlie` were verified by authenticated execution. The password was supplied through a disposable private T3 input and was not retained. Workspace root, harness discovery, session lifecycle, and recovery access remain unverified.
- Assignment is disabled and capacity is 0 pending setup verification. Capability labels remain empty until verified.

## Deployed skills and instructions

- Dependabot installed globally for `charlie` at `/home/charlie/.agents/skills/dependabot` on 2026-10-27. All four files were checked byte-for-byte against the repository sources. Entrypoint SHA-256: `85179928b0838c542078747ed9f749209fa656590df593abeb9853ee43426edf`; supporting file hashes are pinned in `tools/dependabot_deploy.py`. Available across projects for harnesses using this global directory; actual harness discovery and other OS users remain unverified.
- Other deployments remain unverified. Use [the skill deployment guide](../../skills/README.md).

## Verification history

| Date | Source / verifier | Evidence | Limitations |
| --- | --- | --- | --- |
| 2026-10-27 | Operator | Machine name, worker role, Ubuntu OS family, and Tailscale IP supplied | No connectivity or execution checks performed |
| 2026-10-27 | Read-only checks from Trigbotic | Tailscale peer online; direct ping 1 ms; TCP 22 and SSH banner reachable; ED25519 fingerprint observed | Strict host-key verification blocked login before authentication; correct SSH username remains unconfirmed; no remote command executed |
| 2026-10-27 | Operator identity verification and authenticated SSH installation | Operator verified the ED25519 fingerprint; exact matching key enrolled locally. Account `charlie`, hostname `ubuntu-srv1`, and home `/home/charlie` verified. Global Dependabot installation and all four source hashes verified | One earlier login as `Charlie` was rejected; successful private input consumed. No retained password, harness-discovery check, or fleet activation |

## Configuration changes

Registered inventory, verified SSH identity and account, and installed the global Dependabot skill. Follow [worker setup](../../docs/setup/worker.md) and [Linux setup](../../docs/setup/linux.md) to complete activation. Assignment remains disabled.
