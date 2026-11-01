# Durability and Recovery

Persist:
- run_id / parent_run_id
- task/state
- plan graph
- checkpoints
- budgets
- approvals
- tool intents/results
- evidence
- artifacts
- errors/retries

Checkpoint after:
- plan acceptance
- each durable mutation
- replay-sensitive external call
- completed task node
- before human wait
- before/after production deployment

## Recovery
`STATE_X_RECOVERY`:
1. locate last trusted checkpoint;
2. classify uncertain side effects;
3. reconcile actual state;
4. resume or rollback.

Never blindly replay an uncertain mutation.
