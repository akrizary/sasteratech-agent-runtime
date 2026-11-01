# Production Release Gates

## Gate groups

### OFFLINE_CORE
Must pass:
- unit tests
- package validator
- frozen corpus integrity
- critical offline eval gate
- crash/recovery drill
- migration/rollback drill
- deterministic failover logic

### LIVE_RUNTIME
Must pass in the target runtime environment:
- exact Pydantic runtime import
- one no-tool live request per intended provider class
- timeout/request/token limit behavior
- message-history serialization
- telemetry correlation

### REAL_SHADOW
Must use real workload in read-only/shadow mode.
Hard invariant: **zero high-risk false negatives**.
Other acceptance thresholds are configured from observed baselines; v0.8 does not invent universal latency/cost targets.

### SUPPLY_CHAIN
Must include:
- exact top-level pins
- transitive dependency lock
- hashes/provenance
- reproducible container build

### OPERATIONS
Must include:
- backup/restore owner
- rollback procedure
- incident owner
- monitoring/SLOs configured from measured data

## Decision

Production authorization is a human release decision backed by machine evidence.
The ReleaseGate can block automatically but cannot self-authorize deployment.
