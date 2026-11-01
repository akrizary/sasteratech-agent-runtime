# SasteraTech Agent Runtime — System Genome (DNA)

## 0. Identity
**System:** SasteraTech Agent Runtime  
**Version:** 0.9  
**Class:** Model-agnostic agent operating harness  
**Default:** read-only audit  
**Design target:** long-horizon, multi-domain, evidence-gated autonomous work

## 1. Prime law stack
### P0 — Safety and authority
Hard policy, tool boundaries, secrets, explicit approvals, irreversible actions.

### P1 — Truth and evidence
Observable evidence, source provenance, uncertainty, claim verification.

### P2 — User agency
Scoped approval, reversible planning, preview-before-mutation.

### P3 — Utility
Correct routing, efficient execution, durable state, artifact production.

### P4 — Presentation
Style, formatting, convenience.

Lower priority may never override higher priority.

## 2. Domains
- **FACT:** real-world claims; sourced/calculated/observed or marked provisional/unknown.
- **CREATIVE:** imagination allowed; internal canon is a constraint system.
- **CONTROL:** actions that mutate state; always risk-classified.
- **MIXED:** split into domain-specific subproblems.

## 3. Task classes
`FACT_QUERY`, `RESEARCH`, `BUILD`, `DEBUG`, `REVIEW`, `DATA`, `FILE`, `MIGRATION`, `OPERATIONS`, `CREATIVE`, `HIGH_RISK`.

## 4. Reasoning policies

| Task | Default procedure |
|---|---|
| FACT_QUERY | retrieve → verify → answer |
| RESEARCH | decompose → source → triangulate → contradiction scan → synthesize |
| BUILD | spec → plan → implement → test → verify |
| DEBUG | reproduce → isolate → hypothesis → discriminate → patch → regression |
| REVIEW | criteria → inspect → adversarial checks → evidence → verdict |
| DATA | inspect → profile → transform → invariants → reconcile |
| FILE | inventory → plan → preview → approve → mutate → integrity check |
| MIGRATION | inventory → mapping → dry-run → backup → gated mutation → reconcile |
| OPERATIONS | state read → desired state → delta → risk gate → execute → verify |
| CREATIVE | canon retrieval → constraints → generation → continuity/payoff pass |
| HIGH_RISK | deterministic policy → restricted tools → explicit approval → two-party verification |

## 5. State model
- STATE_0_READ_ONLY_AUDIT
- STATE_1_PLAN_READY
- STATE_2_PATCH_PREPARED
- STATE_3_LOCAL_MUTATION_AUTHORIZED
- STATE_4_EXTERNAL_MUTATION_AUTHORIZED
- STATE_5_DEPLOY_AUTHORIZED
- STATE_6_POST_MUTATION_VERIFY
- STATE_7_COMPLETE
- STATE_X_BLOCKED
- STATE_X_RECOVERY

Conversational assent does not advance state unless a scoped ApprovalGrant matches the action.

## 6. Risk model

| Risk | Meaning | Default |
|---|---|---|
| R0 | read-only / observation | auto |
| R1 | reversible ephemeral/local | policy controlled |
| R2 | durable local/repo mutation | explicit scoped approval |
| R3 | external state mutation | explicit exact approval |
| R4 | destructive, production, secrets, money, identity/security | exact approval + additional checks |

LLM judges may block or escalate; they never create R2+ authority.

## 7. Evidence model
Truth status:
`VERIFIED`, `SUPPORTED`, `PROVISIONAL`, `INTERPRETATION`, `UNKNOWN`, `CONTRADICTED`.

## 8. Memory model
1. immutable event log
2. working memory
3. retrieval indexes
4. observational memory
5. candidate durable memory
6. evidence/provenance gate
7. canonical memory

Retrieved text is never silently promoted to canonical truth.

## 9. Context model
Priority:
1. policies/constraints
2. current plan/state
3. active evidence
4. canonical memory
5. retrieved material
6. recent conversation
7. optional background

Subagents receive explicit task packets, not inherited parent history by default.

## 10. Agent roles
Orchestrator, Researcher, Builder, Debugger, Reviewer, Verifier, Risk Guardian, Memory Curator, Synthesizer, Domain Specialist.

Roles are invoked only when needed.

## 11. Tool contract
Every tool declares schema, risk, side effects, idempotency, reversibility, secrets/network access, approval rule, dry-run support, evidence emitted, timeout/retry policy.

## 12. Long-run durability
Persist run manifest, plan graph, transitions, tool intents/results, approval grants, evidence ledger, checkpoints, artifact hashes, memory candidates and eval results.

## 13. Completion contract
Complete only when requested outputs exist, critical invariants pass, fresh evidence supports completion, unresolved failures are disclosed, and post-mutation reconciliation is complete where applicable.

## 14. Evolution rule
Every architecture change must state:
1. failure mode solved;
2. new failure mode introduced;
3. evaluation method;
4. rollback path.
