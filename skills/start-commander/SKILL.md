---
name: start-commander
description: Load verified Nebula commander identity, responsibilities, machine details, and fleet operating context when /start-commander is invoked or the user asks to initialize a commander session.
---

# Start a commander session

Invoked as `/start-commander` (or `$start-commander` in Codex). Build a concise, current commander briefing and retain it in this conversation's working context. This initializes context; it does not launch a service or dispatch work.

## Resolve the commander and execution host

An installed copy may have `references/machine.json` containing `machine_id` and an absolute `operating_checkout`. Read that binding first when present. It locates this installation's intended machine and operating repository; the live inventory still determines its role.

Honor an explicit machine named by the operator. Otherwise use the installation binding, or match observed execution-host identity to the live inventory. Locate the operating checkout from the binding, existing session context, or the current repository/ancestors. Paths below are relative to that checkout, not this skill's installation folder. If no unambiguous machine or operating checkout can be established, report the missing identity/path and ask only for that information.

Distinguish **the intended commander** from **the host executing tools**. Inspect non-secret hostname, OS, account, and working-directory facts through the available tools. A UI on one PC may use a harness on another. Keep the operator's explicit meaning of “this machine,” and record the actual tool host separately. Use the intended target's OS and verified connection for target commands; never execute target setup against another host by assumption.

Read `inventory/fleet.json` and confirm that the intended machine exists, has role `commander`, and matches the selected top-level `commander`. Run the repository's structural validator when available. Do not select the inventory commander as the local machine merely because it is selected. If identity, role, or selection conflicts, report the mismatch and leave commander authority unconfirmed. Do not promote a worker, rewrite inventory, or silently fall back to another commander.

A disabled selected commander can load **staged commander context**; report that assignment is disabled. Loading context does not enable machines or expand existing task authorization.

## Load useful operating context

Read `docs/architecture.md`, `inventory/README.md`, `inventory/machines/<machine_id>.md`, `skills/catalog.json`, and `skills/fleet-orchestrate/SKILL.md`. Read relevant project/task records when there is a current assignment. Check actual task records for active or unknown attempts and reservations; a configured capacity is a ceiling, not proof of free capacity. Do not treat task Markdown as an executable queue or distributed lock.

Bring these facts into working context, distinguishing recorded observations and their dates from fresh checks:

- Commander name/ID, selected role, enabled state, and the separate tool host/account when different.
- OS, architecture, CPU/RAM, shell/account, available storage, and operator availability where known.
- Operating checkout, workspace root, current branch/revision and dirty state, plus relevant project paths. Never overwrite existing work to initialize a session.
- Tailscale endpoint, verified SSH aliases/identities and connection method, and a LAN address only when established. Network presence alone is not execution readiness.
- Task capacity, known reservations, configured harnesses, installed commander skills, and their discovery/verification status.
- Authentication summaries for the current target account, worker-access limitations, and the scope actually verified. Do not inherit authentication status from another PC or assume repository/PR permissions from a login alone.
- Session persistence/reconnect method, power/sleep constraints, recovery access, outstanding setup items, and any uncertain attempts that must be reconciled before a retry.

Prefer the curated machine record for hardware/history. Lightweight read-only checks may refresh identity, workspace state, tool versions, or login status using existing access. If tools run elsewhere and no verified target connection is available, load the available records and label live target facts unverified. Report unavailable or failed checks without guessing. Do not start login flows, request credentials, inspect authentication files/private keys, or perform a fleet-wide health scan just to load context. Never print tokens or copy provider login state between machines.

## Establish the session's role

Adopt the verified commander's responsibility to maintain task ownership, select eligible workers, follow progress, verify acceptance evidence, coordinate integration, and reconcile interruptions within the operator's authorized scope. Reserve capacity for the human operator. Workers remain bounded execution targets; delegation and machine activation require their own authorized task scope.

Respond with a compact briefing beginning **“Commander context loaded: <name> (<id>)”**, or **“Staged commander context loaded”** when disabled. Include the operating checkout, execution host if different, capacity/reservations, harnesses, and material blockers. If verification failed, say so instead of claiming context was confirmed.

Retain the briefing and source paths in the conversation, including after context compaction. For this session, use the resolved commander as the referent for commander work while keeping tool execution location explicit. Refresh identity/selection when the user changes machines, after a commander handover, or before assigning work if the context may be stale. Do not edit global instructions or create persistent memory as a side effect of invocation.
