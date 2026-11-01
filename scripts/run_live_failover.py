from pathlib import Path
import argparse,sys,json,asyncio,datetime
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.runtime import RuntimeAdapter
from sasteratech_runtime.adapters.pydantic_ai import PydanticAIRuntimeAdapter
from sasteratech_runtime.failover import FailoverRuntime
from sasteratech_runtime.runtime_models import ModelProfile,RuntimeRequest,RuntimeResponse,RuntimeStatus
from sasteratech_runtime.roles import Role
from sasteratech_runtime.task_packet import TaskBudget
from sasteratech_runtime.live_validation import ARTIFACT_VERSION, normalize_exact_output,environment_snapshot,live_run_directory

ap=argparse.ArgumentParser(); ap.add_argument('--secondary',required=True,help='live fallback model id'); args=ap.parse_args()
class InjectedFailure(RuntimeAdapter):
    adapter_id='fault_injected_primary'
    async def run(self,request): return RuntimeResponse(RuntimeStatus.PROVIDER_ERROR,error_type='InjectedFailure',error_message='controlled fault injection')
secondary=PydanticAIRuntimeAdapter(); secondary.adapter_id='live_secondary'
req=RuntimeRequest('LIVE-FAILOVER','P','T',Role.RESEARCHER,ModelProfile('secondary','live_secondary',model_id=args.secondary,allowed_roles=(Role.RESEARCHER,)),'Return exactly: SASTERATECH_FAILOVER_OK','No tools are available.',TaskBudget(max_tool_calls=0,max_tokens=128,max_seconds=45,max_model_requests=2,max_context_tokens=512))
res=asyncio.run(FailoverRuntime([InjectedFailure(),secondary]).run(req)); actual=normalize_exact_output(res.output)
passed=res.status==RuntimeStatus.COMPLETE and actual=='SASTERATECH_FAILOVER_OK' and len(res.metadata.get('failover_attempts',[]))>=2
data={'artifact_version':ARTIFACT_VERSION,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'test_type':'controlled_primary_fault_injection_live_secondary','secondary_model':args.secondary,'environment':environment_snapshot(ROOT),'passed':passed,'status':res.status.value,'actual':actual,'attempts':res.metadata.get('failover_attempts',[]),'error_type':res.error_type}
out=live_run_directory(ROOT)/'live_provider_failover.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(data,indent=2),encoding='utf-8'); print(json.dumps(data,indent=2)); raise SystemExit(0 if passed else 1)
