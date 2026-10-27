# Assign and integrate work

This is a supervised procedure. Markdown task files do not launch agents, reserve distributed locks, or provide live status.

1. Read the live inventory, project record, current task ledger, and existing session receipts. Confirm this is the active commander. Run `python tools/inventory.py validate --ready` and check recent health of the intended worker.
2. Create `operations/tasks/<task-id>.md` from `templates/task.md`. Record objective, repository/base commit, scope, expected checks, allowed actions, resource/time limits, and integration owner. Respect the authorization already given; resolve genuinely missing scope before dependent actions.
3. Select an enabled machine with the required capabilities, harness, and free capacity. Count assigned/running/unknown attempts against capacity until reconciled. GUI tasks should use an appropriate worker rather than interrupt the commander's operator.
4. Record the assigned machine, attempt number, unique dispatch identity, and isolated checkout/branch. Mark `assigned`. Do this before launching work so an interrupted connection has something to reconcile against.
5. Use the selected harness's supported remote interface, or an explicitly supervised SSH session. Include the task ID and attempt in the handoff. Obtain the remote acknowledgement/session ID before marking `running`. Do not automatically resend an ambiguous launch.
6. Record checkpoints and blockers. A worker must stop or return a blocker if it needs permission outside the task's scope. Follow progress through the harness; do not use missing console output as proof of failure.
7. Collect a report using `templates/result.md`, including branch/commit, actual checks, limitations, and remaining processes/artifacts. Mark `review`; verify acceptance checks and integration ownership.
8. Integrate within the operator-authorized workflow. Record the final commit or PR, outcome, and disposition of the checkout/session before marking `completed` and releasing capacity.

On timeout or transport loss, mark the attempt `unknown` and follow [recovery](recovery.md). Do not launch a replacement until the previous attempt's status is known or its duplicate-execution risk has been explicitly resolved.
