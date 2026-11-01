import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.production_drills import ProductionDrills
class T(unittest.TestCase):
    def test_crash_recovery(self): self.assertTrue(ProductionDrills.crash_recovery()['passed'])
    def test_migration_rollback(self): self.assertTrue(ProductionDrills.migration_rollback()['passed'])
if __name__=='__main__': unittest.main()
