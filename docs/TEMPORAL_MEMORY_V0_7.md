# Temporal Memory v0.7

SasteraTech uses bitemporal-style metadata:

- **valid time**: when the proposition is true in the represented world (`valid_from`, `valid_to`);
- **transaction time**: when SasteraTech recorded the memory (`transaction_time`).

Supersession is explicit and does not erase history.

Example:

```text
A: manager=Alice valid 2025-01-01 → 2026-01-01
B: manager=Bob   valid 2026-01-01 → open
B supersedes A
```

Querying 2025 returns A; querying 2026 returns B.

This prevents a common long-term-memory error: treating the newest observation as if it had always been true.
