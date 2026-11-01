import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import *

class RiskContradictionTests(unittest.TestCase):
    def test_structured_contradiction(self):
        p=[StructuredProposition('1','PACK','price',3.2,'2026-10-29'),StructuredProposition('2','PACK','price',3.4,'2026-10-29')]
        self.assertEqual(len(ContradictionScanner().scan(p)),1)
    def test_different_time_not_conflict(self):
        p=[StructuredProposition('1','PACK','price',3.2,'day1'),StructuredProposition('2','PACK','price',3.4,'day2')]
        self.assertEqual(len(ContradictionScanner().scan(p)),0)
if __name__=='__main__': unittest.main()
