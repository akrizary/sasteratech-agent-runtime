# Architecture Decisions

## ADR-001 — One runtime, many borrowed mechanisms
Avoid competing orchestration runtimes inside one control loop.

## ADR-002 — Pydantic AI preferred first adapter
Broad composable harness surface and provider neutrality.
Caveat: Harness 0.x, therefore strict adapter boundary.

## ADR-003 — Deterministic policy sovereignty
Models may advise/deny/escalate; they cannot create high-risk authority.

## ADR-004 — Hybrid memory
Observational compression + retrieval + temporal/provenance graph; not pure vector memory.

## ADR-005 — Evidence ledger separate from memory
Remembered ≠ verified.

## ADR-006 — Explicit outer workflow, agentic inner work
Safety/compliance path is code-controlled; semantic subtasks can be model-controlled.

## ADR-007 — Skills are procedures
Skills cannot override global router/policy.
