import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.router import route_task
from sasteratech_runtime.models import TaskClass,DomainClass,ProcedureClass,ActionClass,Risk

class RouterV07Tests(unittest.TestCase):
    def test_risk_mention_not_action(self):
        d=route_task('Explain what production deployment means')
        self.assertEqual(d.task,TaskClass.FACT_QUERY); self.assertEqual(d.action,ActionClass.NONE); self.assertEqual(d.risk_floor,Risk.R0)
    def test_actual_deploy(self):
        d=route_task('Deploy this build to production')
        self.assertEqual(d.task,TaskClass.HIGH_RISK); self.assertEqual(d.action,ActionClass.DEPLOY); self.assertEqual(d.risk_floor,Risk.R4)
    def test_creative_review_keeps_domain_task(self):
        d=route_task('Review chapter continuity and canon conflicts')
        self.assertEqual(d.domain,DomainClass.CREATIVE); self.assertEqual(d.procedure,ProcedureClass.REVIEW); self.assertEqual(d.task,TaskClass.CREATIVE)
    def test_research_no_patch(self):
        d=route_task('Research why the test fails; do not change code')
        self.assertEqual(d.task,TaskClass.RESEARCH); self.assertEqual(d.action,ActionClass.NONE)
    def test_file_mutation_axis(self):
        d=route_task('Rename and organize these files')
        self.assertEqual(d.task,TaskClass.FILE); self.assertEqual(d.action,ActionClass.LOCAL_MUTATION); self.assertEqual(d.risk_floor,Risk.R2)
