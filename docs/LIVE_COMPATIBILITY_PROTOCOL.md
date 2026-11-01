# Live Compatibility Protocol

Run only in an isolated environment with explicit credentials.

1. Generate/install `runtime-lock.txt`.
2. Run `python scripts/probe_runtime_import.py`.
3. Set `SASTERATECH_PROBE_MODEL` to the tested model identifier.
4. Configure the provider credential through its normal environment/secret mechanism.
5. Run `python scripts/probe_live_provider.py`.
6. Run a second probe configured to exceed a small request/token budget and verify fail-closed behavior.
7. Capture package versions, model identifier, usage, runtime IDs and message-history serialization.
8. Do not store API keys or raw authorization headers in evidence files.

The probe is reasoning-only and exposes no mutation tools.
