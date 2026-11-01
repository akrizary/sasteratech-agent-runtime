import json,pathlib,sys,tempfile,threading,unittest,urllib.error,urllib.request
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.local_api import LocalApiAuth, create_server

class LocalApiTests(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parents[1]); self.root=pathlib.Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def test_auth_and_loopback_enforcement(self):
        auth=LocalApiAuth(self.root/'auth.json'); token=auth.initialize()
        self.assertTrue(auth.verify(token)); self.assertFalse(auth.verify('wrong'))
        with self.assertRaises(ValueError): create_server('0.0.0.0',8787,auth,self.root)
    def test_token_is_not_persisted_raw(self):
        auth=LocalApiAuth(self.root/'auth.json'); token=auth.initialize()
        self.assertNotIn(token,(self.root/'auth.json').read_text())
        self.assertIn('token_sha256',json.loads((self.root/'auth.json').read_text()))

    def test_loopback_http_contract_never_dispatches_provider(self):
        auth=LocalApiAuth(self.root/'auth.json'); token=auth.initialize()
        server=create_server('127.0.0.1',0,auth,self.root)
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            self.assertEqual(json.loads(urllib.request.urlopen(base+'/v1/health').read())['provider_dispatch'],'DISABLED')
            with self.assertRaises(urllib.error.HTTPError): urllib.request.urlopen(base+'/v1/status')
            req=urllib.request.Request(base+'/v1/runs',data=json.dumps({'mode':'DRAFT','model':'deepseek:deepseek-flash','dispatch':False}).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
            self.assertEqual(json.loads(urllib.request.urlopen(req).read())['status'],'DRAFT_READY')
            denied=urllib.request.Request(base+'/v1/runs',data=json.dumps({'mode':'DRAFT','model':'deepseek:deepseek-flash','dispatch':True}).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
            with self.assertRaises(urllib.error.HTTPError) as error: urllib.request.urlopen(denied)
            self.assertEqual(error.exception.code,403)
        except urllib.error.URLError as error:
            if getattr(error.reason,'winerror',None)==10013:
                self.skipTest('sandbox forbids loopback client sockets')
            raise
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)

if __name__=='__main__': unittest.main()
