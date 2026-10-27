# macOS execution targets

- Record macOS version, architecture, hardware, available disk space, shell, and intended workloads. Install selected tools through their supported installers or the operator's existing package manager.
- Install and enroll Tailscale. Use ordinary OpenSSH over Tailscale as the default. Enable Remote Login only for the intended execution account, configure keys, and verify the host fingerprint from the commander.
- If selecting Tailscale SSH instead, verify the currently supported macOS distribution of Tailscale; its SSH server requires the open-source `tailscaled` variant. The GUI app alone does not imply server support. See [upstream SSH documentation](https://tailscale.com/docs/features/tailscale-ssh).
- Install Git, SSH client, `rg`, Python 3.11+, and project prerequisites. Record the selected harnesses and their versions; authenticate locally.
- Choose the harness's supported remote lifecycle or a documented persistent terminal/session service. `tmux` can support supervised terminal work. Verify survival of SSH disconnects and document logout/reboot behavior.
- Computer-use workloads may require a logged-in desktop and macOS privacy permissions. Verify those with a disposable task; do not infer GUI access from successful SSH.
- Keep the operator's interactive desktop available, and document power/sleep settings. Put task checkouts under an absolute execution-account-owned workspace root.

Complete [the target state](target-state.md) and record verification before enabling the machine.
