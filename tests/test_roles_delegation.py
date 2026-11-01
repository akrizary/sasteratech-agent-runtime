import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.roles import Role,RoleRegistry
from sasteratech_runtime.models import Risk,TaskClass
from sasteratech_runtime.task_packet import TaskPacket,TaskBudget
from sasteratech_runtime.delegation import DelegationEngine,DelegationError

class RoleDelegationTests(unittest.TestCase):
    def setUp(self): self.reg=RoleRegistry(); self.de=DelegationEngine(self.reg,max_depth=2)
    def test_researcher_no_write(self):
        self.assertFalse(self.reg.get(Role.RESEARCHER).tool_allowed('file.write'))
    def test_builder_no_deploy(self):
        self.assertFalse(self.reg.get(Role.BUILDER).tool_allowed('deploy.production'))
    def test_valid_builder_to_verifier_narrowing(self):
        p=TaskPacket('P','R','T','build',TaskClass.BUILD,Role.BUILDER,Risk.R2,('file.read','file.write'),budget=TaskBudget(10,1000,100),resource_scope=('/repo/*',))
        c=TaskPacket('C','R','V','verify',TaskClass.REVIEW,Role.VERIFIER,Risk.R1,('file.read',),budget=TaskBudget(5,500,50),depth=1,parent_packet_id='P',resource_scope=('/repo/*',))
        self.assertTrue(self.de.validate(p,c))
    def test_child_cannot_expand_risk(self):
        p=TaskPacket('P','R','T','debug',TaskClass.DEBUG,Role.DEBUGGER,Risk.R0,('file.read',),budget=TaskBudget(10,1000,100))
        c=TaskPacket('C','R','V','verify',TaskClass.REVIEW,Role.VERIFIER,Risk.R1,('file.read',),budget=TaskBudget(5,500,50),depth=1,parent_packet_id='P')
        with self.assertRaises(DelegationError): self.de.validate(p,c)
    def test_wrong_delegation_edge(self):
        p=TaskPacket('P','R','T','research',TaskClass.RESEARCH,Role.RESEARCHER,Risk.R0,('file.read',))
        c=TaskPacket('C','R','B','build',TaskClass.BUILD,Role.BUILDER,Risk.R0,('file.read',),depth=1,parent_packet_id='P')
        with self.assertRaises(DelegationError): self.de.validate(p,c)
if __name__=='__main__': unittest.main()
