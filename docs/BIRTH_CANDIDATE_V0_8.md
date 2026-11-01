# Birth Candidate v0.8

v0.8 turns the offline-correct harness into a release-candidate package that can collect the evidence required for production birth.

## Distinction

`artifact complete != production ready`

The package can be complete while production remains blocked by missing external evidence.

## Birth evidence classes

### A. Offline integrity
- package manifest and syntax
- full unit regression
- frozen eval corpus
- critical offline eval gates
- recovery drill
- migration/rollback drill
- failover-logic drill

### B. Runtime compatibility
- exact installed package versions
- live Pydantic import
- no-tool provider request
- timeout/budget behavior
- message-history serialization
- telemetry correlation

### C. Shadow evidence
- real read-only/shadow workload
- reference vs proposed action comparison
- zero high-risk false negatives as a hard invariant
- sample composition and exclusions disclosed

### D. Supply chain
- exact top-level runtime pins
- generated transitive lock with hashes
- build provenance
- container/non-root runtime

### E. Operational baseline
- latency/error/retry/cost observations
- configured SLOs based on actual measurements
- alerting and rollback ownership

## v0.8 status

The offline birth-candidate controls are executable. Live-provider, real-shadow, and transitive-lock evidence are intentionally not fabricated.
