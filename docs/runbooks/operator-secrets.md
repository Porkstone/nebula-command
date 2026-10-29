# Operator-supplied decryption keys through T3 Code

This implementation keeps secrets out of the model conversation and normal tool output. It uses the runtime's `request_secret` tool with `delivery: "file"`. The agent receives a path to a private temporary file, never the value. The Python helper reads and deletes that submitted file, decrypts in a local age subprocess, and returns a fixed JSON status.

The private input file is local plaintext staging. It is not an inaccessible enclave. Processes with the same account's unrestricted file/process access, administrators, or a modified helper could access secrets. Python/age process memory is not guaranteed to be securely erased; swap and crash dumps remain OS concerns. Enforcing secrecy from a hostile or unrestricted agent requires a separately protected broker/tool accepting an opaque secret reference. This helper provides disciplined handling for trusted agent workflows.

## Prerequisites

- Python 3.11+ and a reviewed age installation. No Python packages are required.
- T3 Code with `request_secret` supporting private-file delivery on the same host/filesystem as the helper. Run the helper locally on the commander; do not assume a path issued on one PC exists on another.
- Operator ownership of a native age private identity and its public recipient. SSH, plugin, and passphrase-protected identities are deliberately unsupported here to avoid extra prompts or executables.
- For a real KVM authentication check: the correct username and independently verified HTTPS trust. Its API compatibility must still be verified on the installed firmware.

On this checkout, age 1.3.2 was downloaded from its official Windows release into ignored `.local/tools/age/age/` and the archive's SHA-256 was checked against the release asset digest. This is not a global install or automatic provisioning on other machines. Elsewhere, install age through its [official instructions](https://github.com/FiloSottile/age#installation); the helper otherwise uses `age` on PATH.

## Operator key setup

Generate a dedicated identity in a terminal controlled by the operator. For example, with an installed `age-keygen`:

```powershell
age-keygen -o "$env:USERPROFILE\nebula-operator.agekey"
age-keygen -y "$env:USERPROFILE\nebula-operator.agekey"
```

With this checkout's local binaries, use `.local/tools/age/age/age-keygen.exe` instead of `age-keygen`. The second command prints only the public recipient. Keep that public value for enrollment. Store the private file's contents in the operator's protected recovery location, such as LastPass. After verifying that backup, remove the temporary original through the operator's normal secure file-handling process. Do not ask the agent to display, read, upload, or delete the operator's durable recovery copy.

## Enroll a credential

1. Confirm the KVM username and the public recipient with the operator. A public recipient is safe to provide normally; the helper accepts native age recipients only.
2. Call `request_secret` with `delivery: "file"`, a label naming the KVM password, and a reason stating that it will be encrypted for this credential. The operator enters the password from LastPass in the private card, not chat.
3. Pass the exact returned private file path directly to the helper. Do not read it with a shell, interpolate its contents, or put the password in an argument/environment variable.

```powershell
python tools/fleet_secrets.py seal --credential win-srv-01-kvm --username ACTUAL_KVM_USER --recipient ACTUAL_PUBLIC_AGE_RECIPIENT --input-file 'EXACT_T3_PRIVATE_FILE_PATH'
```

Replace the capitalized values with the confirmed username, public recipient, and tool-returned path. These are illustrative placeholders, not secret references. The input file is consumed and removed before encryption. Password whitespace is preserved; multiline submissions are rejected. The encrypted payload binds the password to credential ID, machine ID, username, and origin. Default enrollment refuses an existing file; `--replace` is required for deliberate credential rotation.

Only `secrets/win-srv-01-kvm.json.age` is written. Keep LastPass as the operator's source of truth and refresh this ciphertext when its password changes. Public-key substitution during enrollment would compromise future ciphertext; verify the recipient through the operator, not an untrusted task payload.

## Use an encrypted credential

Check enrollment first; this needs no secret:

```powershell
python tools/fleet_secrets.py status --credential win-srv-01-kvm
```

Before **each** operation, call the runtime's `request_secret` tool:

```json
{
  "delivery": "file",
  "label": "Age private key for win-srv-01 KVM",
  "reason": "Decrypt the enrolled KVM credential for this one operation. The helper consumes the submitted key file and returns status only."
}
```

Use the actual private file path from its result immediately. Cancellation or timeout stops the operation; do not fall back to chat, a cached key, or a new key. Request a fresh private submission for a later attempt.

Local decryption/schema verification, with no network connection:

```powershell
python tools/fleet_secrets.py verify --credential win-srv-01-kvm --input-file 'EXACT_T3_PRIVATE_FILE_PATH'
```

For an operator-authorized authentication check, use a **new** private submission:

```powershell
python tools/fleet_secrets.py kvm-auth-check --credential win-srv-01-kvm --input-file 'EXACT_T3_PRIVATE_FILE_PATH'
```

The fixed KVM operation logs in, checks authentication, and logs out. It does not open a GUI, retain a browser session, expose session tokens, send keyboard input, or control power. It requests a 60-second session lifetime and never retries a login automatically. Two-step login is reported as requiring operator confirmation; this implementation does not complete that flow. A failed/unconfirmed logout is an error; the device's session expiry remains a fallback, not a verified guarantee on this firmware.

Standard HTTPS chain, hostname, and date verification is the default. For a private CA, supply `--ca-file` pointing to a PEM CA certificate verified through a trusted channel. Certificate validation still checks the endpoint hostname/IP.

For an appliance with an unusable factory certificate, an operator may independently verify the exact certificate's SHA-256 fingerprint and explicitly select certificate pinning. Only then add `tls_pin_sha256` (64 lowercase hexadecimal characters) to that credential's `secrets/catalog.json` entry. The helper completes the TLS handshake and compares the full leaf certificate's SHA-256 **before sending any HTTP request or password**. A mismatch closes the connection. This explicit mode replaces CA, hostname, and validity-date checks with that exact certificate identity; an expired certificate is accepted only in this mode. A changed device certificate requires a new independent verification. Do not combine this mode with `--ca-file` or enable it using a fingerprint copied from an unverified task payload.

For an unchanged operator-approved pin, certificate date validity is deliberately ignored. Do not request certificate replacement or repeated approval because that pinned certificate is expired or not yet valid. The `win-srv-01-kvm` pin has been verified and approved by the operator. A changed pin still requires new independent verification.

There is no unverified TLS mode. The helper uses a direct HTTPS connection, does not use proxy environment variables, and refuses redirects.

## Windows account after KVM login

There are two independent credentials for `win-srv-01`:

| Stage | Credential ID | Account | Binding |
| --- | --- | --- | --- |
| KVM appliance login | `win-srv-01-kvm` | `admin` | Pinned HTTPS endpoint in the catalog |
| Windows sign-in inside the console | `win-srv-01-console` | `Administrator`, as supplied by the operator | `console://win-srv-01` |

The console binding identifies the managed machine; it is not an HTTP, SSH, RDP, or WinRM endpoint. Enroll the Windows credential with the same private password submission and public age recipient procedure, selecting `--credential win-srv-01-console --username Administrator`. Scoped Windows account names are supported when supplied by the operator, including `.\user`, `MACHINE\user`, `DOMAIN\user`, and UPN names. Keep account scope separate from unverified SSH access settings.

Verify local decryption through a fresh private key submission:

```powershell
python tools/fleet_secrets.py verify --credential win-srv-01-console --input-file 'EXACT_T3_PRIVATE_FILE_PATH'
```

The helper rejects `kvm-auth-check` for a Windows console credential before attempting network access. New encrypted payloads bind credential kind as well as ID, machine, and origin; existing version-1 KVM ciphertext remains readable without re-enrollment. Each password remains independently rotatable.

Enrollment alone does not perform Windows sign-in. For an explicitly authorized attempt, the bounded console operation below keeps the password out of tool arguments, screenshots, logs, and agent context. Do not type or paste it into an arbitrary focused application or terminal.

## Bounded Windows console operation

With one fresh private T3 key submission, start a local interactive execution session:

```powershell
python -u tools/kvm_console.py --input-file 'EXACT_T3_PRIVATE_FILE_PATH'
```

This is one operation that decrypts both bound credentials, authenticates to the pinned KVM, and holds its token and Windows credential only in the helper's memory for at most ten minutes. It does not save a session token or private identity. The first result is a console JPEG path under ignored `.local/kvm-console/`, its SHA-256 reference, and its dimensions. Inspect the image locally before issuing any input; images may contain private desktop information and must not be committed or uploaded automatically.

Send one JSON command per line through the execution session's stdin. Allowed operations are `snapshot`, `unlock` (Ctrl+Alt+Delete), `key` (Tab/Enter/Escape only), `click`, `username` (the fixed stored account), `submit-password` (the stored Windows password once), and `finish`. There is no arbitrary text or shell-command operation.

For `click`, `username`, and `submit-password`, include `sha256` from the most recent snapshot and pixel coordinates `x`/`y`. Username/password actions also require `field_confirmed: true`, which is the agent/operator's attestation after visually inspecting the correct sign-in field. The reference expires after sixty seconds. The helper clicks the confirmed location, clears the field, and enters the stored value; password entry submits Enter and takes a post-submit snapshot without exposing secret text. It cannot independently prove a native field's semantics or prevent another operator changing the console, so stop on ambiguous screens or concurrent control.

After one password submission, only snapshots and `finish` are permitted. Do not infer successful Windows authentication from successful HID delivery: inspect the resulting console for a desktop, account error, or other outcome. No automatic password retry is performed. `finish`, stdin closure, timeout, or an error ends the operation and attempts KVM logout. Report an unconfirmed logout explicitly. The Windows session itself is not automatically logged out or locked after a successful sign-in.

The native endpoint shapes were reviewed in the GL.iNet source files `kvmd/apps/kvmd/api/hid.py` and `streamer.py`. The helper sends secret text in the pinned HTTPS request body, never its query string. Power, firmware, arbitrary command execution, and host configuration changes are outside this operation.

### Fixed Dependabot installation on win-srv-01

When the operator requests this installation, add `--allow-dependabot-install` to the console invocation. Inspect a fresh screenshot of the signed-in desktop before sending `open-dependabot-installer` with its `sha256` and `desktop_confirmed: true`. This opens a fixed PowerShell command. Inspect the resulting shell before sending `install-dependabot` with the latest `sha256` and `shell_confirmed: true`. No command text or destination is accepted from stdin. This opt-in mode permits these two actions after sign-in; the one-password limit remains unchanged.

Start `python -u tools/dependabot_deploy.py` on Trigbotic before the console operation. For at most ten minutes it serves only the fixed installer and four non-secret skill files, bound to the commander's Tailscale address on port 49218 and restricted to the worker's Tailscale source address. Stop this exact process after transfer. No firewall rules are changed. The HTTP transfer runs inside Tailscale's encrypted transport; it carries no credentials or private keys.

The short console command verifies the downloaded installer's SHA-256 before running it. The fixed installer checks the Windows machine and Administrator account, verifies every skill file's SHA-256 against the pinned manifest, then moves the staged directory into `%USERPROFILE%\.agents\skills\dependabot`. It preserves an existing differing installation and rejects linked parent directories. Failed downloads may leave a staging directory containing public skill files. The helper types in bounded chunks and never submits Enter after an ambiguous chunk failure. It allows one installation attempt; inspect the terminal result before claiming success. Use `snapshot` and `finish` afterward. A successful file installation does not verify harness discovery or deploy to other Windows users.

## Cleanup and output contract

For explicitly requested OpenSSH setup on win-srv-01, start `python -u tools/windows_ssh_setup.py` on Trigbotic. It serves only the fixed, non-secret setup script to the Windows worker on Tailscale port 49219 for at most ten minutes. Launch the console helper with `--allow-ssh-setup` and a fresh private age input. Visually gate `open-ssh-setup` with `desktop_confirmed: true` and the latest screenshot SHA, then `setup-ssh` with `shell_confirmed: true` and the new screenshot SHA. One setup attempt is allowed. The short command verifies the script hash before execution. It installs OpenSSH only when absent, scopes the standard firewall rule to the two Tailscale addresses, starts the service automatically, and appends the dedicated source-restricted public key for Administrator with SYSTEM/Administrators-only ACLs. Existing key entries are preserved and previous settings are backed up on the server. It does not disable password authentication, change the default shell, reboot, or create an execution account. Verify the displayed host fingerprint through the pinned KVM before enrolling the SSH host key. Finish the KVM session and stop the transfer process after use.

- `--input-file` is **destructive consumption**: use only the disposable file returned by T3, never a durable key, LastPass export, or unrelated file. Absolute regular files outside the repo are required; leaf symlinks are rejected. T3-provided access controls are relied on; the helper does not create this input file.
- Input is removed immediately after reading, including when later configuration/decryption/authentication fails. Abrupt OS termination before consumption can leave the original staging file; use the runtime's cleanup and inspect its status without displaying contents. Deletion is not forensic secure erasure.
- No key or plaintext password is written by the helper. age receives key bytes through stdin; decrypted output is captured inside the helper. Device responses and age stderr are never forwarded.
- Successful output contains only `ok`, credential ID, and an enumerated status. Error output contains only `ok` and a fixed error code. There is no `show`, `decrypt-to-file`, arbitrary consumer command, or secret environment export.
- Exit 0 means the named operation succeeded; 1 means a sanitized operation failure; 2 means argument error; 130 means interruption. `verified` proves local decryption/schema checks only. It does not establish KVM login or fleet readiness.

If a submitted input was rejected as unsafe, it was not consumed. If cleanup fails, output reports `input_read_or_cleanup_failed`; treat the disposable input as potentially remaining and remove that exact file through the trusted runtime/OS workflow.

## Rotation and recovery

Keep a protected backup of the operator identity. Git history retains old ciphertext. Losing the key can make credentials unrecoverable; compromising it requires changing the actual KVM password and re-enrolling, not merely replacing the encrypted file. Removing a recipient or rewriting current ciphertext does not revoke access to historical ciphertext.

The `.gitignore` under `secrets/` permits only reviewed metadata and `.age` files. It is an accident-prevention convention, not a content scanner or an access boundary.

## Implementation references

- [age identity stdin and native-key documentation](https://filippo.io/age/age.1): basis for the local decryption process.
- [T3 Code private-file secret delivery change](https://github.com/pingdotgg/t3code/pull/24809): runtime feature; the tool definition supplied by the active runtime is authoritative for invocation.
- [GL.iNet's auth handlers](https://github.com/gl-inet/glkvm/blob/main/kvmd/apps/kvmd/api/auth.py): basis for the login/check/logout adapter. See [the machine record](../../inventory/machines/win-srv-01.md) for actual device verification history.
