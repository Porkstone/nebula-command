# Encrypted credentials with operator-supplied keys

Credential values may be committed here only as age-encrypted `.age` files. `catalog.json` is nonsecret metadata binding each credential to its machine, HTTPS origin, and ciphertext filename. The KVM credential is registered but **not enrolled**; no real password, key, or ciphertext has been created.

The operator holds the private age identity between operations, for example in LastPass. Each use requires a fresh T3 Code private secret submission. No permanent decryption identity is installed by this workflow.

Read [the complete operator workflow](../docs/runbooks/operator-secrets.md) before enrolling or using a credential.
