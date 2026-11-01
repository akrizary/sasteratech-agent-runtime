# Policy, Risk and Approval

## R0 — Observe
Search, read, inspect, calculate, simulate.

## R1 — Reversible local/ephemeral
Generate new artifact, temporary files, sandbox state.

## R2 — Durable local/repository mutation
Edit canonical local files, commits, database writes, persistent project state.

## R3 — External mutation
Push, send, publish, create/update external SaaS records.

## R4 — Critical/destructive
Production deployment, deletion, secrets/security changes, financial/identity actions.

## ApprovalGrant

```json
{
  "approval_id": "APR-...",
  "risk_ceiling": "R2",
  "actions": ["file.write"],
  "resource_scope": ["/project/src/**"],
  "expires_at": "...",
  "nonce": "...",
  "issued_by": "human"
}
```

## Rules
- Scope may only narrow downstream.
- Expired approval is invalid.
- LLM cannot issue/extend ApprovalGrant.
- LLM judge may deny/escalate, never self-grant R2+.
- Every R2+ action links to approval_id.
- Where possible: read → plan → diff/preview → approve → execute → verify.
