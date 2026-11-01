import sys,pathlib,tempfile,unittest
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import SQLiteStore,ApprovalService,PolicyEngine,ToolDefinition,Risk,ApprovalGrant
from sasteratech_runtime.repository import RunRepository

class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.s=SQLiteStore(pathlib.Path(self.td.name)/'x.db')
        RunRepository(self.s).create('R','BUILD','STATE_0_READ_ONLY_AUDIT'); self.a=ApprovalService(self.s)
    def tearDown(self): self.s.close(); self.td.cleanup()
    def test_schema_v3(self):
        self.assertEqual(self.s.conn.execute('select max(version) v from schema_migrations').fetchone()['v'],5)
    def test_human_grant(self):
        rid=self.a.request('R','A','file.write','/repo/a',Risk.R2,'needed')
        g=self.a.grant_human(rid,'human:user')
        t=ToolDefinition('file.write','1',Risk.R2,True,True)
        self.assertTrue(PolicyEngine().decide(t,'/repo/a',(g,),run_id='R',action_id='A').allowed)
        self.assertFalse(PolicyEngine().decide(t,'/repo/b',(g,),run_id='R',action_id='A').allowed)
    def test_policy_grant_cannot_authorize_r2(self):
        t=ToolDefinition('file.write','1',Risk.R2,True,True)
        g=ApprovalGrant('X',Risk.R4,('*',),('*',),'policy',datetime.now(timezone.utc)+timedelta(hours=1))
        self.assertFalse(PolicyEngine().decide(t,'/repo/a',(g,),run_id='R',action_id='A').allowed)
if __name__=='__main__': unittest.main()
