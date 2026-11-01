import sys,pathlib,json,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.roles import RoleRegistry,Role
ROOT=pathlib.Path(__file__).parents[1]
class RoleManifestTests(unittest.TestCase):
    def test_all_machine_roles_have_manifest(self):
        reg=RoleRegistry()
        manifest_roles={json.loads(p.read_text())['role'] for p in (ROOT/'roles').glob('*.json')}
        runtime_roles={p.role.value for p in reg.all()}
        self.assertEqual(manifest_roles,runtime_roles)
if __name__=='__main__': unittest.main()
