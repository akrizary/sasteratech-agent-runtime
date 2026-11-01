# HARNESS.md — Runtime Composition

## Preferred deployment shape

```text
Application
  └─ SasteraTech Domain Layer
       ├─ Intake
       ├─ Router
       ├─ Plan/State
       ├─ Policy
       ├─ Evidence
       ├─ Memory Governance
       ├─ Eval
       └─ Adapter Interfaces
            └─ Pydantic AI Adapter (preferred)
                 ├─ model provider
                 ├─ workspace/sandbox
                 ├─ planning
                 ├─ memory
                 ├─ skills
                 ├─ subagents
                 ├─ dynamic workflow
                 ├─ guardrails
                 ├─ approval
                 ├─ trajectory/tool judges
                 ├─ durability
                 └─ telemetry
```

## One core runtime
Do not compose competing orchestration runtimes into the same control loop by default. It creates duplicate state, retries and approval semantics.

## Adapter rule
Runtime-specific code stays under `src/sasteratech_runtime/adapters/`.

## Determinism boundary
Use deterministic code for:
- risk overrides;
- state transitions;
- approval matching;
- path/tool permissions;
- evidence completeness;
- budgets;
- idempotency;
- canonical-memory promotion requirements.

Use models for:
- semantic classification;
- synthesis;
- hypothesis generation;
- review;
- context compression;
- candidate memory extraction;
- trajectory advice.
