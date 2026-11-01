from pathlib import Path
import json, importlib.metadata, datetime, sys
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.live_validation import ARTIFACT_VERSION, environment_snapshot, live_run_directory
out=live_run_directory(ROOT)/'runtime_import_probe.json'; out.parent.mkdir(parents=True,exist_ok=True)
packages=['pydantic-ai','pydantic-ai-harness']
result={'artifact_version':ARTIFACT_VERSION,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packages':{},'passed':True,'environment':environment_snapshot(ROOT)}
for pkg in packages:
    try: result['packages'][pkg]={'version':importlib.metadata.version(pkg),'available':True}
    except importlib.metadata.PackageNotFoundError:
        result['packages'][pkg]={'version':None,'available':False}; result['passed']=False
out.write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2)); raise SystemExit(0 if result['passed'] else 2)
