# Machine: win-srv-01

Inventory ID: `win-srv-01`. Current role and Tailscale endpoint are authoritative in [fleet.json](../fleet.json). The operator designated this PC as a worker.

## Identity and ownership

- Execution environment: Windows Server 2025 Standard Evaluation, observed on the KVM desktop watermark after sign-in on 2026-10-27. Full OS build and system configuration have not been queried.
- Purpose: engineering worker.
- Owner, location, account, shell, and availability: pending confirmation.

## Hardware

CPU, RAM, GPU, storage headroom, and power/sleep behavior have not been inventoried.

## Configuration

- The supplied Tailscale endpoint was reachable from Trigbotic on 2026-10-27. Tailscale reported this peer online with hostname `Win-Srv-01`; a direct Tailscale ping returned in 1 ms. Enrollment identity and policy tags remain unverified.
- TCP port 22 initially refused connections. OpenSSH bootstrap on 2026-10-27 subsequently succeeded: `sshd` is running with automatic startup, and key-based login from Trigbotic as `Administrator` is verified. The default remote shell is Windows `cmd.exe`; invoke PowerShell explicitly for PowerShell commands.
- ED25519 host identity: `SHA256:gdYXf645Y4pWj8XajTeXRRouJAY87nGLcpC9w7tnhoQ`. Compared the live network key with the fingerprint displayed through the operator-verified pinned KVM, then enrolled the matching key in the commander's current user's known hosts.
- The enabled `OpenSSH-Server-In-TCP` rule permits TCP 22 at local address `100.121.209.21` from `100.123.213.15` only; verified through authenticated SSH. Other existing firewall rules have not been audited.
- Dedicated commander public key: [trigbotic-win-srv-01.pub](../../config/ssh/trigbotic-win-srv-01.pub), fingerprint `SHA256:W3tFY+Wv57k9A8W03zVqSMRn2ud//MpJBzvqionXeoE`. Private identity stays at `C:\Users\Charl\.ssh\nebula_win_srv_01`, outside this repository, with current-user/SYSTEM/Administrators-only ACL. The server key entry restricts source to the commander and disables agent, port, and X11 forwarding. Existing entries were preserved. The administrator authorized-keys ACL was verified as protected with SYSTEM and Administrators only.
- Local shortcut on Trigbotic: `ssh nebula-win-srv-01`; source configuration is [trigbotic.config](../../config/ssh/trigbotic.config). Password authentication was not changed. This is a bootstrap administrator connection, not a dedicated unprivileged worker account.
- TCP connections succeeded on ports 3389 (normally RDP) and 5985 (normally WinRM HTTP). Port 5986 (normally WinRM HTTPS) actively refused connections. Protocol behavior and authenticated sessions have not been tested.
- Workspace root, harness discovery, and durable session lifecycle remain unverified. KVM authentication, graphical console inspection, sign-in keyboard/mouse input, Windows sign-in, and SSH key authentication are verified.
- Assignment is disabled and capacity is 0 pending setup verification. Capability labels remain empty until verified.

## Recovery access: network KVM

- Management URL: [https://100.126.31.7/#/](https://100.126.31.7/#/).
- Hardware/model, as supplied by the operator: GL.iNet GL-RM10 Comet Pro Wi-Fi 6 KVM Touchscreen 4K Passthrough.
- Managed machine: `win-srv-01`.
- Authentication: password required; stored in the operator's LastPass vault. The LastPass item name has not been recorded. Retrieve it from LastPass through an authorized secure workflow when a connection is needed; keep the password out of this repository.
- Encrypted credential: `win-srv-01-kvm` in `secrets/catalog.json`, enrolled to the dedicated operator public recipient on 2026-10-27. [The T3 operator-key workflow](../../docs/runbooks/operator-secrets.md) uses a fresh private key submission for each decryption. Username, exact certificate pin, and login/check/logout compatibility are verified.
- KVM reachability: Tailscale reports `kvm-win-srv1.tail318394.ts.net` online; a direct ping from Trigbotic returned in 1 ms on 2026-10-27. HTTPS responds, but standard certificate verification fails.
- Verified factory certificate: self-signed, CN `localhost`, validity 1970-01-01 through 1979-12-30. SHA-256 `4dfcb9a9cf17f246ee272f0f4d725ca00fee02f9b236e7fff516de4439843575`. On 2026-10-27 the operator confirmed independent fingerprint verification and explicitly selected exact certificate pinning. This pin is active in `secrets/catalog.json`; the helper checks it before sending credentials.
- KVM username: `admin`, confirmed by the operator on 2026-10-27.
- Operator public recipient: [operator-20261027.txt](../../config/age-recipients/operator-20261027.txt). The dedicated private identity was generated outside the repo with an explicit `TRIGBOTIC\Charl`-only Windows ACL; human backup to LastPass is pending. It must still be supplied through a private T3 card for each decryption operation.
- Authentication verified on 2026-10-27: operator supplied the private age identity through T3; the helper decrypted the credential, matched the configured certificate pin, logged in, checked authentication, and logged out. Only `authenticated_and_logged_out` status was returned; no key, password, or token appeared in tool output.
- Console sign-in verified on 2026-10-27: inspected the Windows lock screen, sent Ctrl+Alt+Delete, confirmed the `Administrator` password field, and submitted the stored password once. The next screenshot showed the Windows desktop. The helper then logged out of the KVM and terminated; Windows was left signed in.
- No persistent KVM session was retained. Power, firmware, and recovery controls have not been tested or changed.

## Windows server sign-in

- Account: `Administrator`, supplied by the operator; no additional domain or machine scope was specified.
- Encrypted credential: `win-srv-01-console`, stored separately in `secrets/win-srv-01-console.json.age` and encrypted to the existing operator public recipient.
- Intended use: Windows sign-in after KVM appliance authentication. Kind `windows-console` and logical binding `console://win-srv-01` prevent the credential from being submitted to the appliance login operation.
- The password was supplied through a private T3 card and its disposable plaintext input was consumed. Local decryption and credential-binding verification succeeded using a separately supplied private age identity. A subsequent bounded KVM console operation successfully signed in as `Administrator` with one password submission and visual desktop confirmation. Temporary private inputs were consumed. Account privileges and remote-login permissions have not been tested.
- This account is now verified for SSH bootstrap access using a separate dedicated commander key. The encrypted console password was not copied or used for SSH authentication. Worker assignment remains disabled.

## Deployed skills and instructions

- Dependabot installed globally for `Administrator` at `C:\Users\Administrator\.agents\skills\dependabot` on 2026-10-27. The fixed installer checked the machine/account, verified all four SHA-256 hashes, and displayed `DEPENDABOT VERIFIED` with the entrypoint hash `85179928b0838c542078747ed9f749209fa656590df593abeb9853ee43426edf`. Files match the pinned source manifest in `tools/dependabot_deploy.py`. Available across projects for harnesses using this global directory; actual harness discovery and other OS users remain unverified.
- Other deployments remain unverified. Use [the skill deployment guide](../../skills/README.md).

## Verification history

| Date | Source / verifier | Evidence | Limitations |
| --- | --- | --- | --- |
| 2026-10-27 | Operator | Machine name, worker role, Windows Server OS family, and Tailscale IP supplied | No connectivity or execution checks performed |
| 2026-10-27 | Operator | Network KVM URL, hardware/model, and password requirement supplied | No connection or login attempted |
| 2026-10-27 | Operator | KVM password is stored in LastPass | Vault item name and access have not been verified |
| 2026-10-27 | Read-only checks from Trigbotic | Tailscale peer online; direct ping 1 ms; TCP 3389 and 5985 reachable; TCP 22 and 5986 refused | No authentication, remote command, or configuration change performed; KVM not probed |
| 2026-10-27 | KVM access preparation | KVM Tailscale/HTTPS endpoint reachable; expired self-signed certificate inspected; dedicated operator key generated with current-user-only ACL | No KVM credentials sent; certificate trust, username, credential enrollment, and authenticated access remain pending |
| 2026-10-27 | Operator | Confirmed username `admin`, independently verified the recorded certificate fingerprint, and chose exact pinning | Credential enrollment and authenticated access pending |
| 2026-10-27 | T3 private password submission | Password encrypted to the dedicated public recipient; disposable plaintext input consumed | No plaintext password or private key entered tool output; authenticated access pending |
| 2026-10-27 | T3 private identity submission and bounded live helper check | `authenticated_and_logged_out`: decryption, operator-approved certificate pin, admin login, authenticated check, and logout succeeded | No retained session, console-control test, or server configuration change |
| 2026-10-27 | Operator username and T3 private password submission | Windows account `Administrator` enrolled as a separate age-encrypted console credential; disposable input consumed | Local decryption verification pending; no Windows authentication attempt |
| 2026-10-27 | T3 private identity submission and local helper check | `verified`: Windows credential decrypted successfully and matched its kind, machine, and console binding; no password output | No Windows authentication attempt or session created |
| 2026-10-27 | Bounded KVM console operation with fresh T3 private identity | Ctrl+Alt+Delete, verified Administrator password field, one encrypted-password submission, and visual Windows desktop confirmation succeeded; KVM logout confirmed | Windows left signed in; no commands, host settings, firmware, or power controls used |
| 2026-10-27 | Operator-authorized global skill installation through pinned KVM | Fixed PowerShell installer verified all four Dependabot files at Administrator's user-wide skill path. Transfer used only five non-secret files over Tailscale, restricted to this worker. Success and entrypoint hash visually confirmed; KVM logged out and transfer listener stopped | Initial long HID request timed out; unsubmitted input cleared before the short installer command. Harness discovery and other users remain unverified; assignment stays disabled |
| 2026-10-27 | Operator-authorized SSH bootstrap through pinned KVM, followed by authenticated SSH checks | Configured automatic sshd startup, scoped the standard firewall rule, installed the dedicated source-restricted public key, and verified host identity through the KVM. Strict-host-checking batch key login returned `win-srv-01\administrator` and `Win-Srv-01`; remote queries verified service, firewall scope, authorized-key ACL, and existing Dependabot hash | Uses Administrator; no dedicated execution account, durable agent session, or dispatch activation. Password authentication remains unchanged |

## Configuration changes

Registered the machine, enrolled the encrypted KVM credential, configured operator-verified certificate pinning, installed Dependabot globally, and bootstrapped verified SSH access. Prior SSH service/firewall/key-file settings were backed up locally at `C:\ProgramData\ssh\nebula-backup-20261027-223257`. Follow [worker setup](../../docs/setup/worker.md) and [Windows setup](../../docs/setup/windows.md) to complete worker activation; SSH access alone does not enable worker assignment.
