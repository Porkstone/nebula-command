---
name: fleet-orchestrate
description: Coordinate bounded engineering tasks across registered Nebula workers from the active commander, including assignment, progress, results, and integration.
---

# Coordinate fleet work

Locate the operating checkout and read `docs/runbooks/dispatch.md`, the live `inventory/fleet.json`, and the relevant project/task records. Do not use example inventory as targets. Confirm the active commander before assigning work.

Use existing user authorization to define a bounded task with a pinned base commit, isolated checkout, acceptance checks, resource limits, and integration owner. Match enabled machines by execution OS, capability, harness, and available reservations. Reserve room for the commander's human operator; route disruptive GUI work to a suitable worker.

Record task ID, attempt, target, and dispatch identity before launch. Use an available, authorized harness remote interface; this repo supplies no dispatcher. A shell connection alone is not a durable agent session. Capture acknowledgement and session receipt before marking running.

Assign each attempt to one worker. Worker-side delegation requires explicit task scope. Respect harness/workspace lifecycle rules instead of creating a second competing session mechanism. Treat ambiguous launch or lost connectivity as unknown and reconcile before resending.

Collect the result, actual validation evidence, commit/branch, and remaining processes. Verify acceptance and integrate within the authorized workflow. Record completion and capacity release only after the outcome is established. Use `templates/task.md` and `templates/result.md`; keep transient state and secrets out of Git.
