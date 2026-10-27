---
name: fleet-recover
description: Reconcile interrupted or uncertain Nebula task attempts, recover worker sessions, or transfer command between PCs without duplicate dispatch.
---

# Recover fleet control

Read the affected task records and `docs/runbooks/recovery.md` in the operating checkout. For commander changes also read `docs/runbooks/commander-handover.md`.

Prevent new assignment to affected capacity while investigating. Use recorded attempt and session IDs to distinguish network loss, authentication failure, harness failure, and a stopped task. Preserve existing branches and changes before any restart or retry.

Restore observation of an existing running attempt when possible. If a launch outcome is ambiguous, keep it unknown and reserved; do not resend merely because SSH timed out. New retries need distinct attempt numbers linked to previous receipts. Stop only identified task processes within existing authorization.

For commander transfer, stop dispatch or establish an effective fence on the old commander first. Git inventory edits alone do not fence a live controller. Reconcile inherited attempts, configure the replacement's own access, then change commander selection and roles together. If the old commander cannot be fenced, report that blocker instead of activating competing control.

Record observed state, evidence, preserved artifacts, retry/integration decisions, and remaining uncertainty. Restore capacity only after verification. Keep raw logs host-local and secret values out of incident records.
