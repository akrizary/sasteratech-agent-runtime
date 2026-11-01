# Cells v0.2

This milestone converts the v0.1 deterministic zygote into a persistent, resumable local core.

## Implemented cells

1. **SQLiteStore** — WAL, foreign keys, migrations, transactions.
2. **RunRepository** — persistent run/state records.
3. **PlanGraph** — dependency-aware tasks, cycle detection, readiness/blocking.
4. **ContextAssembler** — bounded required/optional context with overflow reporting.
5. **EventLog** — append-only per-run sequence with SHA-256 hash chaining.
6. **ArtifactRegistry** — SHA-256, size, lineage, canonical/supersession metadata.
7. **ConfigLoader** — JSON config plus deterministic environment overrides.

All v0.2 modules remain model-independent and network-independent.

`conversation text != system state`
