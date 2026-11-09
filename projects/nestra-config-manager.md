# Project: nestra-config-manager

- Repository: https://github.com/Market-Harborough-Building-Society/nestra-config-manager
- Integration owner: operator through Macbotic; no automatic merge or deployment authorized
- T3 project on Trigbotic: `932dda2a-7815-4757-9ad0-cba741e24378`
- Root checkout: `C:\Files\Development\Orange\Nestra\nestra-config-manager`; contains unrelated uncommitted work, which must be preserved
- Independent task base: latest verified `origin/master`; proposal document-pack attempt 1 pins `c9c00fd38c62aba5462617e0da5424540925bc32`
- Isolation: T3-managed worktree per task, actual path/branch in task record; never synchronize live roots or create a competing shell-managed worktree
- Runtime: Windows with .NET SDK 9.0.308 and Node 26.13.0; use project-selected pnpm (10.34.7 during verification)
- Instructions: read applicable AGENTS.md; read `convex/_generated/ai/guidelines.md` and applicable Convex skill before editing Convex; use the project's get-table skill when first encountering a table definition
- Validation: worker must inspect current package/project scripts and run the required build, type/lint and meaningful feature/API tests. Use isolated/mocked fixtures for generation checks; do not generate live production document packs
- Current task: [Proposal document pack](../operations/tasks/nestra-proposal-document-pack-20261109.md)
