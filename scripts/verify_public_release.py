"""Fail-closed checks for the publishable source tree; performs no network I/O."""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
import sys
from pathlib import Path

try:
    from manifest_contract import manifest_sha256
except ModuleNotFoundError:  # pragma: no cover - module import form
    from scripts.manifest_contract import manifest_sha256


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sasteratech_runtime.skill_security import scan_skill  # noqa: E402

FORBIDDEN_TOP_LEVEL = {".venv", "evidence", "state", "live_inputs"}
SCANNER_EXCLUDED_TOP_LEVEL = {".git"}
FORBIDDEN_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".db", ".sqlite", ".sqlite3", ".zip"}
TEXT_SUFFIXES = {"", ".py", ".md", ".json", ".jsonl", ".toml", ".txt", ".in", ".ps1", ".sh", ".yml", ".yaml"}
REQUIRED = {
    ".gitignore", ".gitattributes", "README.md", "LICENSE", "NOTICE",
    "COPYRIGHT.md", "TRADEMARKS.md", "SECURITY.md", "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md", "PROVENANCE.md", "THIRD_PARTY_NOTICES.md",
    "RELEASE_CHECKLIST.md", "sbom.cdx.json", "pyproject.toml",
    "requirements/runtime-lock.txt", "src/sasteratech_runtime/__init__.py",
    "src/sasteratech_runtime/skill_security.py", "scripts/verify_skill_security.py",
    "schemas/skill_scan_report.schema.json", "config/skill_security.json",
    "docs/SKILL_SECURITY_GATE.md", ".github/workflows/skill-security.yml",
}


def lock_components() -> dict[str, str]:
    pattern = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s;\\]+)")
    components: dict[str, str] = {}
    for line in (ROOT / "requirements" / "runtime-lock.txt").read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if match:
            components[match.group(1).lower()] = match.group(2)
    return components


def eligible_for_manifest(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if relative.parts and relative.parts[0] in SCANNER_EXCLUDED_TOP_LEVEL:
        return False
    if path.name in {"MANIFEST.sha256", "public_release_verification.json"}:
        return False
    if any(part in FORBIDDEN_PARTS | FORBIDDEN_TOP_LEVEL for part in relative.parts):
        return False
    if any(part.endswith(".egg-info") for part in relative.parts):
        return False
    return path.suffix.lower() not in FORBIDDEN_SUFFIXES


def main() -> None:
    failures: list[str] = []
    missing = sorted(item for item in REQUIRED if not (ROOT / item).is_file())
    failures.extend(f"missing required file: {item}" for item in missing)

    old_identity = "omega" + "_harness"
    old_display = "omega" + " harness"
    machine_patterns = (re.compile(r"[A-Za-z]:\\Users\\", re.I), re.compile(r"[A-Za-z]:\\Omega", re.I))
    secret_patterns = (
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    )

    for top_level in FORBIDDEN_TOP_LEVEL:
        if (ROOT / top_level).exists():
            failures.append(f"forbidden top-level path exists: {top_level}")

    for path in ROOT.rglob("*"):
        if path.is_symlink():
            failures.append(f"symbolic link is not allowed: {path.relative_to(ROOT)}")
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative.parts and relative.parts[0] in SCANNER_EXCLUDED_TOP_LEVEL:
            continue
        if any(part in FORBIDDEN_PARTS for part in relative.parts):
            failures.append(f"generated cache included: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden generated/private file: {relative}")
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"Dockerfile", "LICENSE", "NOTICE"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"unexpected non-UTF-8 file: {relative}")
            continue
        lowered = text.lower()
        if old_identity in lowered or old_display in lowered:
            failures.append(f"retired public identity remains in: {relative}")
        if any(pattern.search(text) for pattern in machine_patterns):
            failures.append(f"machine-specific absolute path in: {relative}")
        if any(pattern.search(text) for pattern in secret_patterns):
            failures.append(f"possible secret or private key in: {relative}")

    if (ROOT / "pyproject.toml").is_file():
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        if project.get("name") != "sasteratech-agent-runtime":
            failures.append("pyproject project name is not canonical")
        if project.get("license") != "Apache-2.0":
            failures.append("pyproject licence is not Apache-2.0")

    if (ROOT / "LICENSE").is_file():
        licence = (ROOT / "LICENSE").read_text(encoding="utf-8")
        if "Apache License" not in licence or "Version 2.0, January 2004" not in licence:
            failures.append("LICENSE is not recognizable Apache-2.0 text")

    security_policy = ROOT / "config" / "skill_security.json"
    if security_policy.is_file() and (ROOT / "skills").is_dir():
        skill_directories = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
        if not skill_directories:
            failures.append("no bundled skills found for deterministic security gate")
        for skill_directory in skill_directories:
            report = scan_skill(skill_directory, security_policy)
            if report["verdict"] != "PASS":
                failures.append(
                    f"skill security gate {report['verdict']}: {skill_directory.name}"
                )

    locked = lock_components()
    if (ROOT / "sbom.cdx.json").is_file():
        sbom = json.loads((ROOT / "sbom.cdx.json").read_text(encoding="utf-8"))
        components = {item["name"].lower(): item for item in sbom.get("components", [])}
        if set(components) != set(locked):
            failures.append("SBOM component set does not equal runtime lock")
        for name, version in locked.items():
            component = components.get(name, {})
            if component.get("version") != version:
                failures.append(f"SBOM version mismatch: {name}")
            if not component.get("licenses"):
                failures.append(f"SBOM licence missing: {name}")

    manifest = ROOT / "MANIFEST.sha256"
    if manifest.is_file():
        recorded: dict[str, str] = {}
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if line.strip():
                digest, relative = line.split("  ", 1)
                recorded[relative] = digest
        expected_paths = {
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and eligible_for_manifest(path)
        }
        if set(recorded) != expected_paths:
            failures.append("manifest path set does not equal publishable file set")
        for relative, digest in recorded.items():
            path = ROOT / relative
            if path.is_file() and manifest_sha256(path) != digest:
                failures.append(f"manifest digest mismatch: {relative}")
    else:
        failures.append("MANIFEST.sha256 is missing")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "publishable_files": sum(1 for path in ROOT.rglob("*") if path.is_file() and eligible_for_manifest(path)),
        "locked_packages": len(locked),
        "failures": sorted(set(failures)),
    }
    print(json.dumps(result, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

