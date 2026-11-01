from pathlib import Path
import argparse,json,zipfile,datetime,sys
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.live_validation import ARTIFACT_VERSION, manifest_fingerprint, sha256_file, verify_manifest, live_run_directory

ap=argparse.ArgumentParser(); ap.add_argument('--run-id',required=True); args=ap.parse_args()
integrity=verify_manifest(ROOT)
if not integrity['valid']:
    raise SystemExit(f"REJECT: canonical artifact manifest invalid: {integrity['mismatches'][:5]}")
run_dir=live_run_directory(ROOT,args.run_id)
run_manifest=run_dir/'RUN_MANIFEST.json'
if not run_manifest.exists(): raise SystemExit(f'REJECT: missing run manifest for {args.run_id}')
run=json.loads(run_manifest.read_text(encoding='utf-8'))
if run.get('artifact_version')!=ARTIFACT_VERSION or run.get('run_id')!=args.run_id or not run.get('passed'):
    raise SystemExit('REJECT: only one complete v1.0.0 run may be exported')
attestation=run_dir/'LIVE_ATTESTATION.json'
source_files=sorted(p for p in run_dir.glob('*.json') if p.is_file() and p.name!=attestation.name)
att={'artifact_version':ARTIFACT_VERSION,'run_id':args.run_id,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'artifact_manifest_sha256':manifest_fingerprint(ROOT),'files':{p.name:sha256_file(p) for p in source_files}}
attestation.write_text(json.dumps(att,indent=2),encoding='utf-8')
out=ROOT/f'LIVE_EVIDENCE_BUNDLE_{args.run_id}.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in [*source_files,attestation]: z.write(p,arcname=f'live_evidence/{p.name}')
print(json.dumps({'bundle':str(out),'run_id':args.run_id,'files':[p.name for p in [*source_files,attestation]],'artifact_manifest_sha256':att['artifact_manifest_sha256']},indent=2))
