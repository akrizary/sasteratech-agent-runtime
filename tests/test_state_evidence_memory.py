import sys, pathlib, unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"src"))
from sasteratech_runtime import StateMachine,RunState,EvidenceLedger,ClaimRecord,TruthStatus,MemoryGovernor
from sasteratech_runtime.memory import MemoryCandidate
from sasteratech_runtime.state import StateTransitionError

class SystemTests(unittest.TestCase):
    def test_invalid_jump(self):
        sm=StateMachine()
        with self.assertRaises(StateTransitionError): sm.transition(RunState.DEPLOY_AUTHORIZED)
    def test_verified_requires_evidence(self):
        led=EvidenceLedger()
        with self.assertRaises(ValueError): led.add_claim(ClaimRecord("C1","done",TruthStatus.VERIFIED,[]))
    def test_fact_requires_evidence(self):
        ok,fail=MemoryGovernor().promotable(MemoryCandidate("M1","X","FACT",source_refs=["S1"]))
        self.assertFalse(ok); self.assertIn("missing evidence for authoritative memory type",fail)
    def test_fact_promotable(self):
        ok,fail=MemoryGovernor().promotable(MemoryCandidate("M1","X","FACT",source_refs=["S1"],evidence_refs=["E1"],writer="audit"))
        self.assertTrue(ok); self.assertEqual(fail,[])
if __name__=="__main__": unittest.main()
