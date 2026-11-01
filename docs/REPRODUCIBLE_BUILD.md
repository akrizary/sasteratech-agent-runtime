# Reproducible Build

## Verified current top-level targets (2026-10-29)

The release-preparation pins target:
- `pydantic-ai==2.63.0`
- `pydantic-ai-harness==0.63.0`

These versions were verified against current PyPI release history on 2026-10-29.

## Important distinction

`runtime-pins.in` is **not** a full lockfile.
A production lock must resolve the complete dependency graph and include hashes.

Generate it in a network-enabled clean environment:

```bash
python scripts/generate_runtime_lock.py
```

The script uses:

```bash
uv pip compile requirements/runtime-pins.in --generate-hashes -o requirements/runtime-lock.txt
```

Production gate fails closed when `runtime-lock.txt` is absent or does not contain hashes.

## Container

`container/Dockerfile` refuses to install from floating dependencies; it expects the generated lockfile.
The service runs as a non-root user.
