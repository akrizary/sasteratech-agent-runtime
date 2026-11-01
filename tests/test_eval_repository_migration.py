import sys,pathlib,tempfile,unittest,sqlite3
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime import SQLiteStore

class EvalMigrationTests(unittest.TestCase):
    def test_v3_migrates_to_v4(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'old.db'; c=sqlite3.connect(p)
            c.execute('CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)')
            c.execute("INSERT INTO schema_migrations VALUES(3,'old')"); c.commit(); c.close()
            s=SQLiteStore(p)
            self.assertEqual(s.conn.execute('SELECT max(version) v FROM schema_migrations').fetchone()['v'],5)
            tables={r[0] for r in s.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertIn('eval_runs',tables); self.assertIn('eval_results',tables)
            s.close()
if __name__=='__main__': unittest.main()
