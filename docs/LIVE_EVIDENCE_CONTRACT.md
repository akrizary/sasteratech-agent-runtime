# Live Evidence Contract

Every live evidence JSON record should contain, directly or through the run manifest:

- `artifact_version`
- `artifact_manifest_sha256`
- `runtime_lock_sha256` when a lock exists
- UTC timestamp
- Python version
- platform metadata
- exact `pydantic-ai` and `pydantic-ai-harness` versions
- model identifier used
- mutation-tools-exposed flag
- result status
- bounded usage/latency where available

For a v1.0.0 real-shadow run, the evidence must additionally show that the
input schema excluded pre-written proposals, the no-tool model generated the
proposals, and the result is tied to an input and model-output hash.

## Secrets

Evidence must never store credential values.

Environment capture records only booleans such as:

```json
{"OPENAI_API_KEY_present": true}
```

not the key itself.

## Attestation level

v0.9 uses **self-attestation by artifact hashes**, not cryptographic identity attestation.

A malicious/compromised machine can fabricate evidence. For higher assurance, future deployment may add:
- CI signed provenance;
- OIDC workload identity;
- Sigstore attestations;
- WORM evidence storage.

## Import rule

Evidence generated from a different artifact manifest is rejected by default.

Missing cost evidence is not zero cost. The approved smoke cost gate remains
blocked unless usable provider-reported cost evidence is present.

`LIVE_ATTESTATION.json` is packaged beside the evidence records but is excluded
from its own `files` map. This prevents a prior attestation from being hashed
and then overwritten during a later export.

## Canonical-artifact integrity check

Before evidence export, v0.9 re-hashes every file listed in `MANIFEST.sha256`.
If any canonical file is missing or changed, export is rejected. Each live run writes
to `evidence/live_runs/<run_id>/` exactly once. Its `RUN_MANIFEST.json` records the
single attempt, step outcomes, and no-retry status. Export requires that named complete
run. Import verifies it and records the selected run; the v1 evaluator reads only that
imported run, never mutable local live output.
