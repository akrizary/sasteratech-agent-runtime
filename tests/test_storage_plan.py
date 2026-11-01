import sys,pathlib,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import SQLiteStore,PlanGraph,PlanTask
class StoragePlanTests(unittest.TestCase):
    def test_sqlite(self):
        with tempfile.TemporaryDirectory() as td:
            s=SQLiteStore(pathlib.Path(td)/'a.db'); v=s.conn.execute('SELECT max(version) v FROM schema_migrations').fetchone()['v']; self.assertEqual(v,5); self.assertEqual(s.conn.execute('PRAGMA journal_mode').fetchone()[0].lower(),'wal'); s.close()
    def test_plan_dependencies(self):
        g=PlanGraph(); g.add_many([PlanTask('A','first'),PlanTask('B','second',dependencies=['A'])]); self.assertEqual([x.task_id for x in g.ready()],['A']); g.start('A'); g.complete('A'); self.assertEqual([x.task_id for x in g.ready()],['B'])
    def test_cycle(self):
        g=PlanGraph()
        with self.assertRaises(ValueError): g.add_many([PlanTask('A','a',dependencies=['B']),PlanTask('B','b',dependencies=['A'])])
if __name__=='__main__': unittest.main()
