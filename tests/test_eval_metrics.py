import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.evals.metrics import classification_metrics,skill_reach_metrics

class EvalMetricsTests(unittest.TestCase):
    def test_classification(self):
        m=classification_metrics(['A','A','B'],['A','B','B'])
        self.assertAlmostEqual(m['accuracy'],2/3)
        self.assertIn('A',m['per_class'])
    def test_skill_reach(self):
        m=skill_reach_metrics([
          {'expected_skill':'S','trajectory':['X','S']},
          {'expected_skill':None,'trajectory':[],'out_of_scope':True}
        ])
        self.assertEqual(m['trajectory_reachability'],1.0)
        self.assertAlmostEqual(m['step_efficiency_mrr'],0.5)
        self.assertEqual(m['out_of_scope_restraint'],1.0)
if __name__=='__main__': unittest.main()
