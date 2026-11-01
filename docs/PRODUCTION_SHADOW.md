# Production Shadow Evaluation

A shadow evaluator compares *proposed* actions against a reference action set without executing the proposal.

Metrics:
- true positive / false positive / false negative;
- precision / recall / F1;
- exact action match rate;
- high-risk false-positive count;
- approval escalation delta.

v0.6 includes the evaluator and a synthetic fixture only.

**No real production shadow run has occurred.** Production shadow evidence must come from the target deployment environment before v1.0 readiness can be claimed.
