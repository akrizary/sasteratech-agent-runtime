"""Windows-local BYOK control-plane primitives.

Phase A intentionally does not perform provider dispatch.  It establishes the
secret, policy, budget, audit, and kill-switch boundaries that a dispatcher
must satisfy before a provider adapter may be enabled.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Protocol

from .secrets import SecretBoundary


class LocalControlError(RuntimeError):
    """Base error that must never include a resolved credential value."""


class CredentialUnavailable(LocalControlError):
    pass


class BudgetExceeded(LocalControlError):
    pass


class DispatchDenied(LocalControlError):
    pass


class OperationMode(str, Enum):
    READ_ONLY = "READ_ONLY"
    DRAFT = "DRAFT"


class CredentialStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    INVALID = "INVALID"


class ReservationState(str, Enum):
    RESERVED = "RESERVED"
    SETTLED = "SETTLED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"
    BLOCKED = "BLOCKED"


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class CredentialMetadata:
    credential_id: str
    provider: str
    masked_suffix: str
    status: CredentialStatus
    created_at: str
    last_test_at: str | None = None
    last_test_status: str | None = None


class CredentialStore(Protocol):
    def put(self, provider: str, secret: str) -> CredentialMetadata: ...
    def get_for_dispatch(self, credential_id: str) -> str: ...
    def disable(self, credential_id: str, reason: str) -> None: ...
    def delete(self, credential_id: str) -> None: ...


class InMemoryCredentialStore:
    """Test double only. It is deliberately not persisted."""

    def __init__(self) -> None:
        self._values: dict[str, str] = {}
        self._metadata: dict[str, CredentialMetadata] = {}

    def put(self, provider: str, secret: str) -> CredentialMetadata:
        if not provider or not secret:
            raise ValueError("provider and secret are required")
        credential_id = f"cred_{uuid.uuid4().hex}"
        metadata = CredentialMetadata(
            credential_id=credential_id,
            provider=provider,
            masked_suffix=f"...{secret[-4:]}",
            status=CredentialStatus.ACTIVE,
            created_at=_now(),
        )
        self._values[credential_id] = secret
        self._metadata[credential_id] = metadata
        return metadata

    def get_for_dispatch(self, credential_id: str) -> str:
        metadata = self._metadata.get(credential_id)
        if metadata is None or metadata.status is not CredentialStatus.ACTIVE:
            raise CredentialUnavailable("credential is unavailable")
        return self._values[credential_id]

    def disable(self, credential_id: str, reason: str) -> None:
        metadata = self._metadata.get(credential_id)
        if metadata is None:
            raise CredentialUnavailable("credential is unavailable")
        self._metadata[credential_id] = CredentialMetadata(
            **{**metadata.__dict__, "status": CredentialStatus.DISABLED}
        )

    def delete(self, credential_id: str) -> None:
        self._values.pop(credential_id, None)
        self._metadata.pop(credential_id, None)

    def metadata(self, credential_id: str) -> CredentialMetadata:
        return self._metadata[credential_id]


class WindowsKeyringCredentialStore:
    """Credential Manager-backed store, activated only on Windows.

    ``keyring`` is optional at import time so offline tests do not need a live
    OS vault. Production enrollment fails closed if the backend is absent or
    recognisably insecure.
    """

    def __init__(self, state_path: Path, environment: str = "local") -> None:
        if os.name != "nt":
            raise CredentialUnavailable("Windows Credential Manager is required for local BYOK")
        try:
            import keyring  # type: ignore
        except ImportError as exc:
            raise CredentialUnavailable("secure keyring backend is not installed") from exc
        backend_name = type(keyring.get_keyring()).__name__.lower()
        rejected = ("fail", "null", "plaintext")
        if any(fragment in backend_name for fragment in rejected):
            raise CredentialUnavailable("secure Windows keyring backend is unavailable")
        self._keyring = keyring
        self._service_prefix = f"sasteratech-harness/{environment}"
        self._db = sqlite3.connect(state_path)
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS credential_metadata (
                credential_id TEXT PRIMARY KEY, provider TEXT NOT NULL, masked_suffix TEXT NOT NULL,
                status TEXT NOT NULL, created_at TEXT NOT NULL, last_test_at TEXT, last_test_status TEXT
            )"""
        )
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def _metadata_for(self, credential_id: str) -> CredentialMetadata | None:
        row = self._db.execute(
            "SELECT credential_id, provider, masked_suffix, status, created_at, last_test_at, last_test_status FROM credential_metadata WHERE credential_id=?",
            (credential_id,),
        ).fetchone()
        return CredentialMetadata(*row[:3], CredentialStatus(row[3]), *row[4:]) if row else None

    def _service(self, provider: str) -> str:
        return f"{self._service_prefix}/{provider}"

    def put(self, provider: str, secret: str) -> CredentialMetadata:
        if not provider or not secret:
            raise ValueError("provider and secret are required")
        credential_id = f"cred_{uuid.uuid4().hex}"
        self._keyring.set_password(self._service(provider), credential_id, secret)
        metadata = CredentialMetadata(
            credential_id=credential_id,
            provider=provider,
            masked_suffix=f"...{secret[-4:]}",
            status=CredentialStatus.ACTIVE,
            created_at=_now(),
        )
        self._db.execute(
            "INSERT INTO credential_metadata VALUES (?, ?, ?, ?, ?, ?, ?)",
            (metadata.credential_id, metadata.provider, metadata.masked_suffix, metadata.status.value, metadata.created_at, None, None),
        )
        self._db.commit()
        return metadata

    def get_for_dispatch(self, credential_id: str) -> str:
        metadata = self._metadata_for(credential_id)
        if metadata is None or metadata.status is not CredentialStatus.ACTIVE:
            raise CredentialUnavailable("credential is unavailable")
        secret = self._keyring.get_password(self._service(metadata.provider), credential_id)
        if not secret:
            raise CredentialUnavailable("credential is unavailable")
        return secret

    def disable(self, credential_id: str, reason: str) -> None:
        metadata = self._metadata_for(credential_id)
        if metadata is None:
            raise CredentialUnavailable("credential is unavailable")
        self._db.execute("UPDATE credential_metadata SET status=? WHERE credential_id=?", (CredentialStatus.DISABLED.value, credential_id))
        self._db.commit()

    def delete(self, credential_id: str) -> None:
        metadata = self._metadata_for(credential_id)
        if metadata:
            self._keyring.delete_password(self._service(metadata.provider), credential_id)
            self._db.execute("DELETE FROM credential_metadata WHERE credential_id=?", (credential_id,))
            self._db.commit()


class BudgetLedger:
    def __init__(self, path: Path) -> None:
        self._db = sqlite3.connect(path)
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS budget_account (
                account_id TEXT PRIMARY KEY, limit_usd REAL NOT NULL CHECK(limit_usd >= 0), enabled INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS budget_reservation (
                reservation_id TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES budget_account(account_id),
                request_id TEXT NOT NULL UNIQUE, reserved_usd REAL NOT NULL CHECK(reserved_usd >= 0),
                state TEXT NOT NULL, created_at TEXT NOT NULL, expires_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS usage_receipt (
                receipt_id TEXT PRIMARY KEY, reservation_id TEXT NOT NULL UNIQUE REFERENCES budget_reservation(reservation_id),
                actual_usd REAL NOT NULL CHECK(actual_usd >= 0), cost_status TEXT NOT NULL, created_at TEXT NOT NULL
            );
            """
        )
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def create_account(self, account_id: str, limit_usd: float) -> None:
        self._db.execute(
            "INSERT INTO budget_account(account_id, limit_usd, enabled) VALUES (?, ?, 1)",
            (account_id, limit_usd),
        )
        self._db.commit()

    def reserve(self, account_id: str, request_id: str, maximum_usd: float, ttl_seconds: int = 300) -> str:
        if maximum_usd < 0:
            raise ValueError("maximum_usd must be non-negative")
        now = datetime.now(UTC)
        expires = now + timedelta(seconds=ttl_seconds)
        with self._db:
            account = self._db.execute(
                "SELECT limit_usd, enabled FROM budget_account WHERE account_id=?", (account_id,)
            ).fetchone()
            if account is None or not account[1]:
                raise BudgetExceeded("budget account is unavailable")
            reserved = self._db.execute(
                "SELECT COALESCE(SUM(reserved_usd), 0) FROM budget_reservation WHERE account_id=? AND state='RESERVED'",
                (account_id,),
            ).fetchone()[0]
            settled = self._db.execute(
                "SELECT COALESCE(SUM(actual_usd), 0) FROM usage_receipt r JOIN budget_reservation b ON b.reservation_id=r.reservation_id WHERE b.account_id=?",
                (account_id,),
            ).fetchone()[0]
            if float(reserved) + float(settled) + maximum_usd > float(account[0]):
                raise BudgetExceeded("budget cap would be exceeded")
            reservation_id = f"res_{uuid.uuid4().hex}"
            self._db.execute(
                "INSERT INTO budget_reservation VALUES (?, ?, ?, ?, ?, ?, ?)",
                (reservation_id, account_id, request_id, maximum_usd, ReservationState.RESERVED.value, now.isoformat(), expires.isoformat()),
            )
        return reservation_id

    def settle(self, reservation_id: str, actual_usd: float, cost_status: str) -> None:
        if actual_usd < 0 or cost_status not in {"PROVIDER_REPORTED", "CALCULATED"}:
            raise ValueError("invalid settlement")
        with self._db:
            row = self._db.execute("SELECT state, reserved_usd FROM budget_reservation WHERE reservation_id=?", (reservation_id,)).fetchone()
            if row is None or row[0] != ReservationState.RESERVED.value:
                raise BudgetExceeded("reservation is not settleable")
            if actual_usd > float(row[1]):
                raise BudgetExceeded("actual cost exceeds reserved maximum")
            self._db.execute("UPDATE budget_reservation SET state=? WHERE reservation_id=?", (ReservationState.SETTLED.value, reservation_id))
            self._db.execute("INSERT INTO usage_receipt VALUES (?, ?, ?, ?, ?)", (f"rec_{uuid.uuid4().hex}", reservation_id, actual_usd, cost_status, _now()))

    def release(self, reservation_id: str) -> None:
        with self._db:
            self._db.execute(
                "UPDATE budget_reservation SET state=? WHERE reservation_id=? AND state=?",
                (ReservationState.RELEASED.value, reservation_id, ReservationState.RESERVED.value),
            )


class KillSwitchStore:
    def __init__(self, path: Path) -> None:
        self._db = sqlite3.connect(path)
        self._db.execute("CREATE TABLE IF NOT EXISTS kill_switch (scope TEXT NOT NULL, value TEXT, PRIMARY KEY(scope, value))")
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def disable(self, scope: str, value: str | None = None) -> None:
        self._db.execute("INSERT OR REPLACE INTO kill_switch(scope, value) VALUES (?, ?)", (scope, value))
        self._db.commit()

    def enable(self, scope: str, value: str | None = None) -> None:
        self._db.execute("DELETE FROM kill_switch WHERE scope=? AND value IS ?", (scope, value))
        self._db.commit()

    def blocks(self, provider: str, model: str, credential_id: str) -> bool:
        markers = (("GLOBAL", None), ("PROVIDER", provider), ("MODEL", model), ("CREDENTIAL", credential_id))
        return any(self._db.execute("SELECT 1 FROM kill_switch WHERE scope=? AND value IS ?", marker).fetchone() for marker in markers)


class AuditLedger:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._previous_hash = self._read_previous_hash()

    def _read_previous_hash(self) -> str | None:
        if not self._path.exists():
            return None
        lines = self._path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return None
        return json.loads(lines[-1])["event_hash"]

    def append(self, event: dict) -> dict:
        event = SecretBoundary().redact(event)
        serialized = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        event_hash = hashlib.sha256(f"{self._previous_hash or ''}:{serialized}".encode("utf-8")).hexdigest()
        record = {"previous_event_hash": self._previous_hash, **event, "event_hash": event_hash}
        with self._path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        self._previous_hash = event_hash
        return record


class LocalProviderController:
    """Pre-dispatch guard. Provider adapters must call this before dispatch."""

    def __init__(self, credentials: CredentialStore, budgets: BudgetLedger, switches: KillSwitchStore, audit: AuditLedger) -> None:
        self._credentials = credentials
        self._budgets = budgets
        self._switches = switches
        self._audit = audit

    def prepare(
        self, *, mode: OperationMode, provider: str, model: str, credential_id: str,
        account_id: str, request_id: str, maximum_cost_usd: float,
    ) -> tuple[str, str]:
        if mode not in {OperationMode.READ_ONLY, OperationMode.DRAFT}:
            raise DispatchDenied("operation mode is not enabled")
        if provider != "deepseek" or model != "deepseek:deepseek-flash":
            raise DispatchDenied("provider or model is not allowlisted")
        if self._switches.blocks(provider, model, credential_id):
            raise DispatchDenied("dispatch blocked by kill switch")
        reservation_id = self._budgets.reserve(account_id, request_id, maximum_cost_usd)
        try:
            secret = self._credentials.get_for_dispatch(credential_id)
        except Exception:
            self._budgets.release(reservation_id)
            raise
        self._audit.append({
            "occurred_at": _now(), "request_id": request_id, "credential_id": credential_id,
            "mode": mode.value, "provider": provider, "model": model, "decision": "ALLOW_DISPATCH",
            "budget_reservation_id": reservation_id,
        })
        return reservation_id, secret

