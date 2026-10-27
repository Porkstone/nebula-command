---
name: fleet-onboard
description: Inspect, configure, verify, and register a PC in the Nebula Tailscale fleet when adding a machine or reconciling its setup.
---

# Onboard a fleet machine

Locate the Nebula operating checkout. Read `inventory/README.md`, `docs/setup/target-state.md`, and only the platform/role setup guides relevant to this machine. Paths here are relative to that checkout, not the installed skill directory.

Inspect actual machine state and existing operator authorization before proposing changes. Register verified facts; leave unknown routing fields null and keep the machine disabled while staged. On Windows, `tools/Get-LocalMachineInfo.ps1` collects read-only local facts; curate its output rather than committing raw snapshots.

Choose a stable inventory ID and create `inventory/machines/<id>.md` from `templates/machine.md`. Record hardware, execution environment, account, session lifecycle, versions, and recovery access. For WSL, record the Linux target separately from the Windows host.

Apply only the authorized configuration needed for the target state. Preserve existing recovery access while changing SSH/network settings. Enrollment and provider login use supported local authentication flows; never copy credentials from another PC into the repo or handoff.

Select role-appropriate skills through `skills/catalog.json`, compare existing destinations, and follow `skills/README.md`. Record deployed revision/digest and verify harness discovery.

Verify from the commander: connectivity, host identity, intended account/shell, writable workspace, runtime/harness availability, durable session behavior, and a disposable task/result round trip. Record evidence and limitations before enabling dispatch. Run `python tools/inventory.py validate`, then `--ready` when preparing activation. Report unverified items honestly; structural validation is not a health probe.
