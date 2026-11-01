import sys,pathlib,tempfile,unittest,sqlite3
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import *
from sasteratech_runtime.repository import RunRepository

class MigrationFailClosedTests(unittest.TestCase):
    def test_v2_db_migrates_to_v3(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'old.db'; c=sqlite3.connect(p)
            c.execute('CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)')
            c.execute("INSERT INTO schema_migrations VALUES(2,'old')")
            c.commit(); c.close()
            s=SQLiteStore(p)
            self.assertEqual(s.conn.execute('SELECT max(version) v FROM schema_migrations').fetchone()['v'],5)
            tables={r[0] for r in s.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertIn('tool_effects',tables); self.assertIn('approval_requests',tables); self.assertIn('approval_bindings',tables)
            s.close()
    def test_required_judge_failure_escalates_not_executes(self):
        with tempfile.TemporaryDirectory() as td:
            s=SQLiteStore(pathlib.Path(td)/'x.db'); RunRepository(s).create('R','BUILD','STATE_0_READ_ONLY_AUDIT')
            reg=ExecutableToolRegistry(); called=[]
            tool=ToolDefinition('file.write','1',Risk.R2,True,True)
            reg.register(ToolRuntimeSpec(tool,lambda a:called.append(1),readback=lambda a,r:1,verify_effect=lambda a,r,o:True,semantic_judge_required=True))
            class Broken(SemanticRiskJudge):
                def judge(self,*x): raise RuntimeError('down')
            ap=ApprovalService(s); intent=ActionIntent('b',Role.BUILDER,'file.write','/repo/a',Risk.R2,'x')
            out=ToolGateway(reg,store=s,approval_service=ap,risk_judge=Broken()).execute('R',intent,{})
            self.assertEqual(out.status,'APPROVAL_REQUIRED'); self.assertEqual(called,[]); self.assertIsNotNone(out.approval_request_id)
            s.close()
    def test_unbound_manual_r2_grant_rejected(self):
        from datetime import datetime,timedelta,timezone
        tool=ToolDefinition('file.write','1',Risk.R2,True,True)
        g=ApprovalGrant('manual',Risk.R2,('file.write',),('/repo/a',),'human',datetime.now(timezone.utc)+timedelta(hours=1))
        self.assertFalse(PolicyEngine().decide(tool,'/repo/a',(g,),run_id='R',action_id='A').allowed)
if __name__=='__main__': unittest.main()
