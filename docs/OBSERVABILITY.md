# Observability

Event types:
run.started, route.selected, plan.updated, context.assembled,
model.requested, model.responded,
tool.requested, tool.blocked, tool.executed,
evidence.recorded, claim.updated,
approval.requested, approval.granted, approval.denied,
checkpoint.saved, memory.candidate, memory.promoted,
eval.completed, run.completed, run.failed.

Every event should carry run_id, step_id, parent span, timestamp, component, version and cost/tokens where applicable.

Prefer OpenTelemetry-compatible emission.

Metrics:
task success, routing accuracy, tool failure, approval escalation,
evidence coverage, unsupported-claim rate, context usage, cost,
latency, retries, recovery and memory correction rate.
