# Encrypted credentials with operator-supplied keys

Credential values may be committed here only as age-encrypted `.age` files. `catalog.json` is nonsecret metadata binding each credential to its machine, HTTPS origin, ciphertext filename, and optional operator-verified certificate pin. The `win-srv-01-kvm` credential is enrolled in `win-srv-01-kvm.json.age`; its private key and plaintext password are outside this repository.

The operator holds the private age identity between operations, for example in LastPass. Each use requires a fresh T3 Code private secret submission. The helper never automatically loads the operator's recovery-key file or caches a submitted identity for later use.

The KVM's pinned login/check/logout workflow succeeded on 2026-10-27 using private T3 submissions. No session is retained. See [the machine record](../inventory/machines/win-srv-01.md) for scope and verification history.

`win-srv-01-console.json.age` separately holds the Windows server's `Administrator` sign-in credential. Its `windows-console` kind binds it to `console://win-srv-01`, a logical machine-console identifier rather than a network destination. Enrollment, local decryption verification, and a bounded Windows sign-in succeeded through private T3 submissions on 2026-10-27. A console snapshot confirmed the resulting desktop; the KVM session was logged out afterward. The helper refuses to use this credential for KVM appliance login.

Read [the complete operator workflow](../docs/runbooks/operator-secrets.md) before enrolling or using a credential.
