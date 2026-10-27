# Set up the commander

1. Choose the PC normally used by the human operator. Create its inventory entry and machine record; do not assume the current PC is the intended commander. Start disabled.
2. Follow [the target state](target-state.md) and the relevant [Windows](windows.md), [Linux](linux.md), or [macOS](macos.md) guide. Keep the operating repo in a stable local checkout.
3. Enroll Tailscale and review commander-to-worker access. Tailor `config/tailscale/policy.example.hujson` to the existing tailnet. Leave a recovery access path while changing policy.
4. Configure SSH client aliases using `config/ssh/config.example` if using OpenSSH. Verify worker host fingerprints through a trusted channel before adding them to known hosts; do not disable host key checking.
5. Install the selected harness and independently authenticate it. Deploy commander skills using [the skill catalog](../../skills/README.md). No harness is preselected by this scaffold.
6. Add project records, worker capacities, and task acceptance checks. Set this machine's role to `commander`, all others to `worker`, and its ID as the top-level `commander` in one inventory edit.
7. Enable verified machines and run `python tools/inventory.py validate --ready`. Test one disposable task using [the dispatch runbook](../runbooks/dispatch.md).

Keep the commander’s interactive capacity conservative. If it sleeps or disconnects, existing durable worker sessions may continue; do not start duplicate work from another PC without [a handover](../runbooks/commander-handover.md).
