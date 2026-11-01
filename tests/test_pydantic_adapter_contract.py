import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.adapters.pydantic_ai import PydanticAIRuntimeAdapter
from sasteratech_runtime.runtime_models import ModelProfile,RuntimeRequest
from sasteratech_runtime.roles import Role
from sasteratech_runtime.task_packet import TaskBudget
from tests.async_support import run_immediate
class FakeUsageLimits:
    def __init__(self,**kwargs): self.kwargs=kwargs
class FakeUsage:
    requests=2; tool_calls=0; input_tokens=30; output_tokens=10; total_tokens=40; cost=0.01; unmeasured_requests=0
class FakeResult:
    output='ok'; run_id='RID'; conversation_id='CID'; usage=FakeUsage()
    def all_messages_json(self): return b'[]'
class FakeAgent:
    created=[]
    def __init__(self,model,**kwargs): self.model=model; self.kwargs=kwargs; FakeAgent.created.append(self)
    async def run(self,prompt,**kwargs): self.prompt=prompt; self.run_kwargs=kwargs; return FakeResult()
class AdapterTests(unittest.TestCase):
    def test_contract_mapping(self):
        a=PydanticAIRuntimeAdapter(); a._load=lambda:(FakeAgent,FakeUsageLimits)
        req=RuntimeRequest('RUN','P','T',Role.RESEARCHER,ModelProfile('m','pydantic_ai',model_id='openai:test',allowed_roles=(Role.RESEARCHER,)),'do work','rules',TaskBudget(max_tool_calls=7,max_tokens=1000,max_seconds=5,max_model_requests=4,max_context_tokens=500,max_cost_usd=1.5),context_text='ctx')
        out=run_immediate(a.run(req)); self.assertEqual(out.output,'ok'); agent=FakeAgent.created[-1]; self.assertEqual(agent.model,'openai:test'); limits=agent.run_kwargs['usage_limits']; self.assertEqual(limits.kwargs['request_limit'],4); self.assertEqual(limits.kwargs['tool_calls_limit'],0); self.assertEqual(limits.kwargs['total_tokens_limit'],1000); self.assertEqual(agent.run_kwargs['timeout'],5); self.assertEqual(agent.run_kwargs['run_id'],'RUN'); self.assertIn('bounded context',agent.prompt)
if __name__=='__main__': unittest.main()
