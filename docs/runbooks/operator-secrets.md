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

HTTPS verification is mandatory. For a private CA, supply `--ca-file` pointing to a PEM CA certificate verified through a trusted channel. Certificate validation still checks the endpoint hostname/IP. There is no insecure TLS switch. The helper uses a direct HTTPS connection, does not use proxy environment variables, and refuses redirects.

## Cleanup and output contract

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
- [GL.iNet's auth handlers](https://github.com/gl-inet/glkvm/blob/main/kvmd/apps/kvmd/api/auth.py): basis for the login/check/logout adapter. The actual device has not been authenticated or probed by this implementation task.
