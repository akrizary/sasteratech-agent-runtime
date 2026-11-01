# Live Validation Pack v0.9

## Objective

Turn the offline Birth Candidate into a reproducible evidence-collection pack that can be run on a clean machine or cloud runner with network access and provider credentials.

v0.9 does **not** declare production readiness. It creates the machinery to prove or disprove it.

## Evidence chain

```text
canonical v0.9 artifact
        |
        +-- MANIFEST.sha256
        |
        v
clean runtime environment
        |
        +-- exact package versions
        +-- runtime lock hash
        +-- Python / OS metadata
        +-- provider model identifiers
        +-- credential-presence booleans only
        |
        v
live probes
        +-- runtime import
        +-- provider compatibility
        +-- policy trajectory cases
        +-- provider matrix
        +-- controlled failover
        +-- operational baseline
        +-- real shadow dataset (optional until supplied)
        |
        v
LIVE_EVIDENCE_BUNDLE.zip
        |
        v
return bundle to this project
        |
        v
integrity review + v1 gate evaluator
```

No v1.0 artifact may be produced until that returned bundle is accepted by the
v1 gate evaluator. Producing the ZIP in another environment alone does not
complete the evidence loop.

## Safety boundary

All built-in live probes are **no-tool model calls**. They do not expose file-write, shell, deployment, email, payment, or external mutation tools to the model.

## Truth boundary

- A successful import proves package compatibility, not agent quality.
- A successful provider probe proves a minimal model call, not production reliability.
- A trajectory pass proves the small frozen live policy corpus, not arbitrary reasoning ability.
- SLO samples are observations; thresholds must be explicitly configured.
- Shadow quality is only meaningful against a representative real dataset.

## Local configuration

Before SLO evaluation, copy `config/live_validation.example.json` to
`config/live_validation.local.json` and set project-specific thresholds.
The local file is intentionally not part of the canonical manifest.

For v0.9.2, this local policy and a hashed runtime lock are mandatory
preconditions. The live-pack runner exits before provider calls when either is
missing.

## Canonical command sequence

Linux/macOS:

```bash
./scripts/bootstrap_live_env.sh
source .venv/bin/activate
python scripts/capture_live_environment.py
SASTERATECH_PROBE_MODEL='provider:model' python scripts/probe_live_provider.py
SASTERATECH_PROBE_MODEL='provider:model' python scripts/run_live_trajectory_eval.py
python scripts/run_provider_matrix.py --model primary='provider:model'
python scripts/run_operational_baseline.py --model 'provider:model' --samples 20
python scripts/export_live_evidence.py
python scripts/evaluate_v1_gate.py
```

## Return and assess the evidence bundle

Copy the generated `LIVE_EVIDENCE_BUNDLE.zip` back to the canonical project
workspace. From the project root, import it without the manifest-bypass flag:

```bash
python scripts/import_live_evidence.py /path/to/LIVE_EVIDENCE_BUNDLE.zip
python scripts/evaluate_v1_gate.py
```

The importer rejects evidence produced by a different canonical manifest by
default. Do not use `--allow-manifest-mismatch` to satisfy the v1.0 gate.

Windows PowerShell:

```powershell
.\scripts\bootstrap_live_env.ps1
.\.venv\Scripts\Activate.ps1
Copy-Item config\live_validation.example.json config\live_validation.local.json
python scripts\capture_live_environment.py
$env:SASTERATECH_PROBE_MODEL='provider:model'
python scripts\probe_live_provider.py
python scripts\run_live_trajectory_eval.py
python scripts\run_provider_matrix.py --model primary='provider:model'
python scripts\run_operational_baseline.py --model 'provider:model' --samples 20
python scripts\export_live_evidence.py
python scripts\evaluate_v1_gate.py
```
