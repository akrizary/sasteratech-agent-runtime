# Phase B-Lite Local API runbook

The Phase B-Lite API is private to the current machine. It binds only to `127.0.0.1`, has no tool endpoints, and provider dispatch is disabled.

## Initialise local client authentication

Run once:

```powershell
.\.venv\Scripts\python.exe scripts\initialize_local_api.py
```

The token is stored in Windows Credential Manager and is not printed. A future local client retrieves it through the same OS-protected credential boundary; never put it in a project file, Git repository, or chat transcript.

## Start the API

```powershell
.\.venv\Scripts\python.exe scripts\run_local_api.py
```

The only permitted bind address is `127.0.0.1`. Supplying `0.0.0.0`, a LAN IP, or a hostname is rejected.

## Contract

| Endpoint | Authentication | Result |
|---|---|---|
| `GET /v1/health` | none | confirms loopback API and that provider dispatch is disabled |
| `GET /v1/status` | bearer local token | redacted BYOK/budget/kill-switch status |
| `POST /v1/runs` | bearer local token | accepts a bounded `READ_ONLY` or `DRAFT` contract only; does not call a provider |

`POST /v1/runs` rejects `dispatch: true` with `PROVIDER_DISPATCH_DISABLED`.

## Stop

Press `Ctrl+C`. No provider job is queued or executed by this API.
