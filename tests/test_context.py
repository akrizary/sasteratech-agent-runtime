import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import ContextAssembler,ContextItem,ContextAssemblyError
class ContextTests(unittest.TestCase):
    def test_required(self):
        a=ContextAssembler(20); items=[ContextItem('p','12345678','POLICY',required=True),ContextItem('e','abcdefgh','EVIDENCE',priority=100),ContextItem('x','x'*100,'AUX',priority=1)]; out=a.assemble(items); ids=[i.item_id for i in out['selected']]; self.assertIn('p',ids); self.assertIn('e',ids); self.assertNotIn('x',ids)
    def test_overflow(self):
        with self.assertRaises(ContextAssemblyError): ContextAssembler(2).assemble([ContextItem('p','x'*20,'POLICY',required=True)])
if __name__=='__main__': unittest.main()
