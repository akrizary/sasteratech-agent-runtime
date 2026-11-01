import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.skill_router import SkillRouter
ROOT=pathlib.Path(__file__).parents[1]
class SkillRouterTests(unittest.TestCase):
    def setUp(self): self.r=SkillRouter(ROOT/'skills')
    def test_research(self): self.assertEqual(self.r.select('deep research agent frameworks'),'sasteratech.research.deep')
    def test_build(self): self.assertEqual(self.r.select('implement the parser fix and test it'),'sasteratech.build.verified')
    def test_out_of_scope(self): self.assertIsNone(self.r.select('rewrite this email politely'))
    def test_deploy_not_skill(self): self.assertIsNone(self.r.select('deploy this branch to production'))
    def test_recovery_research(self): self.assertEqual(self.r.select('complex task recovers to research'),'sasteratech.research.deep')
