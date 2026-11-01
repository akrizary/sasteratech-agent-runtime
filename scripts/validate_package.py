"""Validate the source candidate without making network calls or runtime state."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
REQUIRED = {
    "README.md",
    "LICENSE",
    "NOTICE",
    "COPYRIGHT.md",
    "TRADEMARKS.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "PROVENANCE.md",
    "THIRD_PARTY_NOTICES.md",
    "sbom.cdx.json",
    "RELEASE_CHECKLIST.md",
    "pyproject.toml",
    "MANIFEST.sha256",
    "requirements/runtime-lock.txt",
    "src/sasteratech_runtime/__init__.py",
    "scripts/verify_public_release.py",
}


def main() -> None:
    missing = sorted(path for path in REQUIRED if not (ROOT / path).is_file())
    if missing:
        raise SystemExit("FAIL missing required files:\n- " + "\n- ".join(missing))

    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    for path in ROOT.rglob("*.jsonl"):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                try:
                    json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: {exc}") from exc
    for path in ROOT.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    frozen_path = ROOT / "evals" / "frozen_v0_6_hashes.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))["datasets"]
    for name, expected in frozen.items():
        dataset = ROOT / "evals" / "datasets" / name
        actual = hashlib.sha256(dataset.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"FAIL frozen corpus mismatch: {name}")

    mismatches: list[str] = []
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            mismatches.append(relative)
    if mismatches:
        raise SystemExit("FAIL manifest mismatch:\n- " + "\n- ".join(mismatches))

    print("PASS: structure, JSON/JSONL, Python syntax, frozen corpus and manifest")


if __name__ == "__main__":
    main()

