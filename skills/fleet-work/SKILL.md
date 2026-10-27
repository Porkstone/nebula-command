---
name: fleet-work
description: Execute a bounded Nebula fleet assignment on a commander or worker and return task-specific validation evidence and remaining state.
---

# Execute one fleet assignment

Read the supplied task handoff and the project's own instructions. The handoff must identify task ID, attempt, repository/base commit, assigned machine, isolated checkout, allowed scope, expected checks, and result-return method. If critical details are missing, return a blocker before dependent work.

Confirm that the target environment and checkout match the handoff. Do not reuse another active task's checkout. Return the harness/session receipt so the commander can distinguish this attempt from a retry.

Complete the authorized work, run meaningful checks, and retain changes on the recorded branch. Use installed project tooling and honor project instructions. Do not reassign the task, promote a machine, or start additional agents unless explicitly included in the assignment.

On interruption, preserve task identity, branch, changes, and session state. A lost commander connection does not itself cancel authorized local work; follow the task's stated limits and stop conditions. Report blocked, failed, or uncertain states without claiming completion.

Return a report containing task/attempt and machine IDs, outcome, changed commit/branch, actual checks, limitations, and running processes or retained artifacts. Use `templates/result.md` when the operating checkout is available, otherwise these same fields in the agreed channel. The commander owns ledger updates, integration, and capacity release. Never include credentials in results.
