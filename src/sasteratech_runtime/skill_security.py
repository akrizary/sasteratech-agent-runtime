"""Deterministic, dependency-free security gate for local agent skills.

The scanner never imports or executes target code. It reads a bounded local
directory, validates the SasteraTech skill contract, inventories content, and
reports conservative static findings. It is deliberately independent from any
third-party scanner so that release policy does not collapse to one detector.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCANNER_NAME = "sasteratech-capability-gate"
SCHEMA_VERSION = "1.0"
SEVERITY_ORDER = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
REQUIRED_FILES = ("SKILL.md", "skill.json", "evals.jsonl")
TEXT_SUFFIXES = {
    "", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml",
    ".py", ".sh", ".ps1", ".js", ".ts", ".mjs", ".cjs",
}
EXECUTABLE_SUFFIXES = {".py", ".sh", ".ps1", ".js", ".ts", ".mjs", ".cjs"}
RISK_RANK = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4}
CAPABILITY_MINIMUM_RISK = {
    "network.access": 1,
    "file.write": 2,
    "shell.execute": 2,
    "credential.read": 3,
    "deploy.execute": 3,
}
DEFAULT_LIMITS = {
    "max_entries": 4000,
    "max_files": 1000,
    "max_total_bytes": 10 * 1024 * 1024,
    "max_file_bytes": 1024 * 1024,
    "max_depth": 20,
}
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    path: str
    line: int
    message: str
    evidence: str

    def as_dict(self) -> dict[str, Any]:
        canonical = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "path": self.path,
            "line": self.line,
            "message": self.message,
            "evidence": self.evidence,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
        return {**canonical, "fingerprint": "sha256:" + hashlib.sha256(encoded).hexdigest()}


def _finding(
    rule_id: str,
    severity: str,
    path: str,
    message: str,
    *,
    line: int = 0,
    evidence: str = "",
) -> Finding:
    redacted = evidence
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return Finding(rule_id, severity, path, line, message, redacted[:240])


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_policy(path: Path | None) -> dict[str, int]:
    limits = dict(DEFAULT_LIMITS)
    if path is None:
        return limits
    payload = json.loads(path.read_text(encoding="utf-8"))
    configured = payload.get("limits", {})
    for name in limits:
        value = configured.get(name, limits[name])
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"invalid positive integer policy limit: {name}")
        limits[name] = value
    return limits


_CLAUSE_BOUNDARY = re.compile(r"(?:[.;!?]\s*|\b(?:and|but|then|however)\b\s*)", re.I)
_DEFENSIVE_PREFIX = re.compile(
    r"(?:\bdo\s+not|\bdon't|\bmust\s+not|\bnever|\bforbidden\s+to|\bprohibited\s+to)"
    r"\s+(?:[\w-]+\s+){0,4}$",
    re.I,
)


def _match_is_defensive(line: str, match: re.Match[str]) -> bool:
    """Return true only when a negation governs this exact matched clause."""
    clause_start = 0
    for boundary in _CLAUSE_BOUNDARY.finditer(line, 0, match.start()):
        clause_start = boundary.end()
    prefix = " ".join(line[clause_start:match.start()].split())
    return bool(_DEFENSIVE_PREFIX.search(prefix + (" " if prefix else "")))


def _line_findings(path: str, text: str) -> tuple[list[Finding], set[str]]:
    findings: list[Finding] = []
    capabilities: set[str] = set()
    patterns = (
        ("SCG-PI-001", "HIGH", re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions?", re.I), "instruction override"),
        ("SCG-PI-002", "HIGH", re.compile(r"(?:reveal|show|print|send|upload|exfiltrate).{0,100}(?:api[_ -]?key|token|password|secret|credential)", re.I), "secret disclosure or exfiltration instruction"),
        ("SCG-AA-001", "HIGH", re.compile(r"\byou\s+(?:must|are required to)\s+(?:obey|follow|execute)\b", re.I), "embedded authority instruction"),
        ("SCG-DC-001", "HIGH", re.compile(r"(?:rm\s+-rf|remove-item\b.{0,80}-recurse|format\s+[a-z]:|git\s+reset\s+--hard)", re.I), "destructive command instruction"),
        ("SCG-PT-001", "HIGH", re.compile(r"<!--(?:(?!-->).)*(?:ignore|execute|secret|credential|tool)(?:(?!-->).)*-->", re.I), "hidden HTML instruction"),
    )
    capability_patterns = (
        ("network.access", re.compile(r"(?:https?://|\bcurl\b|invoke-webrequest|requests\.|httpx\.|urllib\.|\bsocket\b)", re.I)),
        ("file.write", re.compile(r"(?:file\.write|write_text|write_bytes|apply_patch|open\s*\([^\n]{0,100}['\"](?:w|a|x)[+b]?['\"])", re.I)),
        ("shell.execute", re.compile(r"(?:subprocess\.|os\.system|\bpowershell\b|\bbash\b|shell\.execute)", re.I)),
        ("credential.read", re.compile(r"(?:api[_ -]?key|credential|secret|password|\.env\b|os\.environ|os\.getenv)", re.I)),
        ("deploy.execute", re.compile(r"(?:deploy\.execute|\bgit\s+push\b|\bgh\s+release\b|publish\s+(?:package|release))", re.I)),
    )
    for number, raw in enumerate(text.splitlines(), 1):
        if any(pattern.search(raw) for pattern in SECRET_PATTERNS):
            findings.append(_finding("SCG-SE-001", "CRITICAL", path, "possible secret literal embedded in skill content", line=number, evidence=raw.strip()))
        for rule_id, severity, regex, message in patterns:
            for match in regex.finditer(raw):
                if not _match_is_defensive(raw, match):
                    findings.append(_finding(rule_id, severity, path, message, line=number, evidence=raw.strip()))
        for capability, regex in capability_patterns:
            if any(not _match_is_defensive(raw, match) for match in regex.finditer(raw)):
                capabilities.add(capability)
    if any(character in text for character in ("\u200b", "\u200c", "\u200d", "\u202a", "\u202b", "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069")):
        findings.append(_finding("SCG-OB-001", "HIGH", path, "hidden Unicode control character"))
    if re.search(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{160,}={0,2}(?![A-Za-z0-9+/=])", text):
        findings.append(_finding("SCG-OB-002", "MEDIUM", path, "large encoded payload requires review"))
    return findings, capabilities


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _python_findings(path: str, text: str) -> tuple[list[Finding], set[str], str | None]:
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        return [], set(), f"{path}:{exc.lineno or 0}: Python syntax could not be parsed"
    findings: list[Finding] = []
    capabilities: set[str] = set()
    dangerous = {
        "eval": "dynamic evaluation",
        "exec": "dynamic execution",
        "compile": "runtime compilation",
        "__import__": "dynamic import",
        "os.system": "shell execution",
        "subprocess.run": "subprocess execution",
        "subprocess.call": "subprocess execution",
        "subprocess.Popen": "subprocess execution",
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name in dangerous:
            findings.append(_finding("SCG-AST-001", "HIGH", path, dangerous[name], line=getattr(node, "lineno", 0), evidence=name))
            capabilities.add("shell.execute")
        if name in {"requests.get", "requests.post", "httpx.get", "httpx.post", "urllib.request.urlopen"}:
            capabilities.add("network.access")
        if name in {"os.getenv", "os.environ.get"}:
            capabilities.add("credential.read")
        if name == "open" and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
            mode = str(node.args[1].value)
            if any(marker in mode for marker in ("w", "a", "x", "+")):
                capabilities.add("file.write")
    return findings, capabilities, None


def _validate_manifest(payload: Any) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    if not isinstance(payload, dict):
        return [_finding("SCG-MF-001", "HIGH", "skill.json", "manifest must be a JSON object")], {}
    required_types: dict[str, type] = {
        "id": str,
        "version": str,
        "purpose": str,
        "positive_triggers": list,
        "negative_triggers": list,
        "risk_ceiling": str,
        "workflow": list,
    }
    for field, expected in required_types.items():
        if field not in payload:
            findings.append(_finding("SCG-MF-002", "HIGH", "skill.json", f"missing required field: {field}"))
        elif not isinstance(payload[field], expected):
            findings.append(_finding("SCG-MF-003", "HIGH", "skill.json", f"invalid field type: {field}"))
    for field in ("positive_triggers", "negative_triggers", "workflow", "allowed_tools", "forbidden_tools", "evidence_required", "completion_conditions"):
        if field in payload and (not isinstance(payload[field], list) or any(not isinstance(item, str) or not item.strip() for item in payload[field])):
            findings.append(_finding("SCG-MF-004", "HIGH", "skill.json", f"{field} must contain non-empty strings"))
    if payload.get("risk_ceiling") not in RISK_RANK:
        findings.append(_finding("SCG-MF-005", "HIGH", "skill.json", "risk_ceiling must be R0 through R4"))
    skill_id = payload.get("id")
    if isinstance(skill_id, str) and not re.fullmatch(r"[a-z0-9]+(?:[._-][a-z0-9]+)*", skill_id):
        findings.append(_finding("SCG-MF-006", "MEDIUM", "skill.json", "skill id is not portable lowercase identifier syntax"))
    allowed = set(payload.get("allowed_tools", [])) if isinstance(payload.get("allowed_tools", []), list) else set()
    forbidden = set(payload.get("forbidden_tools", [])) if isinstance(payload.get("forbidden_tools", []), list) else set()
    for tool in sorted(allowed & forbidden):
        findings.append(_finding("SCG-PM-001", "HIGH", "skill.json", f"tool is both allowed and forbidden: {tool}"))
    if any(tool.strip().lower() in {"*", "all", "any"} for tool in allowed if isinstance(tool, str)):
        findings.append(_finding("SCG-PM-002", "HIGH", "skill.json", "wildcard tool permission is not allowed"))
    return findings, payload


def _declared_capabilities(manifest: dict[str, Any]) -> set[str]:
    declared: set[str] = set()
    for raw in manifest.get("allowed_tools", []):
        tool = str(raw).lower()
        if "shell" in tool or "command" in tool:
            declared.add("shell.execute")
        if "web" in tool or "http" in tool or "network" in tool:
            declared.add("network.access")
        if "write" in tool or "patch" in tool:
            declared.add("file.write")
        if "credential" in tool or "secret" in tool or "keyring" in tool:
            declared.add("credential.read")
        if "deploy" in tool or "publish" in tool or "release" in tool:
            declared.add("deploy.execute")
    return declared


def _manifest_content_findings(manifest: dict[str, Any]) -> tuple[list[Finding], set[str]]:
    """Inspect manifest strings while keeping permission declarations declarative."""
    findings: list[Finding] = []
    capabilities: set[str] = set()
    stack: list[tuple[tuple[str, ...], Any]] = [((), manifest)]
    permission_fields = {"allowed_tools", "forbidden_tools"}
    while stack:
        field_path, value = stack.pop()
        if isinstance(value, dict):
            for key in sorted(value, reverse=True):
                stack.append((field_path + (str(key),), value[key]))
        elif isinstance(value, list):
            for index in range(len(value) - 1, -1, -1):
                stack.append((field_path + (str(index),), value[index]))
        elif isinstance(value, str):
            line_items, line_capabilities = _line_findings("skill.json", value)
            findings.extend(line_items)
            if not field_path or field_path[0] not in permission_fields:
                capabilities.update(line_capabilities)
    return findings, capabilities


def _discover_files(
    root: Path,
    limits: dict[str, int],
) -> tuple[list[Path], list[Finding], list[str], bool]:
    """Discover package files without materializing an unbounded directory tree."""
    files: list[Path] = []
    findings: list[Finding] = []
    limitations: list[str] = []
    stack = [root]
    entries_seen = 0

    while stack:
        directory = stack.pop()
        child_directories: list[Path] = []
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    entries_seen += 1
                    if entries_seen > limits["max_entries"]:
                        return [], [], [f"entry count limit exceeded: more than {limits['max_entries']}"], True
                    path = Path(entry.path)
                    relative_path = path.relative_to(root)
                    relative = relative_path.as_posix()
                    try:
                        if entry.is_symlink():
                            findings.append(_finding("SCG-IN-002", "HIGH", relative, "symbolic links are not allowed in skill packages"))
                        elif entry.is_dir(follow_symlinks=False):
                            if len(relative_path.parts) > limits["max_depth"]:
                                limitations.append(f"path depth limit exceeded: {relative}")
                            else:
                                child_directories.append(path)
                        elif entry.is_file(follow_symlinks=False):
                            if len(relative_path.parts) > limits["max_depth"]:
                                limitations.append(f"path depth limit exceeded: {relative}")
                                continue
                            files.append(path)
                            if len(files) > limits["max_files"]:
                                return [], [], [f"file count limit exceeded: more than {limits['max_files']}"], True
                        else:
                            limitations.append(f"unsupported filesystem entry was not inspected: {relative}")
                    except OSError:
                        limitations.append(f"filesystem entry could not be inspected: {relative}")
        except OSError:
            relative = directory.relative_to(root).as_posix() or "."
            limitations.append(f"directory could not be inspected: {relative}")
        stack.extend(sorted(child_directories, key=lambda item: item.as_posix(), reverse=True))

    return sorted(files, key=lambda item: item.relative_to(root).as_posix()), findings, limitations, False


def _validate_evals(text: str, skill_id: str | None) -> list[Finding]:
    findings: list[Finding] = []
    kinds: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except (json.JSONDecodeError, RecursionError):
            findings.append(_finding("SCG-EV-001", "HIGH", "evals.jsonl", "invalid JSONL record", line=line_number))
            continue
        if not isinstance(row, dict) or not isinstance(row.get("input"), str) or row.get("kind") not in {"positive", "negative"}:
            findings.append(_finding("SCG-EV-002", "HIGH", "evals.jsonl", "eval record requires input and positive/negative kind", line=line_number))
            continue
        kinds.add(row["kind"])
        if row["kind"] == "positive" and skill_id and row.get("expected_route") != skill_id:
            findings.append(_finding("SCG-EV-003", "MEDIUM", "evals.jsonl", "positive expected_route does not match skill id", line=line_number))
        if row["kind"] == "negative" and row.get("expected_route") is not None:
            findings.append(_finding("SCG-EV-004", "MEDIUM", "evals.jsonl", "negative case should abstain with null expected_route", line=line_number))
    for required in ("positive", "negative"):
        if required not in kinds:
            findings.append(_finding("SCG-EV-005", "MEDIUM", "evals.jsonl", f"missing {required} eval case"))
    return findings


def _highest_severity(findings: Iterable[Finding]) -> str:
    return max((item.severity for item in findings), key=SEVERITY_ORDER.get, default="INFO")


def scan_skill(target: Path | str, policy_path: Path | None = None) -> dict[str, Any]:
    """Scan one local skill directory and return a deterministic report."""
    supplied = Path(target)
    limits = _load_policy(policy_path)
    findings: list[Finding] = []
    limitations: list[str] = []
    inventory: list[dict[str, Any]] = []
    observed: set[str] = set()
    texts: dict[str, str] = {}

    if not supplied.exists() or not supplied.is_dir() or supplied.is_symlink():
        return {
            "schema_version": SCHEMA_VERSION,
            "scanner": SCANNER_NAME,
            "target": supplied.name or ".",
            "root_sha256": None,
            "verdict": "INCOMPLETE",
            "highest_severity": "HIGH",
            "analysis_complete": False,
            "capabilities_observed": [],
            "finding_counts": {"HIGH": 1},
            "findings": [_finding("SCG-IN-001", "HIGH", ".", "target must be an existing non-symlink local directory").as_dict()],
            "limitations": ["target could not be safely materialized"],
            "inventory": [],
        }

    root = supplied.resolve()
    files, traversal_findings, traversal_limitations, traversal_exhausted = _discover_files(root, limits)
    findings.extend(traversal_findings)
    limitations.extend(traversal_limitations)
    if traversal_exhausted:
        blocking = _finding(
            "SCG-IN-003",
            "HIGH",
            ".",
            "package traversal stopped at a configured resource limit",
        )
        return {
            "schema_version": SCHEMA_VERSION,
            "scanner": SCANNER_NAME,
            "target": root.name,
            "root_sha256": None,
            "verdict": "INCOMPLETE",
            "highest_severity": "HIGH",
            "analysis_complete": False,
            "capabilities_observed": [],
            "finding_counts": {"HIGH": 1},
            "findings": [blocking.as_dict()],
            "limitations": sorted(set(limitations)),
            "inventory": [],
        }

    total_bytes = 0
    for path in files:
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        total_bytes += size
        within_file_limit = size <= limits["max_file_bytes"]
        within_total_limit = total_bytes <= limits["max_total_bytes"]
        digest = _hash_file(path) if within_file_limit and within_total_limit else None
        inventory.append({"path": relative, "bytes": size, "sha256": digest})
        if not within_file_limit:
            limitations.append(f"file size limit exceeded: {relative}")
            continue
        if not within_total_limit:
            limitations.append(f"total byte limit exceeded: {total_bytes}")
            break
        if path.suffix.lower() not in TEXT_SUFFIXES:
            limitations.append(f"unsupported file type was not inspected: {relative}")
            continue
        try:
            texts[relative] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            limitations.append(f"non-UTF-8 file was not inspected: {relative}")

    for required in REQUIRED_FILES:
        if required not in texts:
            findings.append(_finding("SCG-ST-001", "HIGH", required, "required skill contract file is missing or unreadable"))

    manifest: dict[str, Any] = {}
    if "skill.json" in texts:
        try:
            parsed = json.loads(texts["skill.json"])
        except (json.JSONDecodeError, RecursionError):
            findings.append(_finding("SCG-MF-007", "HIGH", "skill.json", "manifest is not valid JSON"))
        else:
            manifest_findings, manifest = _validate_manifest(parsed)
            findings.extend(manifest_findings)
            content_findings, manifest_capabilities = _manifest_content_findings(manifest)
            findings.extend(content_findings)
            observed.update(manifest_capabilities)
    if "evals.jsonl" in texts:
        findings.extend(_validate_evals(texts["evals.jsonl"], manifest.get("id") if manifest else None))

    for relative, text in texts.items():
        if relative in {"skill.json", "evals.jsonl"}:
            continue
        line_items, line_capabilities = _line_findings(relative, text)
        findings.extend(line_items)
        observed.update(line_capabilities)
        suffix = Path(relative).suffix.lower()
        if suffix in EXECUTABLE_SUFFIXES:
            observed.add("shell.execute")
        if suffix == ".py":
            ast_items, ast_capabilities, parse_error = _python_findings(relative, text)
            findings.extend(ast_items)
            observed.update(ast_capabilities)
            if parse_error:
                limitations.append(parse_error)

    if manifest:
        declared = _declared_capabilities(manifest)
        for capability in sorted(observed - declared):
            findings.append(_finding("SCG-PM-003", "HIGH", "skill.json", f"observed capability is not declared in allowed_tools: {capability}"))
        ceiling = RISK_RANK.get(str(manifest.get("risk_ceiling")), -1)
        for capability in sorted(observed):
            minimum = CAPABILITY_MINIMUM_RISK.get(capability, 0)
            if ceiling >= 0 and minimum > ceiling:
                findings.append(_finding("SCG-RC-001", "HIGH", "skill.json", f"{capability} exceeds declared risk ceiling {manifest.get('risk_ceiling')}"))

    unique = {
        (item.rule_id, item.severity, item.path, item.line, item.message, item.evidence): item
        for item in findings
    }
    ordered = sorted(unique.values(), key=lambda item: (-SEVERITY_ORDER[item.severity], item.path, item.line, item.rule_id, item.message))
    highest = _highest_severity(ordered)
    if limitations:
        verdict = "INCOMPLETE"
    elif SEVERITY_ORDER[highest] >= SEVERITY_ORDER["HIGH"]:
        verdict = "REJECT"
    elif SEVERITY_ORDER[highest] >= SEVERITY_ORDER["MEDIUM"]:
        verdict = "CAUTION"
    else:
        verdict = "PASS"
    counts: dict[str, int] = {}
    for item in ordered:
        counts[item.severity] = counts.get(item.severity, 0) + 1
    inventory_encoded = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema_version": SCHEMA_VERSION,
        "scanner": SCANNER_NAME,
        "target": root.name,
        "root_sha256": hashlib.sha256(inventory_encoded).hexdigest(),
        "verdict": verdict,
        "highest_severity": highest,
        "analysis_complete": not limitations,
        "capabilities_observed": sorted(observed),
        "finding_counts": dict(sorted(counts.items())),
        "findings": [item.as_dict() for item in ordered],
        "limitations": sorted(set(limitations)),
        "inventory": inventory,
    }


def report_to_sarif(report: dict[str, Any]) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    level = {"INFO": "note", "LOW": "note", "MEDIUM": "warning", "HIGH": "error", "CRITICAL": "error"}
    for finding in report.get("findings", []):
        rule_id = finding["rule_id"]
        rules.setdefault(rule_id, {"id": rule_id, "name": rule_id, "shortDescription": {"text": finding["message"]}})
        result: dict[str, Any] = {
            "ruleId": rule_id,
            "level": level[finding["severity"]],
            "message": {"text": finding["message"]},
            "partialFingerprints": {"primaryLocationLineHash": finding["fingerprint"]},
        }
        if finding["path"]:
            result["locations"] = [{
                "physicalLocation": {
                    "artifactLocation": {"uri": finding["path"]},
                    "region": {"startLine": max(1, finding["line"] or 1)},
                }
            }]
        results.append(result)
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": SCANNER_NAME, "rules": list(rules.values())}},
            "results": results,
            "properties": {
                "verdict": report.get("verdict"),
                "analysis_complete": report.get("analysis_complete"),
                "root_sha256": report.get("root_sha256"),
            },
        }],
    }
