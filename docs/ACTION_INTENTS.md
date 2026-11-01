# Action Intents

Workers propose **ActionIntent** objects. Intents are not executions.

An intent includes:
- action_id
- worker_id / role
- tool_id
- resource
- requested risk
- purpose
- evidence expected
- approval reference if any

Execution path:

```text
worker proposes intent
  ↓
capability guard
  ↓
policy engine
  ↓
(optional semantic risk judge)
  ↓
executor adapter
  ↓
result + evidence
```

This prevents role prompts from becoming authorization mechanisms.
