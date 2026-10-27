# Machine detail records

Add one `<inventory-id>.md` per real execution target using [the machine template](../../templates/machine.md). Describe hardware, owner, configuration, installed tool versions, and verification dates. Reference `../fleet.json` for current role and routing settings.

Keep raw discovery output in `.local/` and curate only useful nonsecret facts into these records.

Registered records: [Trigbotic](trigbotic.md), [win-srv-01](win-srv-01.md), and [ubuntu-srv1](ubuntu-srv1.md). See `../fleet.json` for current roles and Tailscale endpoints.
