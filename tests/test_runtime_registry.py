import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import ModelProfile,ModelRegistry,RuntimeRegistry,Role
from sasteratech_runtime.adapters.mock import MockRuntimeAdapter
class RuntimeRegistryTests(unittest.TestCase):
    def test_model_env_resolution_and_role(self):
        p=ModelProfile('research','mock',model_env='MODEL',allowed_roles=(Role.RESEARCHER,)); r=ModelRegistry([p],{Role.RESEARCHER:'research'},env={'MODEL':'mock:model'}); x=r.resolve('research',Role.RESEARCHER); self.assertEqual(x.model_id,'mock:model')
        with self.assertRaises(PermissionError): r.resolve('research',Role.BUILDER)
    def test_runtime_registry(self): self.assertEqual(RuntimeRegistry([MockRuntimeAdapter()]).get('mock').adapter_id,'mock')
if __name__=='__main__': unittest.main()
