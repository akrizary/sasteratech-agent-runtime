"""Phase B-Lite localhost-only HTTP boundary.

No endpoint in this module dispatches a model or executes a tool.  It provides
a stable, authenticated contract for a future existing-app adapter.
"""
from __future__ import annotations

import hashlib, hmac, json, secrets, sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


class LocalApiAuth:
    def __init__(self, state_path: Path) -> None:
        self._path = state_path

    def initialize(self) -> str:
        if self._path.exists():
            raise RuntimeError("local API token already initialized")
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).hexdigest()
        self._path.write_text(json.dumps({"token_sha256": digest}), encoding="utf-8")
        return token

    def verify(self, presented: str | None) -> bool:
        if not presented or not self._path.exists():
            return False
        expected = json.loads(self._path.read_text(encoding="utf-8")).get("token_sha256", "")
        actual = hashlib.sha256(presented.encode()).hexdigest()
        return hmac.compare_digest(expected, actual)


class LocalApiTokenVault:
    """Stores the local client token in Windows Credential Manager, not source/state."""
    SERVICE = "sasteratech-harness/local-api"
    ACCOUNT = "local-owner"

    def __init__(self) -> None:
        try:
            import keyring  # type: ignore
        except ImportError as exc:
            raise RuntimeError("keyring is required for local API authentication") from exc
        self._keyring = keyring

    def put(self, token: str) -> None:
        self._keyring.set_password(self.SERVICE, self.ACCOUNT, token)

    def get(self) -> str | None:
        return self._keyring.get_password(self.SERVICE, self.ACCOUNT)

    def delete(self) -> None:
        try: self._keyring.delete_password(self.SERVICE, self.ACCOUNT)
        except Exception: pass


class LocalApiHandler(BaseHTTPRequestHandler):
    server_version = "SasteraTechLocalApi/1.1"

    def _json(self, status: int, body: dict[str, Any]) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(data)

    def _authorized(self) -> bool:
        header = self.headers.get("Authorization", "")
        token = header[7:] if header.startswith("Bearer ") else None
        return self.server.api_auth.verify(token)  # type: ignore[attr-defined]

    def do_GET(self) -> None:
        if self.path == "/v1/health":
            return self._json(HTTPStatus.OK, {"status": "OK", "network_scope": "LOOPBACK_ONLY", "provider_dispatch": "DISABLED"})
        if self.path != "/v1/status":
            return self._json(HTTPStatus.NOT_FOUND, {"code": "NOT_FOUND"})
        if not self._authorized():
            return self._json(HTTPStatus.UNAUTHORIZED, {"code": "UNAUTHORIZED"})
        return self._json(HTTPStatus.OK, self.server.status_provider())  # type: ignore[attr-defined]

    def do_POST(self) -> None:
        if self.path != "/v1/runs":
            return self._json(HTTPStatus.NOT_FOUND, {"code": "NOT_FOUND"})
        if not self._authorized():
            return self._json(HTTPStatus.UNAUTHORIZED, {"code": "UNAUTHORIZED"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 16384: raise ValueError
            body = json.loads(self.rfile.read(size).decode("utf-8"))
        except Exception:
            return self._json(HTTPStatus.BAD_REQUEST, {"code": "INVALID_JSON"})
        if body.get("mode") not in {"READ_ONLY", "DRAFT"} or body.get("model") != "deepseek:deepseek-flash":
            return self._json(HTTPStatus.FORBIDDEN, {"code": "POLICY_DENIED"})
        if body.get("dispatch") is True:
            return self._json(HTTPStatus.FORBIDDEN, {"code": "PROVIDER_DISPATCH_DISABLED"})
        return self._json(HTTPStatus.ACCEPTED, {"status": "DRAFT_READY", "mode": body["mode"], "provider_dispatch": "DISABLED"})

    def log_message(self, fmt: str, *args: object) -> None:
        # Request lines can contain sensitive client data; no default console log.
        return


def local_status(state: Path) -> dict[str, Any]:
    def query(name: str, sql: str) -> list[tuple]:
        db = state / name
        if not db.exists(): return []
        con = sqlite3.connect(db)
        try: return con.execute(sql).fetchall()
        finally: con.close()
    return {
        "network_scope": "LOOPBACK_ONLY", "provider_dispatch": "DISABLED",
        "credentials": query("local_byok_metadata.db", "SELECT provider, masked_suffix, status FROM credential_metadata"),
        "budget_states": query("local_byok_budget.db", "SELECT state,count(*) FROM budget_reservation GROUP BY state"),
        "kill_switches": query("local_byok_switches.db", "SELECT scope,value FROM kill_switch"),
    }


def create_server(host: str, port: int, auth: LocalApiAuth, state: Path) -> ThreadingHTTPServer:
    if host != "127.0.0.1":
        raise ValueError("Phase B-Lite may bind only to 127.0.0.1")
    server = ThreadingHTTPServer((host, port), LocalApiHandler)
    server.api_auth = auth  # type: ignore[attr-defined]
    server.status_provider = lambda: local_status(state)  # type: ignore[attr-defined]
    return server
