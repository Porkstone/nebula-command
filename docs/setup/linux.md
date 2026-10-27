# Linux execution targets

- Record the distribution, version, shell, CPU, memory, GPU, storage, and available disk space. Keep package installation appropriate to that distribution.
- Install Tailscale through its supported package instructions, enroll in the intended tailnet, and record the MagicDNS name or stable endpoint.
- For ordinary OpenSSH, configure a dedicated unprivileged user and `sshd`. Allow the intended tailnet sources and preserve a tested recovery connection while editing firewall/auth settings.
- Alternatively select Tailscale SSH, enable it explicitly on a supported installation, and review both network grants and the separate SSH policy for exact OS users. Do not assume SSH key policy and Tailscale SSH policy are interchangeable.
- Install Git, SSH client, `rg`, Python 3.11+, and the project's required runtimes. Node/pnpm and container tools are optional workload requirements. Record versions available in the noninteractive execution environment, which may differ from an interactive shell.
- A harness-managed remote service or a user service can manage durable agent execution. `tmux` is useful for supervised terminal work. Record how to find sessions, stop the correct task, view logs, and recover after reboot.
- Create workspaces owned by the execution account. Configure sleep and service startup deliberately; inspect user-service logout behavior if using user services.

Complete [the target state](target-state.md), a disposable task, and a disconnect/reconnect check before enabling dispatch. No distribution-specific provisioning script is supplied yet.
