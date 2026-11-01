# SasteraTech Agent Runtime

SasteraTech Agent Runtime is an alpha-stage, provider-neutral Python runtime for
building auditable AI-agent workflows. It combines structured task contracts,
least-privilege tool policy, approval gates, durable state, evidence tracking,
evaluation fixtures, and local bring-your-own-key (BYOK) controls.

The repository is source code, not a hosted service. Provider calls remain
disabled unless an operator deliberately installs a provider adapter, enrolls
their own credential, and runs an explicitly networked command.

## What it provides

- a deterministic orchestration and policy core;
- provider adapters behind a framework-neutral boundary;
- local OS-keyring custody for BYOK credentials;
- loopback-only authenticated local API scaffolding;
- budget reservation, settlement, kill-switch and audit ledgers;
- prompt-injection, secret-boundary and tool-permission controls;
- frozen offline evaluation datasets and regression gates;
- live-provider validation scripts that remain opt-in; and
- recovery, evidence and release-gate utilities.

## Safety boundary

Model output is treated as a proposal. Runtime code validates schemas,
permissions, risk, budgets and approvals before any registered tool may run.
The current local API exposes no mutation tools and keeps provider dispatch
disabled. A green offline test run does not authorize production deployment.

## Quick start: offline core

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\verify_public_release.py
```

The core package has no mandatory third-party runtime dependency. Optional
provider, evaluation, telemetry and keyring integrations are declared in
`pyproject.toml`. The fully hashed compatibility environment is recorded in
`requirements/runtime-lock.txt`.

## Optional Pydantic AI runtime

```powershell
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements\runtime-lock.txt
```

Networked provider validation is intentionally separate from installation. Do
not put provider keys in repository files, command history, issue reports or
chat transcripts. See `docs/LOCAL_BYOK_RUNBOOK.md` and
`docs/LIVE_VALIDATION_PACK_V0_9.md` before enabling it.

## Local API

The Phase B-Lite API binds only to `127.0.0.1`. Its health endpoint is public
to the local machine; status and run-contract endpoints require a bearer token
stored in the OS credential manager. Provider dispatch and mutation tools are
disabled in this phase. See `docs/LOCAL_API_RUNBOOK.md`.

## Repository map

- `src/sasteratech_runtime/` — runtime, policy, storage and adapter code;
- `tests/` — offline unit and contract tests;
- `evals/` — synthetic evaluation datasets and thresholds;
- `schemas/` — JSON contracts for runtime objects;
- `scripts/` — verification, evidence and opt-in live-validation commands;
- `docs/` — architecture, threat model, runbooks and release gates;
- `requirements/` — direct pins and the hashed compatibility lock; and
- `sbom.cdx.json` / `THIRD_PARTY_NOTICES.md` — dependency disclosures.

Runtime-generated `state/`, `evidence/`, local configuration, databases,
virtual environments and evidence bundles are deliberately excluded from the
public source distribution.

## Status and support boundary

This is version `1.1.0a0` and should be treated as alpha software. Offline
tests and historical provider evidence establish bounded behavior only; they
do not prove universal provider compatibility, hosted-service security or
production readiness. Review `SECURITY.md` before use with sensitive data.

## Licence, copyright and brand

The source code is licensed under Apache License 2.0. See `LICENSE` and
`NOTICE`. Copyright 2026 Mohammad Akri bin Eddy Akhyar.

The licence covers copyright and applicable patent permissions; it does not
grant rights to present a fork or hosted service as the official SasteraTech
product. See `TRADEMARKS.md` for descriptive-use and fork-naming guidance.

Third-party packages retain their own licences. See
`THIRD_PARTY_NOTICES.md` and `sbom.cdx.json`.

## Contributing

Read `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` and
`PROVENANCE.md` before submitting a change. Contributions must not include
secrets, private evidence, copied third-party code without provenance, or
generated output whose redistribution rights are unclear.
