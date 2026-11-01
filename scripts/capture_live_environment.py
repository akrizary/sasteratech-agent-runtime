from pathlib import Path
import json, datetime, importlib.metadata, sys
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.live_validation import ARTIFACT_VERSION, environment_snapshot, live_run_directory

outdir=live_run_directory(ROOT); outdir.mkdir(parents=True,exist_ok=True)
base=environment_snapshot(ROOT)
base.update({'artifact_version':ARTIFACT_VERSION,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
versions={}
for pkg in ('pydantic-ai','pydantic-ai-harness'):
    try: versions[pkg]=importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError: versions[pkg]=None
base['package_versions']=versions
base['runtime_import_pass']=all(versions.values())
out=outdir/'live_environment.json'; out.write_text(json.dumps(base,indent=2),encoding='utf-8')
print(json.dumps(base,indent=2))
raise SystemExit(0 if base['runtime_import_pass'] else 2)
