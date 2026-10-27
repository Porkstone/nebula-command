# References and research notes

Checked 27 October 2026. Video titles can change. Timestamped video links identify the original source; transcript mirrors were used to locate the spoken sections and may contain transcription errors. These are design references, not installed dependencies.

## Theo Browne's Fleet workflow

### Agent instructions and skill management

Original: [agent-instructions walkthrough, 3:19–4:10](https://www.youtube.com/watch?v=e1snsuY4lTI&t=199s). [Indexed transcript](https://2outube.com/watch?v=e1snsuY4lTI).

The transcript describes a Fleet repository made mostly of Markdown, shared instruction files, commander-only and universal skills, harness-specific skills, and metadata identifying intended destinations. Around 9:05 he explains why he deliberately does not publish the global instruction file and prefers people to learn the process. This does not establish whether the entire Fleet repo is public or private.

Applied here: canonical skill sources, a role/harness catalog, per-machine deployment records, and instructions tailored to this fleet. We did not copy his personal global instructions or assume his credentials/proxy setup.

### Machine setup and commander locality

Original: [“If you have a Claude sub, watch this,” 23:11–24:14](https://www.youtube.com/watch?v=D8PikZ1KhUo&t=1391s). [Indexed transcript](https://youtube-distilled.com/watch/D8PikZ1KhUo).

The transcript describes a management repo kept on the controlling machine, documentation of the other computers, and a setup guide describing the desired tools and configuration for a new box. New machines are configured through SSH using that context. Around 42:08 he distinguishes interactive fleet management on his current laptop from work assigned to remote servers or GUI-capable machines.

Applied here: a commander-owned ledger, machine inventory/detail records, a common target-state guide, and capability-based worker selection. A full operations-repo clone is optional on workers; the handoff can contain only relevant context.

## Public repository identification

The attempted public URL `github.com/t3dotgg/fleet` returned 404. This alone cannot distinguish a private repo from a different name or nonexistent URL. No public repository was verified as Theo's personal Fleet source. Do not conflate similarly named projects with it.

[T3 Code](https://github.com/pingdotgg/t3code) is a relevant public agent interface, not verified as the personal Fleet repository. [T3 Brigade Fleet](https://github.com/escoffier-labs/t3-brigade-fleet) is a separate project's dispatcher reference. Neither is installed or selected by this scaffold.

## Configuration references

- [Tailscale SSH](https://tailscale.com/docs/features/tailscale-ssh): server support and the distinction between network permission and SSH authorization. Windows workers use OpenSSH over the tailnet; macOS Tailscale SSH server support depends on the Tailscale variant.
- [Tailscale grants](https://tailscale.com/docs/features/access-control/grants) and [policy syntax](https://tailscale.com/docs/reference/syntax/policy-file): sources for the example network grants. Existing grants/ACLs remain additive; review the full policy in the admin console.
- [Microsoft OpenSSH setup](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse): Windows server installation, service, authentication, and firewall details.

Recheck the relevant upstream documentation before applying version-dependent configuration. The example tailnet policy has not been validated against the operator's actual tailnet.
