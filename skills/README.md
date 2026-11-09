# Fleet skill sources and deployment

This directory is the canonical source for repository-owned skills. `catalog.json` records intended roles and harness scope. A role match makes a skill a deployment candidate; it does not authorize operations. Actual deployment is recorded per machine and harness in the machine detail record.

| Skill | Intended use |
| --- | --- |
| `fleet-onboard` | Inspect, configure, verify, and register a machine |
| `fleet-orchestrate` | Commander assignment, tracking, and integration |
| `fleet-work` | Execute one bounded assignment and return evidence |
| `baby-sit-pr` | Worker-only, explicitly invoked PR review monitoring and fixes |
| `fix-dbot-issues` | Worker remediation across an organization or explicit repo list; one consolidated PR per repo |
| `fleet-recover` | Reconcile uncertain attempts or transfer command |
| `dependabot` | Configure dependency updates and manage Dependabot workflows |
| `fleet-secrets` | Use encrypted credentials with operator-supplied keys through T3 Code |

The Dependabot skill is the operator-provided file, preserved unchanged. Its three referenced guides were included from the matching locally installed skill (the entrypoint hashes match). Optional plugin/tool instructions inside it do not mean those integrations are installed on fleet machines.

Dependabot is intended to be available across all projects on both commanders and workers. Install its complete folder in the relevant user's global skill directory for each selected harness, rather than in individual project directories. For the current Codex user on Trigbotic, this is `C:\Users\Charl\.agents\skills\dependabot`; the entrypoint and all three references match this repository. Other machines and harnesses still need their own deployment verification. Global availability does not authorize dependency changes without an assignment.

The worker skill `baby-sit-pr` runs only when a prompt or authorized handoff explicitly invokes `$baby-sit-pr` or the baby-sit PR skill. For example: `Use $baby-sit-pr to monitor https://github.com/OWNER/REPO/pull/123 and fix valid review findings.` This is an invocation example, not a real assignment. Deploy the complete folder, including `agents/openai.yaml`, which disables implicit invocation for compatible harnesses. For other harnesses, verify explicit-only selection before use. Adding the source does not install it on workers or start a monitor.

The worker skill `/fix-dbot-issues` (also `$fix-dbot-issues` in Codex) checks all repositories in the assigned organization unless the user supplies a repository list. It checks open security alerts and Dependabot update PRs, attempts fixes, and creates one consolidated PR per repository. Its report lists PRs with unresolved counts and repositories verified to have no issues, with blocked or inaccessible repositories reported separately. Deploy the complete folder, including `agents/openai.yaml`; normal automatic discovery is enabled. Installation does not run a scan or authorize merging.

Installed for all three registered worker accounts on 2026-11-09: `Charl` on [Trigbotic](../inventory/machines/trigbotic.md), `Administrator` on [win-srv-01](../inventory/machines/win-srv-01.md), and `charlie` on [ubuntu-srv1](../inventory/machines/ubuntu-srv1.md). All complete folders match the source hashes recorded in the machine records, and all three Codex app-server discovery checks returned the enabled global skill. Other users and harnesses are not covered by those checks.

## Deployment procedure

1. Read the machine's OS, role, selected harnesses, and existing skill destinations. Confirm the current discovery/install method for that harness; paths vary. These folders are portable source assets, not automatically installed global skills.
2. Select applicable catalog entries. `harnesses: ["any"]` means no harness-specific dependency, not proof that every harness supports this file format. Read the `SKILL.md` before deployment.
3. Compare source and destination. Preserve unrelated skills and local instruction files. Stage replacement copies in a temporary directory, retaining a local rollback copy for changed files.
4. Deploy complete skill folders through the approved file transfer path. Copy skill content, never provider login state, private keys, or unrelated home directories. Do not replace global `AGENTS.md` or `CLAUDE.md` with this repository's own instructions.
5. Record source revision/digest and destination path in `inventory/machines/<id>.md`. Confirm that the selected harness loads the skill and can resolve repository links from the local operating checkout or the handoff bundle. A worker receiving a minimal bundle needs only `fleet-work` and the task context it references.

No sync tool, automatic update agent, or installer is included yet. Drift is the difference between the recorded deployed revision/digest and current source. Review changes before updating machines.
