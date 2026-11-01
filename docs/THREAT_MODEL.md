# Threat Model

Threats:
1. prompt injection from web/files/tools
2. tool overreach
3. approval confusion
4. memory poisoning
5. stale-state replay
6. duplicate mutation
7. secret leakage
8. context drift
9. agent privilege escalation
10. false completion
11. correlated multi-agent hallucination
12. provider behavior change

Controls:
untrusted-data labeling, policy isolation, least privilege, immutable approvals,
memory promotion gate, idempotency/reconciliation, secret redaction,
state re-injection, independent verification, regression tests, adapter boundary.

A second LLM is not a security boundary.
