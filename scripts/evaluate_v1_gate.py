from pathlib import Path
import json,sys,hashlib,datetime,importlib.metadata
ROOT=Path(__file__).parents[1]
ARTIFACT_VERSION='1.0.0'

def load(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None

def state_for(path, predicate=lambda x: bool(x.get('passed'))):
    d=load(path)
    if d is None: return 'NOT_RUN',{}
    try: return ('PASS' if predicate(d) else 'FAIL'),d
    except Exception as e: return 'FAIL',{'error':type(e).__name__}

def valid_live_shadow(d):
    execution=d.get('shadow_execution',{})
    return (
        d.get('passed')
        and d.get('hard_invariant_pass')
        and d.get('artifact_version') == ARTIFACT_VERSION
        and d.get('input_schema_version') == ARTIFACT_VERSION
        and execution.get('mode') == 'live_no_tool_model_generation'
        and execution.get('proposals_generated_by_model') is True
        and execution.get('prewritten_proposals_rejected') is True
        and bool(d.get('generated_cases'))
        and d.get('metrics',{}).get('high_risk_false_negatives',1) == 0
    )

ev={}
lock=ROOT/'requirements'/'runtime-lock.txt'; ev['runtime_lock']={'state':'PASS' if lock.exists() and '--hash=' in lock.read_text(encoding='utf-8',errors='ignore') else 'BLOCKED'}
try:
    versions={x:importlib.metadata.version(x) for x in ('pydantic-ai','pydantic-ai-harness')}; ev['runtime_import']={'state':'PASS','versions':versions}
except Exception: ev['runtime_import']={'state':'BLOCKED','versions':{}}
pointer=load(ROOT/'evidence'/'imported'/'CURRENT_IMPORTED_RUN.json')
imported_root=(ROOT/'evidence'/'imported').resolve()
live=None
if pointer and pointer.get('artifact_version')==ARTIFACT_VERSION and pointer.get('imported_dir'):
    candidate=Path(pointer['imported_dir']).resolve()
    try:
        candidate.relative_to(imported_root)
        live=candidate
    except ValueError:
        pass
ev['imported_run']={'state':'PASS' if live and live.exists() else 'NOT_RUN','run_id':pointer.get('run_id') if pointer else None}
ev['live_environment']={'state':'PASS' if live and (load(live/'live_environment.json') or {}).get('runtime_import_pass') and (load(live/'live_environment.json') or {}).get('artifact_version')==ARTIFACT_VERSION else 'NOT_RUN'}
for key,file,pred in [
 ('live_provider_probe','live_provider_probe.json',lambda d:d.get('passed')),
 ('live_trajectory_eval','live_trajectory_eval.json',lambda d:d.get('passed') and d.get('pass_rate')==1.0),
 ('provider_matrix','provider_matrix.json',lambda d:d.get('passed')),
 ('operational_slo','operational_slo.json',lambda d:d.get('passed') and d.get('thresholds_configured')),
 ('live_provider_failover','live_provider_failover.json',lambda d:d.get('passed')),
 ('real_shadow','real_shadow.json',valid_live_shadow),
]:
    st,d=state_for(live/file,pred) if live else ('NOT_RUN',{}); ev[key]={'state':st,'details':d}
required=json.loads((ROOT/'config/v1_gate.json').read_text(encoding='utf-8'))['required']
blockers=[k for k in required if ev.get(k,{}).get('state')!='PASS']
# failover is conditional: only gate if evidence exists or config says failover is expected (future config field)
status='PASS_EVIDENCE_COMPLETE' if not blockers else 'BLOCKED_MISSING_EVIDENCE'
report={'artifact_version':ARTIFACT_VERSION,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':status,'production_evidence_complete':not blockers,'deployment_authorized':False,'blockers':blockers,'evidence':ev}
(ROOT/'V1_GATE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'status':status,'production_evidence_complete':not blockers,'deployment_authorized':False,'blockers':blockers},indent=2)); raise SystemExit(0 if not blockers else 2)
