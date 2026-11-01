import hashlib, json, os, platform, sys, time
from dataclasses import dataclass
from pathlib import Path

SECRET_ENV_NAMES = (
    'OPENAI_API_KEY','ANTHROPIC_API_KEY','GOOGLE_API_KEY','GEMINI_API_KEY',
    'OPENROUTER_API_KEY','DEEPSEEK_API_KEY','AZURE_OPENAI_API_KEY','AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY'
)
ARTIFACT_VERSION = '1.1.0a0'

def live_run_directory(root, run_id=None):
    """Return a new immutable live-evidence directory for one validation run."""
    root = Path(root)
    name = run_id or os.getenv('SASTERATECH_LIVE_RUN_ID')
    if not name:
        raise ValueError('SASTERATECH_LIVE_RUN_ID is required for live evidence output')
    if not name.replace('-', '').replace('_', '').isalnum() or '/' in name or '\\' in name:
        raise ValueError('invalid live run id')
    return root / 'evidence' / 'live_runs' / name

def live_run_manifest_path(root, run_id=None):
    return live_run_directory(root, run_id) / 'RUN_MANIFEST.json'

def sha256_file(path):
    p=Path(path)
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def manifest_fingerprint(root):
    p=Path(root)/'MANIFEST.sha256'
    return sha256_file(p) if p.exists() else None


def verify_manifest(root):
    root=Path(root)
    manifest=root/'MANIFEST.sha256'
    if not manifest.exists():
        return {'valid':False,'reason':'manifest_missing','checked':0,'mismatches':[]}
    mismatches=[]; checked=0
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        expected,rel=line.split('  ',1)
        p=root/rel; checked+=1
        if not p.exists():
            mismatches.append({'path':rel,'reason':'missing'})
        elif sha256_file(p)!=expected:
            mismatches.append({'path':rel,'reason':'hash_mismatch'})
    return {'valid':not mismatches,'reason':'ok' if not mismatches else 'mismatch','checked':checked,'mismatches':mismatches}

def environment_snapshot(root):
    root=Path(root)
    lock=root/'requirements'/'runtime-lock.txt'
    integrity=verify_manifest(root)
    return {
        'python_version':sys.version,
        'python_executable':sys.executable,
        'platform':platform.platform(),
        'machine':platform.machine(),
        'artifact_manifest_sha256':manifest_fingerprint(root),
        'artifact_manifest_valid':integrity['valid'],
        'artifact_manifest_checked':integrity['checked'],
        'artifact_manifest_mismatches':integrity['mismatches'][:20],
        'runtime_lock_sha256':sha256_file(lock) if lock.exists() else None,
        'credential_presence':{f'{k}_present':bool(os.getenv(k)) for k in SECRET_ENV_NAMES},
    }

def parse_named_models(values):
    out=[]
    for value in values:
        if '=' not in value:
            raise ValueError(f'--model must be label=model_id, got {value!r}')
        label,model=value.split('=',1)
        label=label.strip(); model=model.strip()
        if not label or not model:
            raise ValueError('model label/id cannot be empty')
        out.append((label,model))
    return out

def normalize_exact_output(value):
    text=str(value or '').strip()
    # tolerate a single code fence while preserving exact semantic token
    if text.startswith('```') and text.endswith('```'):
        lines=text.splitlines()
        if len(lines)>=3:
            text='\n'.join(lines[1:-1]).strip()
    return text.strip().strip('"').strip("'")
