import sys,pathlib,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import *
from sasteratech_runtime.repository import RunRepository

class EffectTests(unittest.TestCase):
    def test_non_idempotent_unknown_blocks_replay(self):
        with tempfile.TemporaryDirectory() as td:
            s=SQLiteStore(pathlib.Path(td)/'x.db'); RunRepository(s).create('R','BUILD','STATE_0_READ_ONLY_AUDIT')
            e=EffectLedger(s)
            row,_=e.reserve('R','A','external.create','x','KEY',False,{})
            e.mark(row['effect_id'],EffectStatus.UNKNOWN,error='crash')
            with self.assertRaises(ReplayBlocked):
                e.reserve('R','B','external.create','x','KEY',False,{})
            s.close()
if __name__=='__main__': unittest.main()
