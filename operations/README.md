# Operational records

`tasks/` stores curated assignment and ownership records. `results/` stores curated result reports. Use [the task](../templates/task.md) and [result](../templates/result.md) templates, with stable IDs such as `2026-10-27-project-short-name` and a numbered attempt.

The active commander owns ledger updates. Workers return reports through the documented harness/result channel; avoid multiple PCs concurrently editing the same ledger. Commit useful handoffs and completed results intentionally. Raw logs, transcripts, process state, and machine snapshots belong under ignored `.local/` or other host-local storage.

This directory is a human/agent-readable ledger, not a transactional queue, heartbeat service, or locking mechanism. If automated multi-writer orchestration is added later, use durable attempt IDs, atomic reservations, and reconciliation rather than Git polling as a lock.
