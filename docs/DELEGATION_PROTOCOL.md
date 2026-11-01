# Delegation Protocol

## Delegation packet

Every child receives an immutable TaskPacket containing:
- packet_id
- parent_packet_id
- run_id
- task_id
- objective
- task class
- assigned role
- constraints
- evidence refs
- requested tool IDs
- risk ceiling
- output contract
- budgets
- current delegation depth

## Narrowing invariant

A child packet must not exceed the parent in:
- risk ceiling;
- tool scope;
- time/token/tool-call budget;
- resource scope.

## Independence

For claims marked `independent_verification_required`, the verifier worker ID must differ from the producer worker ID. Role difference alone is insufficient when the same underlying worker/session produced both outputs.

## Failure behavior

Invalid delegation is rejected before any runtime/model call.
