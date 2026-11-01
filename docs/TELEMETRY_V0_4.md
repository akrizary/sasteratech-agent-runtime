# Telemetry v0.4
Telemetry is observational, not authoritative.

Sinks: Null, InMemory, JSONL, Composite and optional OpenTelemetry.

Before emission, keys containing api_key, authorization, bearer, password, secret or token are redacted recursively.

EventLog remains durable application audit state. Losing telemetry must not erase what SasteraTech knows happened.
