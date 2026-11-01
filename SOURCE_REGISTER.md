# Source Register — primary references

Snapshot date: 2026-10-29.

The system is an original synthesis; third-party source code is not copied.

## Pydantic
- https://pydantic.dev/docs/ai/harness/
- https://pydantic.dev/docs/ai/capabilities/overview/
Used for: composable capabilities, planning, memory, subagents, dynamic workflow, context controls, approvals/judges, trajectory controls, durability, OTel.

## Microsoft
- https://learn.microsoft.com/agent-framework/agents/harness
- https://learn.microsoft.com/en-us/agent-framework/journey/workflows
- https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
Used for: agent-vs-workflow boundary, orchestrations, HITL/checkpoints.

## Mastra
- https://mastra.ai/docs/storage
- https://mastra.ai/docs/memory/overview
- https://mastra.ai/research/observational-memory
- https://mastra.ai/docs/observability/overview
Used for: storage-domain separation, observational memory, isolated subagent memory, observability/evals.

## Google
- https://google.github.io/skill-reach/
- https://google.github.io/skill-reach/api/metrics/
Used for: routing collision/eval metrics.

## Letta
- https://docs.letta.com/configuration/memory
- https://docs.letta.com/concepts/stateful-agents
Used for: durable memory and background consolidation ideas.

## OpenAI
- https://openai.github.io/openai-agents-python/
- https://openai.github.io/openai-agents-python/tracing/
Used for: lean runtime, sessions/HITL, tracing.

## Anthropic
- https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration
Used for: isolated subagents and dynamic orchestration patterns.

## Agent Skills
- https://github.com/addyosmani/agent-skills
Used for: skill/routing methodology and eval structure.

## Superpowers
- https://github.com/obra/superpowers
- https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md
- https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md
Used for: root-cause debugging and evidence-before-completion discipline.

## Freshness warning
Recheck official docs before binding production adapters because agent frameworks evolve rapidly.


## v0.4 API verification — 2026-10-29
- https://pydantic.dev/docs/ai/core-concepts/agent/
- https://pydantic.dev/docs/ai/api/pydantic-ai/usage/
- https://pydantic.dev/docs/ai/core-concepts/timeouts/
- https://pydantic.dev/docs/ai/core-concepts/message-history/
- https://pydantic.dev/docs/ai/models/overview/
- https://pydantic.dev/docs/ai/harness/
- https://pydantic.dev/docs/ai/harness/subagents/
- https://pydantic.dev/docs/ai/harness/dynamic-workflow/
- https://pydantic.dev/docs/ai/harness/step-persistence/
- https://pydantic.dev/docs/ai/harness/trajectory-judge/


## v0.5 security verification — 2026-10-29
- Pydantic Tool Call Judge: https://pydantic.dev/docs/ai/harness/tool-call-judge/
- Pydantic Approval Reviewer: https://pydantic.dev/docs/ai/harness/approval-reviewer/
- Pydantic AI Harness capabilities: https://pydantic.dev/docs/ai/harness/
- OpenAI Agents SDK guardrails: https://openai.github.io/openai-agents-python/guardrails/

Architecture consequence: model judges are advisory/narrowing controls, not security boundaries. SasteraTech retains deterministic authorization, least privilege, argument validation, human approval for R2+, and post-action verification.


## v0.6 evaluation references — 2026-10-29
- Google skill-reach metrics: https://google.github.io/skill-reach/api/metrics/
- Google skill-reach reachability: https://google.github.io/skill-reach/concepts/how-it-works/
- Pydantic Evals: https://pydantic.dev/docs/ai/evals/evals/
- Pydantic span-based evaluation: https://pydantic.dev/docs/ai/evals/evaluators/span-based/
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/
- OpenAI Agents SDK guardrails: https://openai.github.io/openai-agents-python/guardrails/

SasteraTech uses analogous metric concepts while keeping the executable offline core dependency-free.


## v0.8 release-preparation verification — 2026-10-29
- PyPI `pydantic-ai`: current release history shows 2.63.0 released 2026-10-28.
- PyPI `pydantic-ai-harness`: current release history shows 0.63.0 released 2026-10-28.
- Pydantic AI installation: https://pydantic.dev/docs/ai/overview/install/
- Pydantic durable execution overview: https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/
- Pydantic AI Harness overview: https://pydantic.dev/docs/ai/harness/

Top-level versions are pinned for compatibility testing, but a transitive hashed lock must still be generated in a network-enabled environment.


## v0.9 current verification — 2026-10-30
- PyPI release history confirms `pydantic-ai 2.63.0` released 2026-10-28.
- PyPI release history confirms `pydantic-ai-harness 0.63.0` released 2026-10-28.
- Pydantic Harness docs continue to state that Harness 0.x APIs may change between minor releases.
- Step Persistence persists run snapshots/events/tool-effect ledgers but does not by itself make side-effect replay safe; SasteraTech reconciliation remains authoritative.
