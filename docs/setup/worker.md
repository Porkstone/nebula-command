# Set up a worker

1. Record the actual hardware, owner, OS, shell, available disk space, intended workloads, and workspace root using `templates/machine.md`. Add an inventory entry with `enabled: false` and role `worker`.
2. Follow [the target state](target-state.md) and the appropriate platform guide. Prefer a dedicated unprivileged execution account with access only to intended workspaces.
3. Enroll Tailscale. Verify the endpoint from the commander. Install/configure the selected SSH server if SSH is the transport. Restrict inbound access to the intended tailnet sources and ports.
4. Install project prerequisites and selected harnesses. Authenticate on this machine using their supported login process. Do not copy another machine’s provider-session directory.
5. Deploy applicable skills according to `skills/catalog.json` and record destination paths/revision. Confirm that the selected harness actually discovers them. Repo skills are not globally installed by this scaffold.
6. Choose a session lifecycle that survives the commander disconnecting. Use a supported harness service, or a documented persistent session. Record process ownership, session discovery, graceful-stop method, and restart behavior.
7. From the commander, verify hostname, SSH host identity, account, workspace write access, required runtime versions, and a representative disposable task. Confirm result retrieval after disconnect/reconnect.
8. Record proof in the machine record, choose conservative capacity, then enable the worker and run the ready check.

Configure sleep/power behavior deliberately. A sleeping laptop is an unavailable worker. A reboot is not evidence that a previously dispatched task completed or was safely cancelled.
