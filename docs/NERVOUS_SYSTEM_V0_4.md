# Nervous System v0.4

## Purpose
Connect the deterministic SasteraTech core to model runtimes without allowing the runtime to become the source of authority.

v0.4 implements model profiles, runtime adapters, runtime request/response contracts, a reasoning-only Pydantic AI adapter, mock runtime tests, bounded context, validated delegation, bounded fan-out, runtime-call persistence, SasteraTech checkpoints, and telemetry.

## Critical boundary
**No mutation tool bridge is enabled in v0.4.**

A model can reason and return results, but write/deploy/send/payment side effects remain outside the model runtime until Immune System v0.5 connects them through:

`ActionIntent -> CapabilityGuard -> PolicyEngine -> ApprovalGrant -> Executor -> Verification`.

## Runtime flow
```text
TaskPacket -> Worker validation -> ModelRegistry -> ContextAssembler -> RuntimeRequest
    -> RuntimeRegistry -> Adapter -> RuntimeResponse
    -> runtime_calls + EventLog + Checkpoint + Telemetry
    -> UNVERIFIED MODEL OUTPUT
```

SasteraTech owns role assignment, delegation permission, budgets, risk ceilings, resource scopes, plan dependencies, context policy, and verification independence.
