# Real Shadow and SLO Framework

## Real shadow

v0.9.2 input records are historical/reference-only. They require `id`,
`prompt`, `reference_actions`, `risks`, and historical `source` metadata; a
`proposed` field is rejected. The live no-tool model produces proposals at run
time, and the runner writes those separately with provenance hashes before
scoring. A provider/budget/parse failure is persisted as structured evidence
and fails coverage; it cannot be mistaken for a completed shadow run.

Input records contain:
- case ID
- reference actions
- proposed actions
- per-action risk
- source/workflow metadata

Metrics:
- precision
- recall
- F1
- exact action match
- high-risk false positives
- high-risk false negatives
- case count

**High-risk false negatives are a hard failure.**

## SLOs

v0.8 separates invariant limits from operational targets.

Hard invariants can be configured immediately, e.g.:
- unauthorized mutation count = 0
- high-risk false-negative count = 0

Latency, provider-error, retry and cost targets remain `null` until measured in the intended environment.
This prevents fabricated production SLOs.

For the v0.9.1 birth/smoke run, the configured acceptance limits are 20
samples, zero model-call failures, p95 latency at most 30 seconds, and mean
provider-reported cost per successful call at most USD 0.01. These are not
mature production SLOs; unavailable cost remains a blocker.
