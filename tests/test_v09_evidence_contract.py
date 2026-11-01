import sys,pathlib,tempfile,unittest,hashlib
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"src"))
from sasteratech_runtime.live_validation import sha256_file,manifest_fingerprint,verify_manifest,live_run_directory

class EvidenceContractTests(unittest.TestCase):
    def test_sha256(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"x"; p.write_bytes(b"abc")
            self.assertEqual(sha256_file(p),hashlib.sha256(b"abc").hexdigest())
    def test_manifest_fingerprint(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td); m=root/"MANIFEST.sha256"; m.write_text("abc\n",encoding="utf-8",newline="\n")
            self.assertEqual(manifest_fingerprint(root),hashlib.sha256(b"abc\n").hexdigest())
    def test_verify_manifest_detects_change(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td); f=root/"a.txt"; f.write_text("a",encoding="utf-8")
            h=hashlib.sha256(f.read_bytes()).hexdigest(); (root/"MANIFEST.sha256").write_text(f"{h}  a.txt\n",encoding="utf-8")
            self.assertTrue(verify_manifest(root)["valid"])
            f.write_text("b",encoding="utf-8")
            self.assertFalse(verify_manifest(root)["valid"])
    def test_live_run_directory_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            self.assertEqual(live_run_directory(root,'run-1'),root/'evidence'/'live_runs'/'run-1')
            with self.assertRaises(ValueError): live_run_directory(root,'../escape')
if __name__=="__main__": unittest.main()
