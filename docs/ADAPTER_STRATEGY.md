# Adapter Strategy

## Preferred: Pydantic AI / Harness
Target capabilities:
model loop, typed tools, planning, memory, skills, subagents, dynamic workflow,
context controls, guardrails, approval/tool judges, persistence/durability, OTel.

Harness 0.x evolution is isolated behind SasteraTech interfaces.

## Microsoft Agent Framework
Best alternate for explicit enterprise workflow graphs, HITL and checkpoints.

## Mastra
Best alternate for TypeScript products, observational memory and separated storage domains.

## LangGraph
Strong when explicit graph/state/interrupt-resume logic is the dominant problem.

## Vendor-native managed agents
Anthropic/OpenAI managed runtimes may be backends but do not define SasteraTech state, approval or evidence semantics.
