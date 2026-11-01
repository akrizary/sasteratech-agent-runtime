import sys,pathlib,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import *
from sasteratech_runtime.repository import RunRepository

class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.s=SQLiteStore(pathlib.Path(self.td.name)/'x.db')
        RunRepository(self.s).create('R','BUILD','STATE_0_READ_ONLY_AUDIT')
        self.reg=ExecutableToolRegistry(); self.state={}
        def validate(a):
            if 'path' not in a or 'value' not in a: raise ValueError('path/value required')
        def write(a): self.state[a['path']]=a['value']; return {'path':a['path'],'value':a['value']}
        def readback(a,r): return self.state.get(a['path'])
        def verify(a,r,o): return o==a['value']
        td=ToolDefinition('file.write','1',Risk.R2,True,True,idempotent=True,reversible=True,network=False)
        self.reg.register(ToolRuntimeSpec(td,write,validate,readback,verify,output_trust='TRUSTED_LOCAL'))
        self.ap=ApprovalService(self.s)
        self.gw=ToolGateway(self.reg,store=self.s,approval_service=self.ap)
        self.intent=ActionIntent('builder',Role.BUILDER,'file.write','/repo/a',Risk.R2,'test')
    def tearDown(self): self.s.close(); self.td.cleanup()
    def test_requires_approval_then_verifies(self):
        first=self.gw.execute('R',self.intent,{'path':'/repo/a','value':'x'},idempotency_key='K')
        self.assertEqual(first.status,'APPROVAL_REQUIRED'); self.assertFalse(first.executed)
        grant=self.ap.grant_human(first.approval_request_id,'human')
        out=self.gw.execute('R',self.intent,{'path':'/repo/a','value':'x'},grants=(grant,),idempotency_key='K')
        self.assertTrue(out.executed); self.assertTrue(out.verified); self.assertEqual(out.status,'VERIFIED')
        # repeat: same idempotency key must not execute again
        again=self.gw.execute('R',self.intent,{'path':'/repo/a','value':'x'},grants=(grant,),idempotency_key='K')
        self.assertFalse(again.executed); self.assertEqual(again.status,'REUSED')
    def test_wrong_role_block(self):
        bad=ActionIntent('researcher',Role.RESEARCHER,'file.write','/repo/a',Risk.R2,'bad')
        out=self.gw.execute('R',bad,{'path':'/repo/a','value':'x'})
        self.assertEqual(out.status,'BLOCKED')
if __name__=='__main__': unittest.main()
