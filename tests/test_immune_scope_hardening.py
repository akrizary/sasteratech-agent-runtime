import sys,pathlib,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import *
from sasteratech_runtime.repository import RunRepository

class ScopeHardeningTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.s=SQLiteStore(pathlib.Path(self.td.name)/'x.db')
        RunRepository(self.s).create('R1','BUILD','STATE_0_READ_ONLY_AUDIT'); RunRepository(self.s).create('R2','BUILD','STATE_0_READ_ONLY_AUDIT')
        self.a=ApprovalService(self.s)
    def tearDown(self): self.s.close(); self.td.cleanup()
    def test_grant_bound_to_run_and_action(self):
        rid=self.a.request('R1','ACT1','file.write','/repo/a',Risk.R2,'x'); g=self.a.grant_human(rid,'human')
        tool=ToolDefinition('file.write','1',Risk.R2,True,True)
        pe=PolicyEngine()
        self.assertTrue(pe.decide(tool,'/repo/a',(g,),run_id='R1',action_id='ACT1').allowed)
        self.assertFalse(pe.decide(tool,'/repo/a',(g,),run_id='R2',action_id='ACT1').allowed)
        self.assertFalse(pe.decide(tool,'/repo/a',(g,),run_id='R1',action_id='ACT2').allowed)
        loaded=self.a.load_grant(g.approval_id); self.assertEqual(loaded.action_id,'ACT1'); self.assertEqual(loaded.run_id,'R1')
    def test_intent_cannot_understate_risk_or_escape_scope(self):
        guard=CapabilityGuard(); tool=ToolDefinition('file.write','1',Risk.R2,True,True)
        low=ActionIntent('b',Role.BUILDER,'file.write','/repo/a',Risk.R0,'x',resource_scope=('/repo/**',))
        self.assertFalse(guard.check(low,tool).allowed)
        out=ActionIntent('b',Role.BUILDER,'file.write','/other/a',Risk.R2,'x',resource_scope=('/repo/**',))
        self.assertFalse(guard.check(out,tool).allowed)
if __name__=='__main__': unittest.main()
