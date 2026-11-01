from pathlib import Path
import argparse,sys,json,asyncio,datetime,time,statistics
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.adapters.pydantic_ai import PydanticAIRuntimeAdapter
from sasteratech_runtime.runtime_models import ModelProfile,RuntimeRequest,RuntimeStatus
from sasteratech_runtime.roles import Role
from sasteratech_runtime.task_packet import TaskBudget
from sasteratech_runtime.live_validation import ARTIFACT_VERSION, normalize_exact_output,environment_snapshot,live_run_directory

ap=argparse.ArgumentParser(); ap.add_argument('--model',required=True); ap.add_argument('--samples',type=int,default=20); ap.add_argument('--policy',default=str(ROOT/'config/live_validation.local.json')); args=ap.parse_args()
if args.samples<=0: raise SystemExit('samples must be >0')
adapter=PydanticAIRuntimeAdapter(); rows=[]
async def main():
    for i in range(args.samples):
        req=RuntimeRequest(f'SLO-{i}','P',str(i),Role.RESEARCHER,ModelProfile('slo','pydantic_ai',model_id=args.model,allowed_roles=(Role.RESEARCHER,)),'Return exactly: SASTERATECH_SLO_OK','No tools are available. Reply with exactly SASTERATECH_SLO_OK and no other text.',TaskBudget(max_tool_calls=0,max_tokens=512,max_seconds=45,max_model_requests=2,max_context_tokens=512))
        t=time.perf_counter(); res=await adapter.run(req); latency=time.perf_counter()-t
        rows.append({'status':res.status.value,'passed':res.status==RuntimeStatus.COMPLETE and normalize_exact_output(res.output)=='SASTERATECH_SLO_OK','latency_seconds':latency,'total_tokens':res.usage.total_tokens,'cost_usd':res.usage.cost_usd})
asyncio.run(main())
lat=[r['latency_seconds'] for r in rows]; errors=sum(1 for r in rows if not r['passed']); costs=[r['cost_usd'] for r in rows if r['cost_usd'] is not None]
sl=sorted(lat); p95=sl[min(len(sl)-1,max(0,int((len(sl)-1)*0.95)))] if sl else None
observed={'samples':len(rows),'error_rate':errors/len(rows) if rows else 1.0,'mean_latency_seconds':statistics.mean(lat) if lat else None,'p95_latency_seconds':p95,'mean_cost_usd':statistics.mean(costs) if costs else None}
policy_path=Path(args.policy); configured=False; failures=[]; unconfigured=[]
if policy_path.exists():
    cfg=json.loads(policy_path.read_text(encoding='utf-8')).get('slo',{})
    checks=[('minimum_samples','min'),('max_error_rate','max'),('max_p95_latency_seconds','max'),('max_mean_cost_usd','max')]
    configured=True
    for key,mode in checks:
        limit=cfg.get(key)
        if limit is None:
            configured=False; unconfigured.append(key); continue
        metric={'minimum_samples':'samples','max_error_rate':'error_rate','max_p95_latency_seconds':'p95_latency_seconds','max_mean_cost_usd':'mean_cost_usd'}[key]
        value=observed.get(metric)
        if value is None: failures.append(f'{metric} unavailable')
        elif mode=='min' and value<limit: failures.append(f'{metric}={value} below {limit}')
        elif mode=='max' and value>limit: failures.append(f'{metric}={value} exceeds {limit}')
passed=configured and not failures
data={'artifact_version':ARTIFACT_VERSION,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':args.model,'environment':environment_snapshot(ROOT),'observed':observed,'thresholds_configured':configured,'unconfigured':unconfigured,'failures':failures,'passed':passed,'samples_detail':rows}
out=live_run_directory(ROOT)/'operational_slo.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(data,indent=2),encoding='utf-8'); print(json.dumps({k:data[k] for k in ('observed','thresholds_configured','unconfigured','failures','passed')},indent=2)); raise SystemExit(0 if passed else 2)
