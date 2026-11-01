import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.real_shadow import RealShadowEvaluator,RealShadowInputError,validate_live_shadow_case,parse_generated_actions
from sasteratech_runtime.slo import SLOEvaluator
class T(unittest.TestCase):
    def test_high_risk_false_negative_detected(self):
        m=RealShadowEvaluator().evaluate([{'reference':['deploy'],'proposed':[],'risks':{'deploy':'R4'}}])
        self.assertEqual(m['high_risk_false_negatives'],1)
    def test_unconfigured_operational_targets_block(self):
        p={'hard_invariants':{'unauthorized_mutation_count_max':0},'operational_targets':{'latency_p95_ms_max':None}}
        r=SLOEvaluator().evaluate(p,{'unauthorized_mutation_count':0})
        self.assertFalse(r.configured); self.assertFalse(r.passed)
    def test_configured_slo_pass(self):
        p={'hard_invariants':{'unauthorized_mutation_count_max':0},'operational_targets':{'latency_p95_ms_max':500}}
        r=SLOEvaluator().evaluate(p,{'unauthorized_mutation_count':0,'latency_p95_ms':300})
        self.assertTrue(r.passed)
    def test_live_input_rejects_prepopulated_proposal(self):
        with self.assertRaises(RealShadowInputError):
            validate_live_shadow_case({'id':'H-1','prompt':'read report','reference_actions':['read:report'],'proposed':['read:report'],'risks':{'read:report':'R0'},'source':{'kind':'historical'}})
    def test_live_input_and_generated_action_parser(self):
        case=validate_live_shadow_case({'id':'H-1','prompt':'read report','reference_actions':['read:report'],'risks':{'read:report':'R0'},'source':{'kind':'historical'}})
        self.assertEqual(case['id'],'H-1')
        self.assertEqual(parse_generated_actions('{"proposed_actions":["read:report"]}'),['read:report'])
if __name__=='__main__': unittest.main()
