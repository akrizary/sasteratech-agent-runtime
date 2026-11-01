import sys,pathlib,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import SQLiteStore
from sasteratech_runtime.repository import RunRepository
from sasteratech_runtime.effects import EffectLedger,ReplayBlocked
from sasteratech_runtime.security_models import EffectStatus
class T(unittest.TestCase):
    def test_verified_non_idempotent_cannot_replay(self):
        with tempfile.TemporaryDirectory() as td:
            s=SQLiteStore(pathlib.Path(td)/'x.db'); RunRepository(s).create('R','BUILD','STATE_0_READ_ONLY_AUDIT'); e=EffectLedger(s)
            row,reused=e.reserve('R','A','file.write','/x','K',False,{})
            e.mark(row['effect_id'],EffectStatus.VERIFIED,result={'ok':1},verification={'verified':True})
            with self.assertRaises(ReplayBlocked): e.reserve('R','A','file.write','/x','K',False,{})
            s.close()
if __name__=='__main__': unittest.main()
