from pathlib import Path
import argparse,sys,json,asyncio,datetime,time
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.live_validation import ARTIFACT_VERSION, parse_named_models, normalize_exact_output, environment_snapshot, live_run_directory
from sasteratech_runtime.adapters.pydantic_ai import PydanticAIRuntimeAdapter
from sasteratech_runtime.runtime_models import ModelProfile,RuntimeRequest,RuntimeStatus
from sasteratech_runtime.roles import Role
from sasteratech_runtime.task_packet import TaskBudget

ap=argparse.ArgumentParser(); ap.add_argument('--model',action='append',default=[],help='label=model_id'); args=ap.parse_args()
outdir=live_run_directory(ROOT); outdir.mkdir(parents=True,exist_ok=True); out=outdir/'provider_matrix.json'
try: models=parse_named_models(args.model)
except Exception as e:
    print(str(e),file=sys.stderr); raise SystemExit(2)
if not models:
    data={'artifact_version':ARTIFACT_VERSION,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False,'status':'NOT_RUN','reason':'no --model supplied','models':[]}
    out.write_text(json.dumps(data,indent=2),encoding='utf-8'); print(json.dumps(data,indent=2)); raise SystemExit(3)
adapter=PydanticAIRuntimeAdapter(); rows=[]
async def main():
    for label,model in models:
        req=RuntimeRequest(
            f'MATRIX-{label}','P',label,Role.RESEARCHER,
            ModelProfile(label,'pydantic_ai',model_id=model,allowed_roles=(Role.RESEARCHER,)),
            'Return exactly: SASTERATECH_PROVIDER_OK',
            'No tools are available. Return the exact requested token.',
            TaskBudget(max_tool_calls=0,max_tokens=512,max_seconds=45,max_model_requests=2,max_context_tokens=512)
        )
        t=time.perf_counter(); res=await adapter.run(req); latency=time.perf_counter()-t
        actual=normalize_exact_output(res.output)
        rows.append({'label':label,'model':model,'status':res.status.value,'passed':res.status==RuntimeStatus.COMPLETE and actual=='SASTERATECH_PROVIDER_OK','actual':actual,'latency_seconds':latency,'usage':res.usage.__dict__,'error_type':res.error_type})
asyncio.run(main())
passed=bool(rows) and all(r['passed'] for r in rows)
data={'artifact_version':ARTIFACT_VERSION,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environment':environment_snapshot(ROOT),'passed':passed,'status':'COMPLETE','models':rows}
out.write_text(json.dumps(data,indent=2),encoding='utf-8'); print(json.dumps({'passed':passed,'models':[{k:r[k] for k in ('label','status','passed')} for r in rows]},indent=2)); raise SystemExit(0 if passed else 1)
