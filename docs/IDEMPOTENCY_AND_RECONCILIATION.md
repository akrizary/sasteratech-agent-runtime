# Idempotency and Reconciliation

## Effect states

- RESERVED
- STARTED
- SUCCEEDED
- VERIFIED
- FAILED
- UNKNOWN

## Replay rules

### Idempotent tool
Same idempotency key may return the prior verified/succeeded result instead of executing again.

### Non-idempotent tool
If a prior effect is `STARTED`, `SUCCEEDED`, or `UNKNOWN` and final state is uncertain, automatic replay is blocked.

## Crash window

A process can crash after external mutation but before recording success. Therefore absence of a success row is not evidence of no side effect.

Recovery:
1. locate effect record;
2. run tool-specific reconciliation/readback;
3. classify actual state;
4. mark VERIFIED / FAILED / UNKNOWN;
5. only then decide whether a retry is safe.

## Idempotency key

Key should represent the intended semantic effect, not a random retry attempt.
