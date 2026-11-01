import pathlib,unittest

ROOT=pathlib.Path(__file__).parents[1]

class EvidenceLineageTests(unittest.TestCase):
    def test_runtime_lock_is_tracked_and_hashed(self):
        lock=ROOT/'requirements'/'runtime-lock.txt'
        self.assertTrue(lock.exists())
        self.assertIn('--hash=',lock.read_text(encoding='utf-8'))
        self.assertIn('requirements/runtime-lock.txt',(ROOT/'MANIFEST.sha256').read_text(encoding='utf-8'))
    def test_live_pack_creates_an_immutable_run_manifest(self):
        text=(ROOT/'scripts'/'run_live_validation_pack.py').read_text(encoding='utf-8')
        self.assertIn("run_dir.mkdir(parents=True)",text)
        self.assertIn("'retry_performed':False",text)
        self.assertIn("RUN_MANIFEST.json",text)
    def test_export_requires_named_completed_run(self):
        text=(ROOT/'scripts'/'export_live_evidence.py').read_text(encoding='utf-8')
        self.assertIn("add_argument('--run-id',required=True)",text)
        self.assertIn("only one complete v1.0.0 run may be exported",text)
    def test_gate_uses_imported_pointer_not_local_live_output(self):
        text=(ROOT/'scripts'/'evaluate_v1_gate.py').read_text(encoding='utf-8')
        self.assertIn('CURRENT_IMPORTED_RUN.json',text)
        self.assertNotIn("ROOT/'evidence'/'live'",text)

if __name__=='__main__': unittest.main()
