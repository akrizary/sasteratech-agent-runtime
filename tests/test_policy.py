import sys, pathlib, unittest
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"src"))
from sasteratech_runtime import PolicyEngine,Risk,ToolDefinition,ApprovalGrant

class PolicyTests(unittest.TestCase):
    def setUp(self): self.engine=PolicyEngine()
    def test_r0(self):
        t=ToolDefinition("file.read","1",Risk.R0,False,False)
        self.assertTrue(self.engine.decide(t,"/repo/a.txt").allowed)
    def test_r2_block(self):
        t=ToolDefinition("file.write","1",Risk.R2,True,True)
        d=self.engine.decide(t,"/repo/a.txt")
        self.assertFalse(d.allowed); self.assertTrue(d.needs_approval)
    def test_scoped(self):
        t=ToolDefinition("file.write","1",Risk.R2,True,True)
        g=ApprovalGrant("APR-1",Risk.R2,("file.write",),("/repo/**",),"human",datetime.now(timezone.utc)+timedelta(hours=1),None,"RUN","ACT")
        self.assertTrue(self.engine.decide(t,"/repo/a.txt",(g,),run_id="RUN",action_id="ACT").allowed)
        self.assertFalse(self.engine.decide(t,"/other/a.txt",(g,),run_id="RUN",action_id="ACT").allowed)
    def test_llm_grant_invalid(self):
        t=ToolDefinition("file.write","1",Risk.R2,True,True)
        g=ApprovalGrant("APR-X",Risk.R4,("*",),("*",),"llm")
        self.assertFalse(self.engine.decide(t,"/repo/a.txt",(g,),run_id="RUN",action_id="ACT").allowed)
if __name__=="__main__": unittest.main()
