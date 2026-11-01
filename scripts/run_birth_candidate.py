from pathlib import Path
import sys,json,subprocess,datetime,hashlib,argparse
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.release_gate import ReleaseGate,GateEvidence,GateState
from sasteratech_runtime.production_drills import ProductionDrills
from sasteratech_runtime.failover import FailoverRuntime
from sasteratech_runtime.runtime_models import RuntimeResponse,RuntimeStatus,ModelProfile,RuntimeRequest
from sasteratech_runtime.roles import Role
from sasteratech_runtime.task_packet import TaskBudget
from sasteratech_runtime.runtime import RuntimeAdapter
import asyncio, importlib.metadata

ap=argparse.ArgumentParser(); ap.add_argument('--verify-only',action='store_true'); args=ap.parse_args()
def cmd(c):
    p=subprocess.run(c,cwd=ROOT,capture_output=True,text=True); return p.returncode,p.stdout[-4000:],p.stderr[-4000:]

evidence=[]; details={}
rc,so,se=cmd([sys.executable,'-m','unittest','discover','-s','tests','-q']); evidence.append(GateEvidence('unit_tests',GateState.PASS if rc==0 else GateState.FAIL,True,{'rc':rc})); details['unit_tests']={'rc':rc,'stdout':so,'stderr':se}
rc,so,se=cmd([sys.executable,'scripts/validate_package.py']); evidence.append(GateEvidence('package_validator',GateState.PASS if rc==0 else GateState.FAIL,True,{'rc':rc})); details['package_validator']={'rc':rc,'stdout':so,'stderr':se}
rc,so,se=cmd([sys.executable,'scripts/run_full_evals.py']); eval_state=GateState.FAIL
try:
    er=json.loads((ROOT/'EVAL_REPORT.json').read_text(encoding='utf-8')); eval_state=GateState.PASS if er.get('gates',{}).get('_critical_pass') and er.get('frozen_v0_6_verified') else GateState.FAIL
except Exception: er={}
evidence.append(GateEvidence('frozen_eval',eval_state,True,{'rc':rc,'critical':er.get('gates',{}).get('_critical_pass'),'frozen':er.get('frozen_v0_6_verified')})); details['eval']={'rc':rc,'stdout':so,'stderr':se}
cr=ProductionDrills.crash_recovery(); mr=ProductionDrills.migration_rollback(); evidence.append(GateEvidence('crash_recovery',GateState.PASS if cr['passed'] else GateState.FAIL,True,cr)); evidence.append(GateEvidence('migration_rollback',GateState.PASS if mr['passed'] else GateState.FAIL,True,mr))

class Fixed(RuntimeAdapter):
    def __init__(self,aid,status): self.adapter_id=aid; self.status=status
    async def run(self,request): return RuntimeResponse(self.status,output='ok' if self.status==RuntimeStatus.COMPLETE else None)
req=RuntimeRequest('R','P','T',Role.RESEARCHER,ModelProfile('m','x',model_id='x',allowed_roles=(Role.RESEARCHER,)),'x','x',TaskBudget())
fo=asyncio.run(FailoverRuntime([Fixed('a',RuntimeStatus.PROVIDER_ERROR),Fixed('b',RuntimeStatus.COMPLETE)]).run(req)); failover_ok=fo.status==RuntimeStatus.COMPLETE and len(fo.metadata.get('failover_attempts',[]))==2
evidence.append(GateEvidence('failover_logic',GateState.PASS if failover_ok else GateState.FAIL,True,{'attempts':fo.metadata.get('failover_attempts')}))

lock=ROOT/'requirements'/'runtime-lock.txt'; lock_ok=lock.exists() and '--hash=' in lock.read_text(encoding='utf-8',errors='ignore'); evidence.append(GateEvidence('runtime_lock',GateState.PASS if lock_ok else GateState.BLOCKED,True,{'present':lock.exists(),'hashed':lock_ok}))
try:
    versions={x:importlib.metadata.version(x) for x in ['pydantic-ai','pydantic-ai-harness']}; import_ok=True
except Exception:
    versions={}; import_ok=False
evidence.append(GateEvidence('runtime_import',GateState.PASS if import_ok else GateState.BLOCKED,True,{'versions':versions}))
for key,path in [('live_provider_probe',ROOT/'evidence'/'live_provider_probe.json'),('live_trajectory_eval',ROOT/'evidence'/'live_trajectory_eval.json'),('real_shadow',ROOT/'evidence'/'real_shadow.json'),('operational_slo',ROOT/'evidence'/'operational_slo.json'),('live_provider_failover',ROOT/'evidence'/'live_provider_failover.json')]:
    state=GateState.NOT_RUN; d={}
    if path.exists():
        try:
            d=json.loads(path.read_text(encoding='utf-8')); state=GateState.PASS if d.get('passed') or d.get('hard_invariant_pass') else GateState.FAIL
        except Exception as e: state=GateState.FAIL; d={'error':type(e).__name__}
    evidence.append(GateEvidence(key,state,True,d))

cfg=json.loads((ROOT/'config'/'release_gate.json').read_text(encoding='utf-8')); decision=ReleaseGate(cfg['offline_required'],cfg['production_required']).evaluate(evidence)
report={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_ready':decision.candidate_ready,'production_ready':decision.production_ready,'blockers':decision.blockers,'evidence':{k:{'state':v.state.value,'critical':v.critical,'details':v.details} for k,v in decision.evidence.items()},'details':details}
(ROOT/'BIRTH_CANDIDATE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
lines=['# SasteraTech Agent Runtime v0.8 — Birth Candidate Report','',f"**Offline birth candidate:** {'PASS' if report['candidate_ready'] else 'FAIL'}",f"**Production ready:** {'YES' if report['production_ready'] else 'NO'}",'', '## Gates','', '| Gate | State |','|---|---|']
for k,v in report['evidence'].items(): lines.append(f"| `{k}` | **{v['state']}** |")
lines += ['', '## Production blockers'] + ([f'- `{x}`' for x in report['blockers']] if report['blockers'] else ['- None']) + ['', 'Production deployment is not authorized by this report.']
(ROOT/'BIRTH_CANDIDATE_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'candidate_ready':report['candidate_ready'],'production_ready':report['production_ready'],'blockers':report['blockers']},indent=2)); raise SystemExit(0 if report['candidate_ready'] else 1)
