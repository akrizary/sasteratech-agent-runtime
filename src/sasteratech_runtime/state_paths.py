"""Portable, side-effect-free state-directory discovery."""

from __future__ import annotations

import os
import sys
from pathlib import Path


STATE_DIR_ENV = "SASTERATECH_STATE_DIR"


def platform_state_dir() -> Path:
    """Return the per-user state location without creating it."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        root = Path(base) if base else Path.home() / "AppData" / "Local"
        return root / "SasteraTech" / "AgentRuntime"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "SasteraTech" / "AgentRuntime"
    base = os.environ.get("XDG_STATE_HOME")
    root = Path(base) if base else Path.home() / ".local" / "state"
    return root / "sasteratech-agent-runtime"


def resolve_state_dir(
    explicit: str | Path | None = None, *, working_directory: Path | None = None
) -> Path:
    """Resolve state with explicit > environment > legacy local > platform precedence."""
    if explicit is not None:
        return Path(explicit).expanduser().resolve(strict=False)
    configured = os.environ.get(STATE_DIR_ENV)
    if configured:
        return Path(configured).expanduser().resolve(strict=False)
    legacy = (working_directory or Path.cwd()) / "state"
    if legacy.is_dir():
        return legacy.resolve(strict=False)
    return platform_state_dir().expanduser().resolve(strict=False)
