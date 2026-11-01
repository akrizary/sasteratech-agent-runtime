import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from manifest_contract import manifest_sha256


class ManifestContractTests(unittest.TestCase):
    def test_text_hash_is_stable_across_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "example.md"
            path.write_bytes(b"alpha\nbeta\n")
            lf_digest = manifest_sha256(path)
            path.write_bytes(b"alpha\r\nbeta\r\n")
            self.assertEqual(manifest_sha256(path), lf_digest)

    def test_binary_hash_preserves_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "example.png"
            path.write_bytes(b"alpha\nbeta\n")
            lf_digest = manifest_sha256(path)
            path.write_bytes(b"alpha\r\nbeta\r\n")
            self.assertNotEqual(manifest_sha256(path), lf_digest)


if __name__ == "__main__":
    unittest.main()
