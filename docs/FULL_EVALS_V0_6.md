# Full Evals v0.6

## Objective

Turn SasteraTech Runtime from an architecture that *claims* reliability into a system that can measure where reliability exists, where it regresses, and where it is still unproven.

## Evaluation tiers

| Tier | Scope | v0.6 mode |
|---|---|---|
| T0 | Structural/package contracts | executable/offline |
| T1 | Routing + skill reachability/collisions | executable/offline |
| T2 | Behavioral/trajectory contracts | executable trace evaluator; live-agent trajectory pending |
| T3 | Adversarial/abuse resistance | executable/offline core scenarios |
| T4 | Regression against baselines | executable/offline |
| T5 | Long-horizon/memory coherence | capability probes + deterministic scenarios |
| T6 | Safety/approval/effect controls | executable/offline core scenarios |
| T7 | Production shadow | shadow engine + fixture; real production shadow not run |

## Doctrine

1. A passing final answer does not imply a passing trajectory.
2. Deterministic evaluators are preferred where the property is deterministic.
3. LLM judges may supplement subjective evaluation but never replace security invariants.
4. Evals need negative controls, not only happy paths.
5. Model/provider upgrades are code changes: rerun frozen corpora.
6. One aggregate score is insufficient; safety, routing, evidence and coherence remain separate dimensions.
7. Missing capability is a valid eval result. Do not manufacture a pass.

## Current production-readiness rule

`v1.0 READY` requires all CRITICAL gates to pass and all live-required gates to have real evidence. A scaffold/fixture pass is not equivalent to a production-shadow pass.
