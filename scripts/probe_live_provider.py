from pathlib import Path
import os,sys,json,datetime,hashlib,asyncio,importlib.metadata,time
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.adapters.pydantic_ai import PydanticAIRuntimeAdapter
from sasteratech_runtime.runtime_models import ModelProfile,RuntimeRequest,RuntimeStatus
from sasteratech_runtime.roles import Role
from sasteratech_runtime.task_packet import TaskBudget
from sasteratech_runtime.live_validation import ARTIFACT_VERSION, environment_snapshot, live_run_directory, normalize_exact_output

model=os.getenv('SASTERATECH_PROBE_MODEL')
out=live_run_directory(ROOT)/'live_provider_probe.json'; out.parent.mkdir(parents=True,exist_ok=True)
base={'artifact_version':ARTIFACT_VERSION,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':model,'mutation_tools_exposed':False,'environment':environment_snapshot(ROOT)}
if not model:
    base.update({'passed':False,'status':'NOT_RUN','reason':'SASTERATECH_PROBE_MODEL not set'})
    out.write_text(json.dumps(base,indent=2),encoding='utf-8'); print(json.dumps(base,indent=2)); raise SystemExit(3)
try:
    versions={x:importlib.metadata.version(x) for x in ['pydantic-ai','pydantic-ai-harness']}
except Exception as e:
    base.update({'passed':False,'status':'BLOCKED','reason':f'runtime unavailable: {type(e).__name__}'})
    out.write_text(json.dumps(base,indent=2),encoding='utf-8'); print(json.dumps(base,indent=2)); raise SystemExit(2)
req=RuntimeRequest('PROBE-RUN','PROBE-PACKET','PROBE-TASK',Role.RESEARCHER,ModelProfile('probe','pydantic_ai',model_id=model,allowed_roles=(Role.RESEARCHER,)),'Return exactly: SASTERATECH_PROBE_OK','This is a no-tool compatibility probe. Return the exact token.',TaskBudget(max_tool_calls=0,max_tokens=256,max_seconds=30,max_model_requests=2,max_context_tokens=512))
t=time.perf_counter(); res=asyncio.run(PydanticAIRuntimeAdapter().run(req)); latency=time.perf_counter()-t
raw=str(res.output or ''); norm=normalize_exact_output(raw)
base.update({'versions':versions,'status':res.status.value,'passed':res.status==RuntimeStatus.COMPLETE and norm=='SASTERATECH_PROBE_OK','exact_output_match':norm=='SASTERATECH_PROBE_OK','output_sha256':hashlib.sha256(raw.encode()).hexdigest() if raw else None,'output_length':len(raw),'latency_seconds':latency,'runtime_run_id':res.runtime_run_id,'conversation_id':res.conversation_id,'usage':res.usage.__dict__,'messages_serialized':bool(res.messages_json),'error_type':res.error_type})
out.write_text(json.dumps(base,indent=2),encoding='utf-8'); print(json.dumps({k:base[k] for k in ['model','status','passed','exact_output_match','latency_seconds']},indent=2)); raise SystemExit(0 if base['passed'] else 1)
