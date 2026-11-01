"""Regenerate the canonical package manifest from tracked package files."""
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).parents[1]
EXCLUDED_PARTS = {
    "__pycache__", ".venv", ".git", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "build", "dist", "evidence", "state", "live_inputs",
}
EXCLUDED_NAMES = {"MANIFEST.sha256", "public_release_verification.json"}


def is_manifested(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if path.name in EXCLUDED_NAMES or any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if any(part.endswith(".egg-info") for part in relative.parts):
        return False
    return path.suffix.lower() not in {".pyc", ".pyo", ".db", ".sqlite", ".sqlite3", ".zip"}

files = sorted(
    path for path in ROOT.rglob("*")
    if path.is_file() and is_manifested(path)
)
lines = [f"{sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}" for path in files]
(ROOT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {len(lines)} manifest entries")
