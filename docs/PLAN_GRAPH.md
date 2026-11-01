# Plan Graph

Statuses: `PENDING`, `READY`, `RUNNING`, `BLOCKED`, `COMPLETE`, `FAILED`, `SKIPPED`.

Rules:
1. READY only when every dependency is COMPLETE.
2. RUNNING can become COMPLETE or FAILED.
3. Failed dependencies block downstream tasks.
4. Cycles are invalid.
5. Plan changes should be evented, not silently rewritten.
6. Readiness does not equal authorization; PolicyEngine remains authoritative.
