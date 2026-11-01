# Remediation Backlog — after v0.7

## Resolved from v0.6

- ✅ Flat keyword router replaced by Domain × Procedure × Action/Risk routing.
- ✅ Risk-word mention no longer implies high-risk intent.
- ✅ Temporal memory now supports valid time, transaction time, supersedes and superseded_by.
- ✅ Frozen v0.6 routing corpus: 100%.
- ✅ Frozen risk-negative controls: 100%.
- ✅ Actual skill router entrypoint: 100%.
- ✅ Memory core + temporal evals: 100%.

## Remaining before v1.0

1. **Live Pydantic/provider compatibility** — adapter contract is not enough; run against pinned installed packages and intended providers.
2. **Live trajectory evals** — current T2 uses deterministic fixtures, not real agent traces.
3. **Real production shadow** — frozen shadow fixture is evaluator self-test only.
4. **Provider/model A/B** — compare candidate models using the same frozen task/evidence corpus.
5. **Reproducible release environment** — lockfile, dependency hashes, clean install, migration drill, crash/recovery drill.
6. **Operational SLOs** — latency, cost, retry/recovery, evidence coverage and context budgets need measured baselines.

Production promotion remains blocked until these are evidenced.
