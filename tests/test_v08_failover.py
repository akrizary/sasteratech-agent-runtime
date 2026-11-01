import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.failover import FailoverRuntime
from sasteratech_runtime.runtime import RuntimeAdapter
from sasteratech_runtime.runtime_models import RuntimeResponse,RuntimeStatus,RuntimeRequest,ModelProfile
from sasteratech_runtime.roles import Role
from sasteratech_runtime.task_packet import TaskBudget
from tests.async_support import run_immediate
class A(RuntimeAdapter):
    def __init__(self,id,status): self.adapter_id=id; self.status=status
    async def run(self,r): return RuntimeResponse(self.status,output='ok' if self.status==RuntimeStatus.COMPLETE else None)
def req(): return RuntimeRequest('R','P','T',Role.RESEARCHER,ModelProfile('m','x',model_id='x'),'x','x',TaskBudget())
class T(unittest.TestCase):
    def test_failover_on_provider_error(self):
        r=run_immediate(FailoverRuntime([A('one',RuntimeStatus.PROVIDER_ERROR),A('two',RuntimeStatus.COMPLETE)]).run(req()))
        self.assertEqual(r.status,RuntimeStatus.COMPLETE); self.assertEqual(len(r.metadata['failover_attempts']),2)
    def test_no_failover_on_budget_exceeded(self):
        r=run_immediate(FailoverRuntime([A('one',RuntimeStatus.BUDGET_EXCEEDED),A('two',RuntimeStatus.COMPLETE)]).run(req()))
        self.assertEqual(r.status,RuntimeStatus.BUDGET_EXCEEDED); self.assertEqual(len(r.metadata['failover_attempts']),1)
if __name__=='__main__': unittest.main()
