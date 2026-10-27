# Nebula Command

The shared operating repository for agentic engineering across PCs connected by Tailscale. One **commander** coordinates work across **workers**. The commander is usually the PC the human operator is using directly and can also execute local tasks within its recorded capacity.

This scaffold provides inventory conventions, configuration examples, operating guides, reusable skills, and local inspection tools. Remote dispatch, scheduling, credential distribution, and service installation are not implemented yet. The live inventory contains Trigbotic (commander), win-srv-01 (Windows Server worker), and ubuntu-srv1 (Ubuntu worker), staged pending setup verification. Example machines are fictional.

## Repository map

```text
nebula-command/
├── AGENTS.md                  Instructions for agents working in this repo
├── inventory/
│   ├── fleet.json             Authoritative machine inventory and commander selection
│   ├── examples/              Fictional inventory to copy from
│   └── machines/              Human-readable records for real PCs
├── projects/                  Project ownership, repository URLs, and workspace mapping
├── config/
│   ├── ssh/                   Client configuration examples
│   └── tailscale/             Tailnet policy examples
├── secrets/                   Encrypted credentials and nonsecret target catalog
├── skills/
│   ├── fleet-onboard/         Register and configure a machine
│   ├── fleet-orchestrate/     Assign, track, and integrate work
│   ├── fleet-work/            Execute a bounded assignment and return evidence
│   ├── fleet-recover/         Reconcile interrupted work and commander changes
│   ├── dependabot/            Shared dependency update and security guidance
│   └── fleet-secrets/         Private operator key submission and credential use
├── tools/                     Local inventory validation and Windows hardware collection
├── templates/                 Machine, project, task, and result records
├── operations/
│   ├── tasks/                 Curated task handoffs and status
│   └── results/               Curated completion reports
├── docs/
│   ├── architecture.md        Roles, ownership, state, and trust boundaries
│   ├── setup/                 Commander, worker, and platform setup
│   ├── runbooks/              Dispatch, recovery, and commander handover
│   ├── plans/                 Standalone HTML plans
│   └── references.md          Research and upstream documentation
└── tests/                     Behavioral checks for local tools
```

## Start here

1. Read [the architecture](docs/architecture.md), [machine target state](docs/setup/target-state.md), and [inventory contract](inventory/README.md).
2. Register real PCs in `inventory/fleet.json`, with details in `inventory/machines/<id>.md` using [the template](templates/machine.md). Pick one commander and leave workers disabled until verified.
3. Follow [commander setup](docs/setup/commander.md), [worker setup](docs/setup/worker.md), and the relevant platform guide.
4. Add project records using [the project template](templates/project.md).
5. Validate the inventory, then follow [the dispatch runbook](docs/runbooks/dispatch.md).

From the repository root, with Python 3.11+:

```sh
python tools/inventory.py validate
python tools/inventory.py list
python tools/inventory.py validate --ready
python -m unittest discover -s tests -v
```

The first validation accepts an empty scaffold. `--ready` requires an enabled commander and complete connection details for enabled machines; it does not probe hosts or prove operational readiness. See [tool usage](tools/README.md).

## Repository-owned skills

The six skill folders under `skills/` are the canonical sources. [The catalog and deployment guide](skills/README.md) describe role selection and deployment records. Point a compatible harness at them or install reviewed copies into its skill directory; cloning the repo alone does not install them. Load only the skill relevant to the task. The repo’s `AGENTS.md` provides routing for agents reading this checkout.

Keep this repo private if it contains internal machine names or project information. Commit curated configuration and results; keep plaintext credentials, private keys, raw logs, and sessions outside Git. [Encrypted credentials](secrets/README.md) may be committed under `secrets/`; each use requires an operator-supplied key through T3 Code. See [the operator workflow](docs/runbooks/operator-secrets.md), [configuration conventions](config/README.md), and [operations conventions](operations/README.md).
