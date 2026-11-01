import sys,pathlib,tempfile,unittest,os,json
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.live_validation import parse_named_models,normalize_exact_output,environment_snapshot

class LiveValidationTests(unittest.TestCase):
    def test_model_parser(self):
        self.assertEqual(parse_named_models(['a=openai:x','b=anthropic:y']),[('a','openai:x'),('b','anthropic:y')])
        with self.assertRaises(ValueError): parse_named_models(['bad'])
    def test_normalize_exact_output(self):
        self.assertEqual(normalize_exact_output('"SASTERATECH_OK"'),'SASTERATECH_OK')
        self.assertEqual(normalize_exact_output('```\nSASTERATECH_OK\n```'),'SASTERATECH_OK')
    def test_environment_does_not_capture_secret_value(self):
        old=os.environ.get('OPENAI_API_KEY'); os.environ['OPENAI_API_KEY']='SUPERSECRET'
        try:
            x=environment_snapshot(pathlib.Path(__file__).parents[1])
            blob=json.dumps(x)
            self.assertNotIn('SUPERSECRET',blob)
            self.assertTrue(x['credential_presence']['OPENAI_API_KEY_present'])
        finally:
            if old is None: os.environ.pop('OPENAI_API_KEY',None)
            else: os.environ['OPENAI_API_KEY']=old
    def test_environment_captures_deepseek_presence_only(self):
        old=os.environ.get('DEEPSEEK_API_KEY'); os.environ['DEEPSEEK_API_KEY']='DEEPSEEK_SECRET'
        try:
            x=environment_snapshot(pathlib.Path(__file__).parents[1]); blob=json.dumps(x)
            self.assertNotIn('DEEPSEEK_SECRET',blob)
            self.assertTrue(x['credential_presence']['DEEPSEEK_API_KEY_present'])
        finally:
            if old is None: os.environ.pop('DEEPSEEK_API_KEY',None)
            else: os.environ['DEEPSEEK_API_KEY']=old
if __name__=='__main__': unittest.main()
