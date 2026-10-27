---
name: fleet-secrets
description: Enroll or use encrypted Nebula fleet credentials through T3 Code private secret prompts, with operator-supplied decryption keys and status-only output.
---

# Use operator-supplied fleet secrets

Locate the Nebula operating checkout and read `docs/runbooks/operator-secrets.md`. Use the existing credential catalog and the operator's authorized action. This skill requires a runtime with `request_secret` private-file delivery and a local shell on the same host. If unavailable, report the missing capability; never collect secrets in chat.

Run `python tools/fleet_secrets.py status --credential <catalog-id>` before requesting a key. A missing credential requires enrollment with a confirmed public recipient and username, plus a separate private password submission. Never request a private key before it can be used. Do not generate a replacement key for existing ciphertext.

For every key-dependent operation, call `request_secret` yourself with `delivery: "file"`, a specific credential label, and the action in its reason. The operator enters the native age identity in the private card. Use only the returned private file path as `--input-file` to the helper. A cancellation/timeout stops the operation. Never read, print, copy, or inspect its contents through tools; never put the value in arguments, environment variables, or task handoffs.

Choose a fixed helper operation: `seal` for encryption, `verify` for local decryption checks, or `kvm-auth-check` for an authorized login/check/logout. For an explicitly requested Windows sign-in through the console, use the bounded `tools/kvm_console.py` operation described in the runbook. The helper consumes and deletes the disposable input before continuing; each new operation needs a fresh private submission. Do not pass a durable recovery-key file as input. No arbitrary consumer, plaintext password output, or persistent session storage is provided.

For `win-srv-01`, distinguish the two login stages: `win-srv-01-kvm` is the KVM appliance's `admin` credential; `win-srv-01-console` is the Windows server's `Administrator` credential used after entering the console. The server entry has kind `windows-console` and a logical `console://win-srv-01` binding. Never submit it to KVM appliance authentication; the helper rejects that action. The bounded console operation decrypts both credentials for one operator-authorized sign-in, keeps values and tokens in process memory, and allows at most one Windows password submission. Inspect a fresh console screenshot and identify the intended Windows account and password-field coordinates before sending `submit-password`. Stop if the screen, machine, account, or focus is ambiguous. Inspect the post-submit screen before claiming success, then send `finish` to log out of the KVM and terminate the helper. Never display a password or retry a rejected/ambiguous password submission automatically.

For a credential with an operator-verified `tls_pin_sha256` in the catalog, ignore certificate validity dates (`notBefore`/`notAfter`), self-signed issuer status, and hostname mismatch. The exact certificate pin is the identity check and must match before any credentials are sent. Do not block access, request certificate replacement, or ask for renewed approval solely because that unchanged pinned certificate is expired or not yet valid. The operator has already verified and approved the pin for `win-srv-01-kvm`.

For credentials without an approved pin, retain standard HTTPS validation. New pins require independent operator verification; record the verification source. Never allow an unverified TLS connection or accept a changed pin automatically. Stop if a pin changes or two-step confirmation is required. Do not retry login automatically or broaden device control beyond the requested action. Return only the helper's sanitized result, and distinguish local verification from actual authentication.

This workflow prevents normal disclosure in model context and logs. It does not isolate secrets from unrestricted processes under the same account. Never describe the private file or Python helper as an enforceable security boundary against such access.
