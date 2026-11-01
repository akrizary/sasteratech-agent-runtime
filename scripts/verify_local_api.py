"""Verify local API authentication without echoing or persisting the token."""
import json
import urllib.error
import urllib.request

from pathlib import Path
import sys
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.local_api import LocalApiTokenVault
token = LocalApiTokenVault().get()
if not token: raise SystemExit("No local API token exists in Windows Credential Manager. Initialize first.")
request = urllib.request.Request(
    "http://127.0.0.1:8787/v1/status",
    headers={"Authorization": f"Bearer {token}"},
)
try:
    with urllib.request.urlopen(request, timeout=5) as response:
        status = json.loads(response.read().decode("utf-8"))
except urllib.error.HTTPError as error:
    raise SystemExit(f"Local API verification failed: HTTP {error.code}") from error
except urllib.error.URLError as error:
    raise SystemExit("Local API verification failed: API is not reachable on 127.0.0.1:8787") from error
finally:
    token = ""

if status.get("provider_dispatch") != "DISABLED" or status.get("network_scope") != "LOOPBACK_ONLY":
    raise SystemExit("Local API verification failed: unsafe runtime state")
print("PASS: authenticated local API status; loopback-only; provider dispatch disabled.")
