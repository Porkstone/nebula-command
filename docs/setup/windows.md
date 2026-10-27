# Windows execution targets

Use Windows-native tools for Windows tasks. Treat WSL as a separate Linux environment when work actually runs there; Windows and WSL have distinct paths, service lifecycles, and possibly different network endpoints.

## Inspect first

In PowerShell, from this repository:

```powershell
New-Item -ItemType Directory -Force .local | Out-Null
./tools/Get-LocalMachineInfo.ps1 | Set-Content -Encoding UTF8 .local/machine-snapshot.json
```

This reads local hardware/OS facts and returns JSON. Curate the relevant facts into the machine record. It does not enroll Tailscale or assign a role.

## Configure

- Install Tailscale using its supported Windows installer and enroll interactively in the intended tailnet.
- If acting as an SSH worker, use Windows OpenSSH Server and a dedicated local account. Follow [Microsoft’s current setup guide](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse). Review the created inbound firewall rule; scope it to the intended tailnet access and retain required recovery access.
- Configure public-key authentication, verify host keys, and test the exact account from the commander before tightening password settings. Administrative accounts can use a different authorized-keys location; consult the Microsoft guide rather than assuming a user-home path.
- Use ordinary OpenSSH over Tailscale. The Tailscale SSH server is not supported on Windows; network connectivity and SSH server authentication are separate.
- Record the remote default shell and test quoting/path handling. Do not send POSIX shell commands to a PowerShell session by assumption.
- Record an absolute Windows workspace path, such as `C:\work\nebula`. Install Git, Python, and project-specific tools for the execution account. Install the chosen harness only if it supports this execution environment.
- Choose a supported harness service or documented Windows session mechanism. A remote process started in a transient SSH shell is not automatically durable. Record its behavior across logout, sleep, and restart.

Verify all items in [the target state](target-state.md). This scaffold does not change Windows services, firewall, execution policy, or power settings.
