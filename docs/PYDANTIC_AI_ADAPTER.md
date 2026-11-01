# Pydantic AI Adapter

## Validation status
The SasteraTech adapter implementation is contract-tested against the documented `Agent` / `UsageLimits` surface. The build environment could not install `pydantic-ai` or `pydantic-ai-harness` because outbound package resolution was unavailable, so live import/provider execution is **not claimed**.

## Mapping
| SasteraTech | Pydantic AI |
|---|---|
| model ID | `Agent(model)` |
| instructions | `Agent(..., instructions=...)` |
| model request budget | `UsageLimits(request_limit=...)` |
| tool-call budget | `UsageLimits(tool_calls_limit=...)` |
| total token budget | `UsageLimits(total_tokens_limit=...)` |
| per-request context | `UsageLimits(per_request_input_tokens_limit=...)` |
| wall time | `Agent.run(..., timeout=...)` |
| SasteraTech run ID | `Agent.run(..., run_id=...)` |
| output | `AgentRunResult.output` |
| usage | `AgentRunResult.usage` |
| resume material | `AgentRunResult.all_messages_json()` |

Pydantic Harness capabilities such as Planning, Memory, SubAgents, DynamicWorkflow, StepPersistence, guards and judges remain optional optimizations. SasteraTech PlanGraph, DelegationEngine, ContextAssembler, EventLog, approvals and evidence remain canonical.

Current StepPersistence documentation explicitly says it records snapshots/events/tool effects but does not automatically make replayed side effects safe and does not restore all application capability/graph state. SasteraTech reconciliation therefore remains mandatory.
