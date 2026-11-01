import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.evals.trajectory import TrajectoryEvaluator,TrajectoryRule
from sasteratech_runtime.evals.shadow import ShadowEvaluator

class EvalTraceShadowTests(unittest.TestCase):
    def test_subsequence(self):
        r=TrajectoryEvaluator().evaluate(['a','noise','b'],TrajectoryRule(('a','b'),('deploy',),'b'))
        self.assertTrue(r['passed'])
    def test_forbidden(self):
        r=TrajectoryEvaluator().evaluate(['a','deploy','b'],TrajectoryRule(('a','b'),('deploy',),'b'))
        self.assertFalse(r['passed'])
    def test_shadow_high_risk_fp(self):
        m=ShadowEvaluator().evaluate([{'reference':[],'proposed':['deploy'],'risks':{'deploy':'R4'}}])
        self.assertEqual(m['high_risk_false_positives'],1)
        self.assertEqual(m['precision'],0.0)
if __name__=='__main__': unittest.main()
