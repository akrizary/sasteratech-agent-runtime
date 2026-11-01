from pathlib import Path
import argparse,subprocess,sys,os,json,datetime,uuid
ROOT=Path(__file__).parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('--model'); ap.add_argument('--shadow-dataset'); ap.add_argument('--slo-samples',type=int,default=20); ap.add_argument('--slo-policy',default=str(ROOT/'config/live_validation.local.json')); ap.add_argument('--run-id'); args=ap.parse_args()
model=args.model or os.getenv('SASTERATECH_PROBE_MODEL')
lock=ROOT/'requirements'/'runtime-lock.txt'
if not lock.exists() or '--hash=' not in lock.read_text(encoding='utf-8',errors='ignore'):
    raise SystemExit('BLOCKED: requirements/runtime-lock.txt with hashes is required before any live provider call')
if not Path(args.slo_policy).exists():
    raise SystemExit(f'BLOCKED: approved SLO policy is required: {args.slo_policy}')
env=dict(os.environ)
if model: env['SASTERATECH_PROBE_MODEL']=model
run_id=args.run_id or (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8])
run_dir=ROOT/'evidence'/'live_runs'/run_id
if run_dir.exists(): raise SystemExit(f'REJECT: live run id already exists: {run_id}')
run_dir.mkdir(parents=True)
env['SASTERATECH_LIVE_RUN_ID']=run_id
steps=[
 [sys.executable,'scripts/capture_live_environment.py'],
 [sys.executable,'scripts/probe_runtime_import.py'],
]
if model:
    steps += [[sys.executable,'scripts/probe_live_provider.py'],[sys.executable,'scripts/run_live_trajectory_eval.py'],[sys.executable,'scripts/run_provider_matrix.py','--model',f'default={model}'],[sys.executable,'scripts/run_operational_baseline.py','--model',model,'--samples',str(args.slo_samples),'--policy',args.slo_policy]]
if args.shadow_dataset:
    if not model:
        raise SystemExit('--model or SASTERATECH_PROBE_MODEL is required for a live real-shadow run')
    steps += [[sys.executable,'scripts/run_real_shadow.py',args.shadow_dataset,'--model',model]]
results=[]
for cmd in steps:
    p=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True)
    results.append({'cmd':cmd,'rc':p.returncode,'stdout_tail':p.stdout[-1500:],'stderr_tail':p.stderr[-1500:]})
passed=all(r['rc']==0 for r in results)
manifest={'artifact_version':'1.0.0','run_id':run_id,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'attempt':1,'retry_performed':False,'run_dir':str(run_dir),'model':model,'slo_samples':args.slo_samples,'shadow_dataset':str(Path(args.shadow_dataset).resolve()) if args.shadow_dataset else None,'steps':results,'passed':passed}
(run_dir/'RUN_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'run_id':run_id,'run_dir':str(run_dir),'passed':passed,'steps':results},indent=2)); raise SystemExit(0 if passed else 2)
