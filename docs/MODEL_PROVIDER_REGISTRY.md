# Model Provider Registry

Models are referenced by stable SasteraTech aliases rather than scattering provider strings through the system.

A profile contains alias, adapter ID, literal or environment-resolved model ID, allowed roles, enabled state, and advisory metadata.

Rules:
1. Secrets never live in model profiles.
2. Role permission is checked before model selection.
3. Model fallback cannot change risk/tool permissions.
4. Provider/model identity is routing data, not authority.
5. Production must pin tested framework/model combinations in a lockfile and compatibility matrix.

Pydantic AI currently documents provider prefixes including OpenAI, Anthropic, Google, OpenRouter, Azure/Foundry, Bedrock, vLLM and others. SasteraTech deliberately keeps the registry open-ended.
