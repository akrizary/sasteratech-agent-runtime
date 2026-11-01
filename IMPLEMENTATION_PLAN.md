# SasteraTech-SEEDFORGE Implementation Plan

## DNA — COMPLETE
Genome, invariants, risk/state, evidence/memory, adapter boundary.

## Zygote — INCLUDED
Deterministic core proving routing, state transitions, policy, evidence, memory promotion and tool registry.

## Cells — v0.2 — COMPLETE
Implemented SQLite persistence, RunRepository, PlanGraph, ContextAssembler, hash-chained EventLog, ArtifactRegistry, ConfigLoader and regression tests. Postgres remains a future storage adapter.

## Agents / Organs — v0.3 — COMPLETE
Implemented machine-readable capability profiles and deterministic contracts for Researcher, Builder, Debugger, Reviewer, Verifier, Risk Guardian, Memory Curator, Synthesizer and Domain Specialist; added task packets, action intents, delegation narrowing, independence checks and organ routing.

## Nervous System — v0.4 — COMPLETE AT SasteraTech BOUNDARY
Implemented:
- model/provider profile registry
- runtime adapter registry
- Pydantic AI adapter with lazy dependency loading
- deterministic mock runtime
- request/token/time/cost budget mapping
- ContextAssembler integration
- validated delegation and bounded fan-out
- runtime-call persistence
- framework-neutral SasteraTech checkpoints
- telemetry and OpenTelemetry sink
- adapter contract tests

Live Pydantic/provider execution is NOT claimed because package installation/network access was unavailable in the build environment. Production binding requires an exact-version compatibility run.

## Immune System — v0.5
Policy enforcement, approval service, prompt-injection defense, tool-call risk judge, contradiction scanner, budgets, secret handling.

## Evals — v0.6
T0–T7 corpus and model/provider comparison.

## Birth — v1.0
Criteria:
- critical T0/T6 100%;
- no unauthorized R2+ in adversarial suite;
- durable recovery drill passes;
- audit log complete;
- rollback tested;
- provider failover tested.

## Growth
Eval-driven tuning, memory correction metrics, routing optimization, cost/latency optimization and adapter upgrades behind compatibility tests.


## Evals — v0.6 — COMPLETE AS EVALUATION INFRASTRUCTURE
See docs/FULL_EVALS_V0_6.md.


## Eval-Driven Rectification — v0.7 — IMPLEMENTED
- multi-axis router
- intent-based risk classification
- temporal memory v2
- actual skill router evaluation
- frozen-corpus integrity enforcement
- rerun v0.6 corpus unchanged

Next birth-preparation work is determined by the v0.7 scorecard, live adapter compatibility and real shadow evidence.


## Birth Candidate / Production Hardening — v0.8 — IMPLEMENTED
- exact verified top-level Pydantic runtime pins
- lockfile generator and fail-closed lock gate
- non-root container recipe requiring hashed lock
- runtime import and live-provider probe scripts
- release evidence/gate model
- crash/recovery drill
- migration/rollback drill
- non-idempotent verified replay hardening
- deterministic provider failover logic
- real shadow evaluator with high-risk false-negative detection
- SLO framework that refuses fabricated operational targets

Production remains blocked until the external/live evidence gates pass.


## Live Validation Pack — v0.9 — COMPLETE
- isolated environment bootstrap scripts
- live environment evidence capture
- safe provider probe
- frozen live trajectory policy suite
- provider matrix runner
- controlled live failover runner
- operational baseline collection
- real-shadow integration
- evidence export/import with manifest/hash validation
- v1 evidence gate evaluator

No production deployment is authorized by v0.9.
