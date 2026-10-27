# Transfer command to another PC

There is no automatic leader election or fencing service. Git edits alone cannot prevent two commanders from assigning work.

1. Stop new dispatch on the old commander. If unreachable, establish an effective fence first: revoke its worker access or stop its dispatch mechanism through a separately trusted control path. If it cannot be fenced, leave the new commander inactive and resolve that condition with the operator.
2. Capture the latest inventory and task records, including uncommitted handoffs and all known session IDs. Reconcile active/unknown attempts on each worker. Existing worker tasks need not be killed simply to change commanders.
3. Bring the new commander's checkout up to date. Configure and verify its own connectivity and harness access without copying private keys or provider sessions from the old machine.
4. In one inventory edit, demote the old commander to `worker` (disabled until reviewed), promote the new one, and update the selected `commander` ID. Review any tailnet tags, grants, and account permissions affected by the transfer.
5. Record the operator, timestamp, previous/new commander IDs, fence evidence, and inherited active tasks in a handover task record. Validate the inventory and verify that only the new commander can dispatch.
6. Resume assignment with reconciled capacity. Record how to reverse the transfer if connectivity fails.

If both machines were assigning work, stop new launches and reconcile every task/attempt first. Treat duplicate attempts as an incident requiring a single integration owner.
