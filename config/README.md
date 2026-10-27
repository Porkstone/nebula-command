# Configuration conventions

Files here are reviewed examples, not installed configuration. Copy and tailor them on the appropriate host. Record what was applied, by whom, and when in its machine record. Keep a rollback copy locally before modifying existing SSH or service settings.

- `ssh/config.example`: commander-side OpenSSH client entries.
- `tailscale/policy.example.hujson`: a minimal policy fragment for commander-to-worker SSH. Merge deliberately into the actual tailnet policy; grants and legacy ACLs are additive, so an existing allow-all rule would defeat this restriction.
- Platform and role guides live in `docs/setup/`.

Private keys, Tailscale enrollment keys, provider sessions, tokens, and plaintext passwords belong in operator-held or host-local secret storage. An environment variable name or secret-store reference may be documented; its plaintext value must not be committed. Reviewed age-encrypted credentials may live under `secrets/` using [the operator-supplied key workflow](../docs/runbooks/operator-secrets.md). There is no automatic configuration deployment or secret-sync tool in this scaffold.
