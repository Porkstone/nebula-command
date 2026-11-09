---
name: fix-dbot-issues
description: Use this skill when you are asked to check one or more Repos for dependabot issues or when directly invoked
---

# Fix Dependabot issues across repositories

Invoked as `/fix-dbot-issues` (or `$fix-dbot-issues` in Codex). Check every repository in the assigned organization, or only the user's explicit repository list. Attempt all feasible fixes and collect them into **one PR per repository**. A PR cannot span repositories. Leave merging to the user.

## Establish scope and coverage

- Honor the worker handoff and each repository's own instructions. Use the assigned isolated checkout; for multiple repositories keep a separate checkout and branch for each. Do not change a checkout with unrelated work. Do not delegate or start other workers without authorization.
- Use the explicit repository list when supplied; normalize to `OWNER/REPO` and remove duplicates. Otherwise resolve the organization from the assignment or established session context. If ambiguous, ask for the organization; do not choose the first organization the account can access.
- Enumerate all organization repositories, including private repositories and forks visible to the authenticated account, following every pagination link. Do not silently exclude archived or disabled repositories: inspect when possible and report write restrictions. Confirm enumeration succeeded and disclose visibility limitations; an accessible subset is not proof of organization-wide coverage.
- Use an available GitHub connector or authenticated `gh` CLI. Check authentication and permissions without displaying tokens. Missing access, disabled alerts, rate limits, failed pagination, and API errors mean incomplete coverage, never zero issues. Continue independent repositories and report the blocker; resume after a known rate-limit reset if practical.

## Inspect every repository

Read the installed `dependabot` skill for ecosystem-specific work when available; this skill remains usable without it. Fetch **all open Dependabot security alerts**, then **all open PRs authored by GitHub's Dependabot app**, including ordinary version updates. Security alerts are not ordinary GitHub Issues and cannot be discovered solely through issue or PR searches. Do not depend on labels being present. If the user explicitly narrows the task to security alerts, respect that scope.

With `gh`, suitable read-only starting points are:

```sh
gh api --paginate 'orgs/ORG/repos?type=all&per_page=100'
gh api --paginate 'repos/OWNER/REPO/dependabot/alerts?state=open&per_page=100'
gh api --paginate 'repos/OWNER/REPO/pulls?state=open&per_page=100'
```

Substitute confirmed identifiers. Preserve page boundaries correctly when parsing multiple JSON responses; use `--slurp` if supported or process each page. Follow Dependabot's cursor pagination via the returned links, not invented numeric pages. Identify the actual Dependabot bot author from PR metadata (commonly `dependabot[bot]`), rather than inferring from titles. Check live API documentation if a response or supported option differs.

Build a per-repository ledger of alert numbers/URLs, advisories, package/ecosystem, manifest path, affected range, patched versions, and relevant bot PRs. Count each alert number once. Record PRs with no matching alert as separate update items; associate matching PRs with their alerts to avoid double-counting the same work. Grouped PRs can cover several alerts. Retain evidence for uncertain associations rather than hiding a pending update. Process critical/high vulnerabilities first, but finish all repositories and severities in scope.

## Apply and validate feasible fixes

1. Refresh the default branch and inspect existing remediation PRs before creating a branch. Reuse an existing consolidated PR only when it belongs to this authorized run or is explicitly assigned for continuation; otherwise preserve it and report any overlap. Never overwrite another contributor's work.
2. For each item, verify the installed dependency path and current advisory or update requirement. Prefer a compatible patched release; for transitive dependencies update the parent or use a supported narrow override after checking compatibility. Include necessary code migrations. Avoid blanket forced upgrades and unrelated refactors. No available patch, incompatible migrations, missing private registry access, and archived repositories may leave unresolved items; record specific reasons and continue.
3. Collect every viable fix on the same branch for that repository. Existing bot PR diffs may inform the changes, but inspect them and resolve combined constraints. Use the repository's package manager and regenerate its lockfiles; cover all affected manifests and workspaces. Do not dismiss alerts, disable scanning, add ignore rules, or remove used functionality to make the count fall.
4. Run the repository's required checks plus relevant install/build/tests and dependency scanning where supported. Confirm the resolved dependency graph is outside each addressed advisory's vulnerable ranges, including transitive copies. Classify unverified fixes honestly. Revert or isolate an incompatible fix so the remaining viable fixes can proceed. If essential validation is blocked, use a draft PR and explain the gap.
5. Review the final diff for only intended changes and no credentials or generated runtime state. Create exactly one consolidated PR for this run in that repository when there are useful changes. Include addressed alert/update links, package changes, checks and results, and the number and reasons for unresolved items. Do not create an empty PR. Leave existing bot PRs open unless their closure is explicitly authorized; explain which are superseded. Do not merge or enable auto-merge.

If the runtime supplies PR-linking tools, link each PR immediately after creating it or pushing to it. Do not start PR review monitoring unless separately requested. After completing each repository, save enough non-secret progress evidence to resume without duplicating PRs.

## Final reconciliation and user report

Recheck open alerts and bot PRs after the changes to catch newly appearing work and concurrent fixes. Attempt newly discovered items within the authorized scope; disclose later changes or any unfinished work at the final check time. Default-branch alerts usually remain open until the PR merges: distinguish **addressed in the PR, awaiting merge** from **unresolved by the PR**. Do not claim GitHub has closed an alert before it does.

When every scoped repository has been attempted, show these two lists, using `None` for an empty list:

1. **Repositories with a PR to merge** — `OWNER/REPO`, direct PR link, number of addressed items, **unresolved count** (including zero), and validation status. Identify draft/blocked PRs rather than presenting them as ready. Give unresolved item links and reasons where any remain.
2. **Repositories checked with no issues** — repository links for repositories whose complete in-scope alert and bot-PR queries succeeded and returned no open items at the final check. Do not put repositories with fixes awaiting merge here.

Below those lists, report **exceptions**: repositories with issues but no viable PR (known unresolved count and reasons), inaccessible/incomplete scans (unknown count where necessary), and any incomplete organization enumeration. These exceptions must not disappear merely because neither requested list fits them. Reconcile the totals against the deduplicated scoped repository list and state the final check time and overall coverage. Return worker task/attempt evidence through the agreed handoff channel when applicable.

API references: [organization repositories](https://docs.github.com/en/rest/repos/repos#list-organization-repositories), [Dependabot alerts](https://docs.github.com/en/rest/dependabot/alerts#list-dependabot-alerts-for-a-repository), [pull requests](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests).
