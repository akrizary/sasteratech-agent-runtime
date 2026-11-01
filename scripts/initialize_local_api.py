from pathlib import Path
import sys
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.local_api import LocalApiAuth, LocalApiTokenVault
auth_path=ROOT/'state'/'local_api_auth.json'
if auth_path.exists(): auth_path.unlink()
vault=LocalApiTokenVault(); vault.delete()
token=LocalApiAuth(auth_path).initialize()
vault.put(token)
token=''
print('Local API token rotated and stored in Windows Credential Manager.')
print('No token value was printed.')
