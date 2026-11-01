import sys,pathlib,unittest
ROOT=pathlib.Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.evals import SasteraTechEvalRunner

class EvalRunnerTests(unittest.TestCase):
    def test_runner_produces_all_tiers(self):
        r=SasteraTechEvalRunner(ROOT).run()
        tiers={x.tier.value for x in r.outcomes}
        for prefix in ['T0_','T1_','T2_','T3_','T4_','T5_','T6_','T7_']:
            self.assertTrue(any(x.startswith(prefix) for x in tiers),prefix)
        self.assertIn('routing.accuracy',r.metrics)
        self.assertIn('safety.core_pass_rate',r.metrics)
    def test_memory_gap_is_rectified(self):
        r=SasteraTechEvalRunner(ROOT).run()
        mem=[x for x in r.outcomes if x.case_id=='MEM-005'][0]
        self.assertTrue(mem.passed)
        self.assertIn('valid_from',mem.details['fields'])
        self.assertIn('supersedes',mem.details['fields'])
if __name__=='__main__': unittest.main()
