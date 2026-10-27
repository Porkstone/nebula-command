# Fleet architecture

## Roles

The human operator sets goals and grants the scope of work. Exactly one enabled machine is selected as commander in an activated inventory. The commander holds the current task ledger, selects suitable workers, follows progress, and integrates results. It can run local work too, but must reserve capacity for the operator.

Workers run bounded tasks in their own checkouts and return evidence. They do not reassign work, promote themselves, or create additional workers unless the task explicitly authorizes this. A machine role describes responsibility; `enabled` expresses eligibility for assignment and is separate from reachability.

Tailscale supplies private network connectivity. SSH supplies an optional remote shell. The selected agent harness owns execution, permissions, and session persistence. Nebula Command supplies inventory and operating conventions. An eventual dispatcher must implement the contract in `tools/adapters/README.md`; none exists in this scaffold.

## Sources of truth

| Data | Location | Rule |
| --- | --- | --- |
| Machines, roles, capacity, selected commander | `inventory/fleet.json` | One canonical structured record per machine |
| Hardware, setup history, verification | `inventory/machines/<id>.md` | Reference inventory IDs; do not duplicate mutable routing settings |
| Project mappings and validation commands | `projects/<project-id>.md` | Name repos, paths, and integration owner |
| Task ownership and dispatch receipt | `operations/tasks/<task-id>.md` | One assigned machine and attempt at a time |
| Results and validation evidence | `operations/results/<task-id>-<attempt>.md` | Curated reports; redact sensitive details |
| Logs, leases, process IDs, transcripts | `.local/` or host-local storage | Ignored by Git; never treat Git as a distributed lock |
| Plaintext credentials, keys, and agent authentication | Operator vault or machine-local secret store | Never copied into this repository |
| Encrypted fleet credentials | `secrets/*.age` | Operator supplies the decryption key privately for each use; see the [workflow](runbooks/operator-secrets.md) |

## Task lifecycle

`draft → ready → assigned → running → review → completed`

Tasks can also enter `blocked`, `failed`, `cancelled`, or `unknown`. `assigned` means capacity is reserved and a handoff is recorded. `running` requires a worker acknowledgement and a harness/session receipt. Only the commander records reassignment and integration decisions. Workers report progress and results to the commander; they do not race to edit shared ledger files.

A lost connection is `unknown`, not proof that work stopped. Reconcile the existing attempt before starting a replacement. Record a new attempt number on a retry; preserve old session IDs and outputs. A result reaches `completed` only after the recorded acceptance checks and integration decision.

## Workspace and capacity

Use a separate clone or harness-managed worktree per task. Record repository URL, base commit, branch, and absolute worker path. Do not synchronize live working trees, `.git` directories, provider sessions, or package caches between machines. Exchange changes through Git commits/branches or reviewed patches.

Choose machines using enabled status, OS, capabilities, harness availability, current reservations, and operator impact. `max_parallel_tasks` is a ceiling, not evidence of free capacity; task records supply reservations. Initial capacity should be conservative, especially on the interactive commander.

## Access and control

Prefer commander-to-worker connectivity over unrestricted worker-to-worker access. Use ordinary OpenSSH over Tailscale as the cross-platform baseline; Tailscale SSH is an alternative on supported servers. Host key checks, tailnet policy, OS account permissions, and harness permissions remain separate controls.

Prefer a dedicated unprivileged worker account. Authenticate providers independently on each machine. Keep dashboards on loopback unless deliberately configured with authentication and a reviewed tailnet rule. Do not use public exposure as a prerequisite for remote work.

There is no automatic leader election. Commander transfer requires stopping new dispatch, reconciling active attempts, and retiring the old commander's authority before activating the new one. See the [handover runbook](runbooks/commander-handover.md).
