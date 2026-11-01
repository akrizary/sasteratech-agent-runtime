import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.release_gate import ReleaseGate,GateEvidence,GateState
class T(unittest.TestCase):
    def test_candidate_can_pass_while_production_blocked(self):
        g=ReleaseGate(['a','b'],['live'])
        r=g.evaluate([GateEvidence('a',GateState.PASS),GateEvidence('b',GateState.PASS),GateEvidence('live',GateState.NOT_RUN)])
        self.assertTrue(r.candidate_ready); self.assertFalse(r.production_ready); self.assertIn('live',r.blockers)
    def test_offline_failure_blocks_candidate(self):
        g=ReleaseGate(['a'],[]); r=g.evaluate([GateEvidence('a',GateState.FAIL)])
        self.assertFalse(r.candidate_ready)
if __name__=='__main__': unittest.main()
