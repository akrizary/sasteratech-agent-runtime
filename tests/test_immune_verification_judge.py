import sys,pathlib,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import *
from sasteratech_runtime.repository import RunRepository

class VerificationJudgeTests(unittest.TestCase):
    def setup_env(self):
        td=tempfile.TemporaryDirectory(); s=SQLiteStore(pathlib.Path(td.name)/'x.db'); RunRepository(s).create('R','BUILD','STATE_0_READ_ONLY_AUDIT')
        return td,s
    def test_r2_without_readback_blocked_even_with_grant(self):
        td,s=self.setup_env(); ap=ApprovalService(s); reg=ExecutableToolRegistry(); called=[]
        tool=ToolDefinition('file.write','1',Risk.R2,True,True)
        reg.register(ToolRuntimeSpec(tool,lambda a: called.append(1) or 'ok'))
        intent=ActionIntent('b',Role.BUILDER,'file.write','/repo/a',Risk.R2,'x')
        req=ap.request('R',intent.action_id,'file.write','/repo/a',Risk.R2,'x'); grant=ap.grant_human(req,'human')
        out=ToolGateway(reg,store=s,approval_service=ap).execute('R',intent,{},grants=(grant,))
        self.assertEqual(out.status,'BLOCKED'); self.assertEqual(called,[])
        s.close(); td.cleanup()
    def test_escalation_accepts_existing_human_grant(self):
        td,s=self.setup_env(); ap=ApprovalService(s); reg=ExecutableToolRegistry(); state={}
        tool=ToolDefinition('file.write','1',Risk.R2,True,True)
        reg.register(ToolRuntimeSpec(tool,lambda a: state.update(v=1) or 'ok',readback=lambda a,r:state.get('v'),verify_effect=lambda a,r,o:o==1))
        intent=ActionIntent('b',Role.BUILDER,'file.write','/repo/a',Risk.R2,'x')
        req=ap.request('R',intent.action_id,'file.write','/repo/a',Risk.R2,'x'); grant=ap.grant_human(req,'human')
        class Escalate(SemanticRiskJudge):
            def judge(self,*x): return JudgeDecision(JudgeDisposition.ESCALATE,'ambiguous','test')
        out=ToolGateway(reg,store=s,approval_service=ap,risk_judge=Escalate()).execute('R',intent,{},grants=(grant,),idempotency_key='k')
        self.assertTrue(out.verified)
        s.close(); td.cleanup()
if __name__=='__main__': unittest.main()
