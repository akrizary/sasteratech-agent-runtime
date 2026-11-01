# SasteraTech Agent Runtime v0.9.1 — START HERE

**Artifact type:** portable canonical handoff ZIP  
**Status:** DNA + ZYGOTE + CELLS + AGENTS/ORGANS + NERVOUS SYSTEM CORE VALIDATED  
**Default operational state:** `STATE_0_READ_ONLY_AUDIT`  
**Generated:** 2026-10-30

SasteraTech Agent Runtime is a model-agnostic agent operating architecture for long-horizon work. It is designed to make the *system* reliable rather than assuming the model is reliable.

## Prime directive

> Model intelligence is a component. Reliability comes from routing, state, evidence, policy, memory governance, bounded tools, durable execution, and repeatable evaluation.

## Start in this order

1. `README.md`
2. `SYSTEM_GENOME.md`
3. `docs/ARCHITECTURE.md`
4. `docs/POLICY_AND_APPROVAL.md`
5. `docs/MEMORY_AND_PROVENANCE.md`
6. `docs/EVIDENCE_LEDGER.md`
7. `docs/EVAL_SYSTEM.md`
8. `IMPLEMENTATION_PLAN.md`

## Included

- Complete architecture and system genome
- Risk/approval state machine
- Task-conditioned reasoning router
- Evidence ledger and truth-status model
- Hybrid long-term memory architecture
- Provenance and canonical-memory promotion rules
- Context firewall and subagent isolation model
- Tool registry contract
- Durable execution/checkpoint model
- Observability/event schema
- Multi-tier eval framework
- Portable skill contract + examples
- Deterministic Python zygote scaffold (standard library only)
- Unit tests and artifact validator
- Runtime-adapter boundary for Pydantic AI / Microsoft Agent Framework / Mastra / LangGraph
- v0.4 runtime registry, model profiles, checkpoints, telemetry and reasoning-only Pydantic adapter
- Official source register and decision log
- v0.9.1 DeepSeek presence-only evidence and live real-shadow provenance gate

## Deliberate non-goals of v0.4

This artifact does **not**:
- grant itself external write access;
- deploy anything;
- auto-authorize destructive actions;
- hard-code one model/provider;
- treat retrieved memory as truth;
- treat an LLM judge as an approval authority;
- copy third-party framework source code.

## Validation

```bash
python scripts/validate_package.py
python -m unittest discover -s tests -v
```

The scaffold works without external packages.

## Canonical precedence

`P0 safety/policy > P1 observable evidence > P2 explicit scoped approval > P3 workflow plan > P4 style/convenience`
