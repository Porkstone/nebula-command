# Recover interrupted work

1. Stop new assignment for the affected machine by setting its capacity to 0 or disabling it. Preserve task files, attempt IDs, branches, and session receipts.
2. Distinguish tailnet connectivity, SSH/account access, harness availability, and the task process. Check each relevant layer without restarting services blindly.
3. Query the recorded harness/session ID or reconnect to the documented persistent session. Inspect task-specific process ownership, checkout, branch, and recent commits. Do not kill processes by broad name matching.
4. If still running, restore observation and keep the same attempt. If paused, record the required input. If completed, retrieve its result and verify it. If definitely stopped, preserve changes before deciding whether to resume or create a new attempt.
5. If outcome remains ambiguous, retain `unknown` and the capacity reservation. Record evidence and the decision needed. Do not create duplicate work merely because a transport timed out.
6. A retry gets a new attempt number and checkout/session receipt with a link to the old attempt. A cancelled attempt is recorded as stopped only after confirmation where possible.
7. Restore assignment capacity only after a representative health check and reconciliation of reservations.

For an unreachable commander, use [commander handover](commander-handover.md). If compromise is suspected, isolate the affected access and rotate the specific credentials through their owning systems; keep secret values out of incident notes.
