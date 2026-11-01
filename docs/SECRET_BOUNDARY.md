# Secret Boundary

## Rules

1. Credentials belong in secret providers/environment, not task packets or persistent prompts.
2. Logs, events and telemetry redact secret-like keys and credential patterns.
3. Network tools reject arguments containing detected credentials unless the runtime spec explicitly allows secret transmission.
4. Secret-bearing tool results should be transformed to references/handles where possible.
5. Model context should receive the minimum secret-derived information required for the task.

## Detection

v0.5 includes conservative detection for common:
- authorization/bearer headers
- API key/token/password fields
- private key blocks
- credential-looking environment assignments

Detection is not exhaustive. It supplements, not replaces, provider secret stores and sandboxing.
