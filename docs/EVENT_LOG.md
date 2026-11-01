# Event Log

Append-only records contain event_id, run_id, sequence, timestamp, type, payload, previous_hash, event_hash. The previous hash is part of each record hash, forming a per-run tamper-evident chain.

This is tamper-evident, not tamper-proof. Production hardening can add remote append-only storage, signatures, WORM/object-lock or transparency logs.
