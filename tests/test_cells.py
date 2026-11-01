import sys,pathlib,tempfile,unittest,json
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import SQLiteStore,EventLog,ArtifactRegistry,EventIntegrityError,ConfigLoader
from sasteratech_runtime.repository import RunRepository
class CellsTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.root=pathlib.Path(self.td.name); self.store=SQLiteStore(self.root/'o.db'); RunRepository(self.store).create('RUN-1','RESEARCH','STATE_0_READ_ONLY_AUDIT')
    def tearDown(self): self.store.close(); self.td.cleanup()
    def test_event_chain(self):
        log=EventLog(self.store); log.append('RUN-1','run.started',{'a':1}); log.append('RUN-1','plan.updated',{'b':2}); self.assertTrue(log.verify('RUN-1')); self.store.conn.execute("UPDATE events SET payload_json='{}' WHERE run_id='RUN-1' AND seq=1"); self.store.conn.commit();
        with self.assertRaises(EventIntegrityError): log.verify('RUN-1')
    def test_artifact(self):
        f=self.root/'x.txt'; f.write_text('hello'); reg=ArtifactRegistry(self.store); aid=reg.register(f,run_id='RUN-1'); self.assertTrue(reg.verify(aid)['ok']); f.write_text('changed'); self.assertFalse(reg.verify(aid)['ok'])
    def test_config(self):
        p=self.root/'c.json'; p.write_text(json.dumps({'llm_may_grant_high_risk_approval':False,'default_risk_ceiling':'R0','limits':{'context_token_budget':100}})); out=ConfigLoader().load(p,{'SASTERATECH__limits__context_token_budget':'200'}); self.assertEqual(out['limits']['context_token_budget'],200)
if __name__=='__main__': unittest.main()
