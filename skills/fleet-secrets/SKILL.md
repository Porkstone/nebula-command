---
name: fleet-secrets
description: Enroll or use encrypted Nebula fleet credentials through T3 Code private secret prompts, with operator-supplied decryption keys and status-only output.
---

# Use operator-supplied fleet secrets

Locate the Nebula operating checkout and read `docs/runbooks/operator-secrets.md`. Use the existing credential catalog and the operator's authorized action. This skill requires a runtime with `request_secret` private-file delivery and a local shell on the same host. If unavailable, report the missing capability; never collect secrets in chat.

Run `python tools/fleet_secrets.py status --credential <catalog-id>` before requesting a key. A missing credential requires enrollment with a confirmed public recipient and username, plus a separate private password submission. Never request a private key before it can be used. Do not generate a replacement key for existing ciphertext.

For every key-dependent operation, call `request_secret` yourself with `delivery: "file"`, a specific credential label, and the action in its reason. The operator enters the native age identity in the private card. Use only the returned private file path as `--input-file` to the helper. A cancellation/timeout stops the operation. Never read, print, copy, or inspect its contents through tools; never put the value in arguments, environment variables, or task handoffs.

Choose a fixed helper operation: `seal` for encryption, `verify` for local decryption checks, or `kvm-auth-check` for an authorized login/check/logout. The helper consumes and deletes the disposable input before continuing; each retry needs a fresh private submission. Do not pass a durable recovery-key file as input. No arbitrary consumer, plaintext output, or retained session operation is provided.

Keep HTTPS validation enabled. Stop on untrusted certificates or two-step confirmation requirements and report the fixed error code. Do not retry login automatically or broaden device control beyond the requested action. Return only the helper's sanitized result, and distinguish local verification from actual authentication.

This workflow prevents normal disclosure in model context and logs. It does not isolate secrets from unrestricted processes under the same account. Never describe the private file or Python helper as an enforceable security boundary against such access.
