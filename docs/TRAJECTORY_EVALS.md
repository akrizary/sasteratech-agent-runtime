# Trajectory Evals

## Why

Agent output can be correct by accident. For BUILD/DEBUG/CONTROL work, process matters.

## Trace assertions

Supported deterministic assertions:
- required event subsequence;
- forbidden events;
- maximum occurrences;
- must precede / must follow;
- terminal event requirement.

Examples:
- DEBUG: `reproduce -> diagnose -> patch -> regression`
- gated mutation: `approval.granted -> tool.executed -> verification`
- model run: `model.requested -> model.responded`

## Live model evaluation

v0.6 provides the evaluator and fixtures. Live Pydantic/provider trajectories remain a separate compatibility/experiment run because the build environment has no live provider execution evidence.
