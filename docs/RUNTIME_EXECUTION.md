# Runtime Execution

## RuntimeRequest
Contains SasteraTech IDs, role, resolved model profile, prompt, developer instructions, budget, bounded context, optional resumable history and metadata.

## RuntimeBudget mapping
TaskBudget controls model requests, tool calls, total tokens, wall-clock seconds, optional per-request context and optional cost.

In v0.4, model-visible tool calls are forced to zero because the Immune System is not yet connected.

## RuntimeResponse statuses
`COMPLETE`, `UNAVAILABLE`, `TIMEOUT`, `BUDGET_EXCEEDED`, `PROVIDER_ERROR`, `CANCELLED`, `INVALID_RESPONSE`, `INTERNAL_ERROR`.

Failures are persisted facts about execution, not instructions to silently retry.
