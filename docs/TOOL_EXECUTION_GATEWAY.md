# Tool Execution Gateway

## ToolRuntimeSpec

The executable registry binds a static `ToolDefinition` to runtime behavior:

- argument validator
- handler
- optional readback verifier
- secret transmission policy
- output trust class
- retry/reconciliation semantics

A model never receives raw Python callables.

## Execution order

1. Resolve tool definition/runtime spec.
2. Check role capability.
3. Validate action/tool/risk consistency.
4. Validate arguments deterministically.
5. Apply semantic risk advice. `BLOCK` stops. `ESCALATE` requires human approval.
6. Apply PolicyEngine and scoped ApprovalGrant.
7. Enforce secret/network policy.
8. Reserve idempotency/effect record.
9. Execute once.
10. Persist execution status.
11. For side effects, perform readback/post-action verification.
12. Mark effect VERIFIED / SUCCEEDED_UNVERIFIED / FAILED / UNKNOWN.
13. Defend/sanitize output before it returns to model context.

## Fail closed

- Validator failure: block.
- Missing required approval: defer/block.
- Risk judge failure for configured sensitive tool: escalate.
- Secret found in prohibited network argument: block.
- Existing UNKNOWN non-idempotent effect: reconciliation required.
- Verification failure: execution may have happened, but completion is not claimed.

## Additional invariants

- ActionIntent may not understate the registered tool risk.
- Action resource must remain inside the task-provided resource scope.
- R2+ side effects require readback verification by default.
- Side effects automatically fall back to the action ID as an idempotency key when no stronger semantic key is supplied.
