# Future remote execution adapters

No adapter is implemented. Start with the supported remote interface of the operator-selected harness and the supervised dispatch runbook. SSH can transport commands, but is not by itself a durable task scheduler.

An eventual adapter should expose:

| Operation | Required outcome |
| --- | --- |
| Inspect target | Reachability, execution identity, harness/version, capacity observation |
| Submit attempt | Stable caller-supplied dispatch identity, target/project/base commit, bounded handoff, acknowledgement/session receipt |
| Read attempt | Running/paused/terminal/unknown state, checkpoint timestamp, result reference |
| Reconcile attempt | Resolve ambiguous submit/disconnect without automatically duplicating work |
| Cancel attempt | Task-specific graceful stop and confirmation, preserving work |
| Collect result | Commit/branch, actual validation, limitations, remaining processes/artifacts |

Require a reviewed target list, literal structured arguments rather than string-built shell commands, isolated checkouts, and durable attempt identity. Define idempotency and crash recovery before automatic retries. Do not implement generic arbitrary remote shell execution as the default dispatch interface.

Any runtime state needs atomic reservation and commander fencing appropriate to its deployment. Store it outside curated Git records. Choose an adapter only after verifying the actual harness API and platform support.
