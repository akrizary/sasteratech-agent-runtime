import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.roles import Role
from sasteratech_runtime.models import Risk,TaskClass,ToolDefinition
from sasteratech_runtime.actions import ActionIntent,CapabilityGuard
from sasteratech_runtime.task_packet import TaskPacket
from sasteratech_runtime.workers import Worker
from sasteratech_runtime.verification import VerificationRequest,VerificationIndependenceError
from sasteratech_runtime.organ_router import OrganRouter

class OrganTests(unittest.TestCase):
    def test_capability_guard_blocks_builder_deploy(self):
        intent=ActionIntent('W1',Role.BUILDER,'deploy.production','prod',Risk.R4,'ship')
        tool=ToolDefinition('deploy.production','1',Risk.R4,True,True)
        self.assertFalse(CapabilityGuard().check(intent,tool).allowed)
    def test_worker_packet_tool_check(self):
        w=Worker('W1',Role.RESEARCHER)
        p=TaskPacket('P','R','T','research',TaskClass.RESEARCH,Role.RESEARCHER,Risk.R0,('file.read',))
        self.assertTrue(w.validate_packet(p))
    def test_worker_rejects_wrong_role(self):
        w=Worker('W1',Role.RESEARCHER)
        p=TaskPacket('P','R','T','build',TaskClass.BUILD,Role.BUILDER,Risk.R0,('file.read',))
        with self.assertRaises(ValueError): w.validate_packet(p)
    def test_independent_verifier(self):
        self.assertTrue(VerificationRequest(('C1',),'builder-1','verifier-1').validate())
    def test_self_verification_blocked(self):
        with self.assertRaises(VerificationIndependenceError):
            VerificationRequest(('C1',),'same','same').validate()
    def test_organ_router(self):
        r=OrganRouter()
        self.assertEqual(r.primary(TaskClass.DEBUG),Role.DEBUGGER)
        self.assertIn(Role.VERIFIER,r.post_roles(TaskClass.BUILD))
if __name__=='__main__': unittest.main()
