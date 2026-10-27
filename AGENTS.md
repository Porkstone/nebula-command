# Repository instructions

## Fleet context

This repo manages a Tailscale-connected fleet. Read `docs/architecture.md` and `inventory/README.md` before changing fleet behavior. `inventory/fleet.json` is authoritative; examples are not real targets. Do not infer that the machine running this session is the commander.

- Machine setup: use `skills/fleet-onboard/SKILL.md`.
- Work assignment: use `skills/fleet-orchestrate/SKILL.md`.
- Worker execution: use `skills/fleet-work/SKILL.md`.
- Interrupted work or commander changes: use `skills/fleet-recover/SKILL.md`.
- Dependabot configuration and dependency update workflows: use `skills/dependabot/SKILL.md`.
- Encrypted credentials and private key submission: use `skills/fleet-secrets/SKILL.md`.

The scaffold has no remote dispatcher. Do not describe task records as an executable queue or claim an SSH command started a durable managed agent session. Respect authorization already given in the current session; network reachability alone grants no permission to run work. Do not copy credentials between PCs.

## Planning

When creating a plan, store it in a standalone HTML file in `docs/plans`. Take care with layout and styling to make review easy. Put any clarification questions at the end of the plan.

## Scaffolding new projects

For a new frontend and backend project, default to:

```sh
pnpm create convex@latest -t react-vite <app-name>
```

For a frontend-only project, use:

```sh
pnpm create vite@latest <app-name> -- --template react-ts
```

Unless instructed differently, use TypeScript, pnpm, Tailwind, Lucide, and React Router when multiple pages are expected. Use Convex for the backend and Resend for email features. Do not assume authentication is required; ask when no instruction is given. When authentication is required, default to WorkOS AuthKit for frontend and backend.

## Deployment

For projects using Convex with Vercel frontend hosting, ensure `package.json` makes a Vercel build trigger a Convex deployment. Remind the operator to create a Convex deploy key and add it as a Vercel environment variable. This repo itself is tooling and documentation, not a web application.

## Validation

Run `python tools/inventory.py validate` after inventory edits. Use `--ready` when preparing activation. Run the unit tests after changing the validator or secret-handling tools. Never commit plaintext secrets, private decryption keys, provider login state, raw machine snapshots, or runtime logs. Reviewed age-encrypted credential files may live under `secrets/`; private keys must be supplied through the T3 private secret prompt for each operation. Never read a submitted private input into tool output.
