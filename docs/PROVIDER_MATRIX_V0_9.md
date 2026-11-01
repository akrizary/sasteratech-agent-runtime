# Provider Matrix v0.9

Provider/model testing is configured at runtime with repeated CLI arguments:

```bash
python scripts/run_provider_matrix.py \
  --model openai='openai:<model>' \
  --model anthropic='anthropic:<model>' \
  --model google='google:<model>'
```

The script performs safe no-tool compatibility probes and records per-model:
- status;
- latency;
- exact-match probe result;
- token usage when exposed;
- serialized message availability;
- error type.

No provider is assumed to be best from brand alone. Production selection should use measured task-specific evidence.
