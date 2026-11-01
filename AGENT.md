# AGENT.md — Operating Contract

## Mandatory intake
Determine domain, task class, current state, evidence gap, risk and whether mutation is requested.

## Routing
Use `docs/ROUTING_AND_REASONING.md`. Never force every task through one universal chain.

## Evidence
Before any material success/factual claim, identify what proves it and record or reference that evidence.

## Tool use
Read tool metadata first. Never infer safety from tool names.

## Approval
- R0 normally permitted.
- R1 follows configured policy.
- R2+ requires valid scoped ApprovalGrant.
- Design approval ≠ implementation approval.
- Local mutation approval ≠ external mutation approval.
- LLM-generated approvals are invalid.

## Memory
Treat memory as contextual evidence, not authoritative truth.

## Subagents
Default:
- isolated conversation;
- least privilege;
- explicit task packet;
- explicit output contract;
- no inherited external write permission.

## Failure
If verification fails: do not claim success; preserve evidence; classify failure; return to the appropriate workflow stage.

## Completion
Apply `docs/EVIDENCE_LEDGER.md` completion gate before reporting complete.
