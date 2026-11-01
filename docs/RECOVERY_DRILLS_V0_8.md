# Recovery Drills v0.8

## Crash / uncertain-effect drill

The drill proves:
1. an R2 non-idempotent action requires approval;
2. the handler can create an external/local effect and then fail;
3. the effect ledger records `UNKNOWN`;
4. replay with the same idempotency key is blocked;
5. after reconciliation marks the effect verified, replay is **still blocked** for a non-idempotent action;
6. another execution requires a new action/idempotency identity.

This closes a v0.7 replay edge case.

## Migration / rollback drill

The drill:
1. creates a legacy schema database with data;
2. makes a byte-for-byte backup;
3. opens it through the current store and performs additive migration;
4. verifies legacy data survived;
5. restores the original backup;
6. verifies SHA-256 and SQLite integrity.

A real production migration still requires a copy of production-shaped data.
