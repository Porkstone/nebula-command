# Target state for a Nebula machine

Describe the finished machine here; platform guides supply the OS-specific details. Verify existing state before installing anything. This guide is the common onboarding contract, inspired by the Fleet setup walkthrough cited in [references](../references.md).

## Every execution target

- Stable inventory ID, hostname, owner, execution OS, shell, and absolute workspace root.
- Tailscale enrolled in the intended tailnet, with the actual endpoint and applicable policy recorded.
- Git, a suitable SSH client, `rg`, Python 3.11+, and the project’s required runtimes/build tools available to the execution account. Node and pnpm are defaults for JavaScript projects, not mandatory on every specialized worker.
- Selected harnesses installed, versions recorded, and provider authentication completed locally.
- Applicable skills deployed from a known repository revision using `skills/catalog.json`; destination paths, hashes or revision, and verification recorded in the machine record. Preserve unrelated local skills and instructions.
- A disposable checkout where the intended account can run one representative validation task.
- Known power/sleep behavior, disk headroom, task capacity, and reboot/session recovery procedure.
- No credentials or raw login state stored in this operating repository.

## Commander additions

- Human operator can use the machine directly; local task capacity leaves room for interactive use.
- Holds the authoritative working copy of the fleet inventory and task ledger. Workers can receive a minimal relevant handoff without needing the entire operations repo.
- Can reach each enabled worker using the documented transport and verify its identity.
- Knows how to locate worker sessions, stop a specific attempt, retrieve results, and hand over command.

## Worker additions

- A dedicated execution account and SSH service, or an explicitly selected harness remote interface.
- Noninteractive SSH connectivity verified when SSH is used; known host keys enrolled through a trusted channel.
- Durable sessions through the harness’s supported remote service, or an appropriate terminal/session manager. `tmux` is an option on Linux/macOS, not a native Windows requirement.
- One isolated checkout per task, explicit capacity limits, and a working result-return path.

## Onboarding proof

Record the date, verifier, command/tool versions, connectivity result, harness session ID, disposable-task result, and outstanding limitations in `inventory/machines/<id>.md`. Enable assignment only after verification. A structural inventory check cannot replace these observations.
