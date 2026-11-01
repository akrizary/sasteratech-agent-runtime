from pathlib import Path
import argparse,zipfile,tempfile,json,shutil,sys,datetime
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.live_validation import ARTIFACT_VERSION, manifest_fingerprint, sha256_file
ap=argparse.ArgumentParser(); ap.add_argument('bundle'); args=ap.parse_args()
bundle=Path(args.bundle)
with tempfile.TemporaryDirectory() as td:
    with zipfile.ZipFile(bundle) as z: z.extractall(td)
    base=Path(td)/'live_evidence'; att=json.loads((base/'LIVE_ATTESTATION.json').read_text(encoding='utf-8'))
    expected=manifest_fingerprint(ROOT); actual=att.get('artifact_manifest_sha256'); run_id=att.get('run_id')
    if att.get('artifact_version')!=ARTIFACT_VERSION or not run_id:
        raise SystemExit('REJECT: unsupported or unlabelled evidence version')
    if expected!=actual: raise SystemExit(f'REJECT: artifact manifest mismatch expected={expected} evidence={actual}')
    for name,h in att.get('files',{}).items():
        p=base/name
        if not p.exists() or sha256_file(p)!=h: raise SystemExit(f'REJECT: evidence hash mismatch {name}')
    run=json.loads((base/'RUN_MANIFEST.json').read_text(encoding='utf-8'))
    if run.get('run_id')!=run_id or not run.get('passed') or run.get('retry_performed'):
        raise SystemExit('REJECT: evidence run is incomplete, mismatched, or retried')
    dest=ROOT/'evidence'/'imported'/run_id
    if dest.exists(): raise SystemExit(f'REJECT: imported run already exists: {run_id}')
    dest.mkdir(parents=True)
    for p in base.glob('*.json'): shutil.copy2(p,dest/p.name)
    pointer={'artifact_version':ARTIFACT_VERSION,'run_id':run_id,'imported_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bundle_sha256':sha256_file(bundle),'imported_dir':str(dest)}
    pointer_path=ROOT/'evidence'/'imported'/'CURRENT_IMPORTED_RUN.json'; pointer_path.write_text(json.dumps(pointer,indent=2),encoding='utf-8')
    print(json.dumps({'imported_to':str(dest),'run_id':run_id,'manifest_match':True,'files':sorted(p.name for p in dest.glob('*.json'))},indent=2))
