"""Cross-platform content hashing for the public source manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path


TEXT_SUFFIXES = {
    "", ".bat", ".in", ".json", ".jsonl", ".md", ".ps1", ".py",
    ".sh", ".toml", ".txt", ".yaml", ".yml",
}
TEXT_NAMES = {"Dockerfile", "LICENSE", "NOTICE"}


def canonical_manifest_bytes(path: Path) -> bytes:
    """Return stable bytes for hashing across Git checkout line endings."""
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES:
        return data.replace(b"\r\n", b"\n")
    return data


def manifest_sha256(path: Path) -> str:
    return hashlib.sha256(canonical_manifest_bytes(path)).hexdigest()
