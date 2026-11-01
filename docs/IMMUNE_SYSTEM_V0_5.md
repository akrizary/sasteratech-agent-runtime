# Immune System v0.5

## Purpose

The Immune System is the mandatory execution boundary between model intent and side effects.

```text
MODEL / WORKER
    |
    v
ActionIntent
    |
    v
CapabilityGuard
    |
    v
Tool Argument Validation
    |
    v
Semantic Risk Judge (may BLOCK / ESCALATE only)
    |
    v
PolicyEngine
    |
    +-- needs approval --> ApprovalService --> HUMAN
    |
    v
Secret / Exfiltration Boundary
    |
    v
Idempotency + Effect Ledger
    |
    v
EXECUTOR
    |
    v
Post-action Readback / Verification
    |
    v
Evidence + Event + Checkpoint
```

## Sovereignty rules

1. A model judge can block or escalate. It cannot create R2-R4 authorization.
2. R2-R4 grants must be human-issued.
3. R1 policy grants may exist only if local policy explicitly permits them.
4. Network tools reject detected secrets unless the tool explicitly permits secret transmission.
5. R2-R4 side effects require a verification/readback contract unless explicitly configured as unverifiable; unverifiable high-risk effects remain PROVISIONAL.
6. Unknown non-idempotent effects are never blindly retried.
7. Tool output is untrusted content. Prompt-injection findings can withhold dangerous output from model context without deleting the raw execution record.
8. Logs/telemetry store redacted data by default.

## Current implementation

- structured approval requests and grants;
- human-only high-risk authorization;
- executable tool registry;
- deterministic argument validators;
- semantic risk judge interface;
- prompt-injection defender for untrusted tool results;
- secret detection/redaction;
- action/effect ledger;
- idempotency/replay protection;
- reconciliation API;
- post-action verification;
- structured contradiction scanner;
- integrated ToolGateway;
- SQLite schema v3;
- adversarial regression tests.

## Deliberate limit

The prompt-injection detector in v0.5 is a deterministic local defense layer, not a proof that content is safe. A production deployment may add a model/classifier-based defender, but deterministic privilege/policy controls remain authoritative.
