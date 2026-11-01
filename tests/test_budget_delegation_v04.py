import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.task_packet import TaskPacket,TaskBudget
from sasteratech_runtime.roles import Role
from sasteratech_runtime.models import TaskClass,Risk
from sasteratech_runtime.delegation import DelegationEngine,DelegationError
class DelegationBudgetTests(unittest.TestCase):
    def test_child_model_budget_cannot_expand(self):
        parent=TaskPacket('P','R','T','root',TaskClass.RESEARCH,Role.ORCHESTRATOR,Risk.R0,budget=TaskBudget(max_model_requests=3,max_tokens=1000,max_seconds=60,max_tool_calls=2),depth=0)
        child=TaskPacket('C','R','T2','child',TaskClass.RESEARCH,Role.RESEARCHER,Risk.R0,budget=TaskBudget(max_model_requests=4,max_tokens=900,max_seconds=50,max_tool_calls=1),depth=1,parent_packet_id='P')
        with self.assertRaises(DelegationError): DelegationEngine().validate(parent,child)
if __name__=='__main__': unittest.main()
