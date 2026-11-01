import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.telemetry import InMemoryTelemetrySink,redact
class TelemetryTests(unittest.TestCase):
    def test_recursive_redaction(self):
        x=redact({'api_key':'abc','nested':{'access_token':'xyz','ok':1}}); self.assertEqual(x['api_key'],'[REDACTED]'); self.assertEqual(x['nested']['access_token'],'[REDACTED]'); self.assertEqual(x['nested']['ok'],1)
    def test_sink(self):
        s=InMemoryTelemetrySink(); s.emit('x',{'secret':'bad','safe':'yes'}); self.assertEqual(s.events[0]['attributes']['secret'],'[REDACTED]'); self.assertEqual(s.events[0]['attributes']['safe'],'yes')
if __name__=='__main__': unittest.main()
