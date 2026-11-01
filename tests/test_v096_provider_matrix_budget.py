import pathlib,unittest

ROOT=pathlib.Path(__file__).parents[1]

class ProviderMatrixBudgetTests(unittest.TestCase):
    def test_matrix_uses_approved_512_token_budget(self):
        text=(ROOT/'scripts'/'run_provider_matrix.py').read_text(encoding='utf-8')
        self.assertIn('max_tokens=512,max_seconds=45',text)
        self.assertNotIn('max_tokens=128,max_seconds=45',text)

if __name__=='__main__': unittest.main()
