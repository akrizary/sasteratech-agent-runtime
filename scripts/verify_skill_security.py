"""Fail-closed deterministic scan of every bundled skill; no network I/O."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sasteratech_runtime.skill_security import scan_skill  # noqa: E402


def main() -> None:
    policy = ROOT / "config" / "skill_security.json"
    reports = [scan_skill(path, policy) for path in sorted((ROOT / "skills").iterdir()) if path.is_dir()]
    result = {
        "status": "PASS" if reports and all(report["verdict"] == "PASS" for report in reports) else "FAIL",
        "scanner": "sasteratech-capability-gate",
        "reports": reports,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
