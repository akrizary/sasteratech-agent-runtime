import sys,pathlib,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import SQLiteStore,EventLog,ModelProfile,ModelRegistry,RuntimeRegistry,Role,TaskClass,Risk,TaskPacket,TaskBudget,ContextItem,NervousSystem
from sasteratech_runtime.repository import RunRepository
from sasteratech_runtime.adapters.mock import MockRuntimeAdapter
from tests.async_support import run_immediate
class NervousSystemTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.store=SQLiteStore(pathlib.Path(self.td.name)/'sasteratech.db'); RunRepository(self.store).create('RUN-1','RESEARCH','STATE_0_READ_ONLY_AUDIT')
        p=ModelProfile('research','mock',model_id='mock:model',allowed_roles=(Role.RESEARCHER,)); self.models=ModelRegistry([p],{Role.RESEARCHER:'research'}); self.mock=MockRuntimeAdapter(); self.ns=NervousSystem(self.models,RuntimeRegistry([self.mock]),store=self.store,event_log=EventLog(self.store),context_budget=1000)
    def tearDown(self): self.store.close(); self.td.cleanup()
    def packet(self): return TaskPacket('P1','RUN-1','T1','Research evidence',TaskClass.RESEARCH,Role.RESEARCHER,Risk.R0,requested_tools=('web.read',),budget=TaskBudget(max_tool_calls=2,max_tokens=1000,max_seconds=30,max_model_requests=3))
    def test_execute_persists_runtime_call_checkpoint_events(self):
        out=run_immediate(self.ns.execute(self.packet(),[ContextItem('E1','trusted source text','EVIDENCE',required=True)])); self.assertEqual(out['response'].status.value,'COMPLETE'); self.assertIsNotNone(out['call_id']); self.assertIsNotNone(out['checkpoint_id']); self.assertEqual(self.store.conn.execute('SELECT count(*) n FROM runtime_calls').fetchone()['n'],1); self.assertEqual(self.store.conn.execute('SELECT count(*) n FROM checkpoints').fetchone()['n'],1); self.assertEqual(self.store.conn.execute('SELECT count(*) n FROM events').fetchone()['n'],2)
    def test_role_model_boundary(self):
        p=self.packet(); self.models.register(ModelProfile('build','mock',model_id='x',allowed_roles=(Role.BUILDER,)))
        with self.assertRaises(PermissionError): run_immediate(self.ns.execute(p,model_alias='build'))
if __name__=='__main__': unittest.main()
