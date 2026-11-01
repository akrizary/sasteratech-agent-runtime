import sys,pathlib,json,hashlib,unittest
ROOT=pathlib.Path(__file__).parents[1]
class FrozenCorpusTests(unittest.TestCase):
    def test_v06_hashes_unchanged(self):
        frozen=json.loads((ROOT/'evals/frozen_v0_6_hashes.json').read_text())['datasets']
        for name,h in frozen.items():
            self.assertEqual(hashlib.sha256((ROOT/'evals/datasets'/name).read_bytes()).hexdigest(),h,name)
