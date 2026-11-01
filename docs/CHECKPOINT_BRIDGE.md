# Checkpoint Bridge

An SasteraTech checkpoint stores run ID, monotonic sequence, state JSON, optional runtime reference, stability flag and metadata.

`stable=true` means the application-level snapshot is internally coherent; it does not prove an external side effect succeeded.

Recovery order:
1. load latest stable SasteraTech checkpoint;
2. inspect runtime/tool-effect persistence;
3. reconcile uncertain external effects;
4. resume only after policy decides replay safety.
