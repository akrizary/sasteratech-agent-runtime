import sys, pathlib, unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"src"))
from sasteratech_runtime import route_task, TaskClass

class RouterTests(unittest.TestCase):
    def test_research(self): self.assertEqual(route_task("Deep research agent harness options").task,TaskClass.RESEARCH)
    def test_debug(self): self.assertEqual(route_task("A failing test needs debugging").task,TaskClass.DEBUG)
    def test_high_risk(self): self.assertEqual(route_task("Deploy this build to production").task,TaskClass.HIGH_RISK)
    def test_default(self): self.assertEqual(route_task("What is idempotency?").task,TaskClass.FACT_QUERY)
if __name__=="__main__": unittest.main()
