import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.local_api import LocalApiAuth, create_server
p=argparse.ArgumentParser(); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=8787); a=p.parse_args()
auth=LocalApiAuth(ROOT/'state'/'local_api_auth.json')
if not (ROOT/'state'/'local_api_auth.json').exists(): raise SystemExit('Initialize local API authentication first.')
server=create_server(a.host,a.port,auth,ROOT/'state')
print(f'SasteraTech local API listening at http://{a.host}:{a.port} (provider dispatch disabled)')
try: server.serve_forever()
except KeyboardInterrupt: pass
finally: server.server_close()
