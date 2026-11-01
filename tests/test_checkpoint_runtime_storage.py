import sys,pathlib,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import SQLiteStore
from sasteratech_runtime.repository import RunRepository
from sasteratech_runtime.checkpoints import CheckpointRepository
class CheckpointTests(unittest.TestCase):
    def test_schema_v2_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            s=SQLiteStore(pathlib.Path(td)/'x.db'); self.assertEqual(s.conn.execute('SELECT max(version) v FROM schema_migrations').fetchone()['v'],5); RunRepository(s).create('R','RESEARCH','STATE_0_READ_ONLY_AUDIT'); c=CheckpointRepository(s); c.save('R',{'x':1},stable=False); good=c.save('R',{'x':2},runtime_ref='rid',stable=True); latest=c.latest('R'); self.assertEqual(latest['checkpoint_id'],good); self.assertEqual(latest['runtime_ref'],'rid'); s.close()
if __name__=='__main__': unittest.main()
