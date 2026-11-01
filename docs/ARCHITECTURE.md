# Architecture

## Nervous system
The Orchestrator coordinates explicit services:
1. IntakeService
2. Router
3. PlanStore
4. PolicyEngine
5. ContextAssembler
6. Executor
7. ToolRegistry
8. EvidenceLedger
9. VerificationService
10. MemoryService
11. CheckpointStore
12. EvaluationService
13. TelemetrySink

## Control loop

```text
observe state
→ select workflow step
→ assemble bounded context
→ invoke model only where judgement is needed
→ policy-check intended action
→ execute permitted action
→ capture evidence
→ verify expected effect
→ checkpoint
→ update plan
```

## Agent vs workflow
Use model-decided orchestration for open semantic decomposition.
Use developer-defined workflow when sequence, safety, retries or compliance matter.
Production default: **explicit outer workflow + agentic inner steps**.

## Context firewall
Subagent packet:
- objective
- constraints
- permitted tools
- evidence bundle
- output schema
- budget
- delegation depth
- escalation rule

## Multi-agent patterns
Allowed:
- independent fan-out/fan-in;
- sequential specialists;
- explicit handoff;
- independent verifier.

Avoid:
- unbounded swarms;
- shared mutable context between independent workers;
- recursive delegation without depth/budget;
- consensus where all workers share the same unverified source.
