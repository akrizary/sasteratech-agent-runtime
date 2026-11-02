import contextlib
import io
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))

from sasteratech_runtime.cli import main
from sasteratech_runtime.skill_security import report_to_sarif, scan_skill


POLICY = ROOT / "config" / "skill_security.json"


def write_case(root: pathlib.Path, case: dict) -> None:
    (root / "SKILL.md").write_text(case["skill_md"], encoding="utf-8")
    (root / "skill.json").write_text(json.dumps(case["manifest"]), encoding="utf-8")
    with (root / "evals.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in case["evals"]:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    if case.get("extra_binary"):
        (root / "payload.bin").write_bytes(b"\x00\x01\x02")


class SkillSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = [
            json.loads(line)
            for line in (ROOT / "evals" / "datasets" / "skill_security_v1.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_adversarial_corpus_expected_verdicts(self):
        for case in self.cases:
            with self.subTest(case=case["id"]), tempfile.TemporaryDirectory(dir=ROOT) as temporary:
                skill = pathlib.Path(temporary) / case["id"]
                skill.mkdir()
                write_case(skill, case)
                report = scan_skill(skill, POLICY)
                self.assertEqual(report["verdict"], case["expected_verdict"])

    def test_bundled_skills_pass_and_reports_are_deterministic(self):
        for skill in sorted((ROOT / "skills").iterdir()):
            if not skill.is_dir():
                continue
            with self.subTest(skill=skill.name):
                first = scan_skill(skill, POLICY)
                second = scan_skill(skill, POLICY)
                self.assertEqual(first, second)
                self.assertEqual(first["verdict"], "PASS")
                self.assertTrue(first["analysis_complete"])

    def test_missing_contract_file_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            skill = pathlib.Path(temporary) / "missing-evals"
            skill.mkdir()
            (skill / "SKILL.md").write_text("# Missing\n", encoding="utf-8")
            (skill / "skill.json").write_text("{}", encoding="utf-8")
            report = scan_skill(skill, POLICY)
        self.assertEqual(report["verdict"], "REJECT")
        self.assertIn("SCG-ST-001", {item["rule_id"] for item in report["findings"]})

    def test_cli_json_and_sarif_are_machine_readable(self):
        target = ROOT / "skills" / "example_research"
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["scan-skill", str(target), "--policy", str(POLICY)]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["verdict"], "PASS")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["scan-skill", str(target), "--format", "sarif"]), 0)
        sarif = json.loads(output.getvalue())
        self.assertEqual(sarif["version"], "2.1.0")
        self.assertEqual(sarif["runs"][0]["properties"]["verdict"], "PASS")

    def test_sarif_preserves_blocking_finding(self):
        case = next(item for item in self.cases if item["id"] == "embedded-authority")
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            skill = pathlib.Path(temporary) / "unsafe"
            skill.mkdir()
            write_case(skill, case)
            report = scan_skill(skill, POLICY)
        sarif = report_to_sarif(report)
        self.assertEqual(report["verdict"], "REJECT")
        self.assertTrue(any(item["level"] == "error" for item in sarif["runs"][0]["results"]))

    def test_secret_evidence_is_redacted(self):
        case = dict(next(item for item in self.cases if item["id"] == "clean-local-skill"))
        secret = "sk-" + "x" * 24
        case["skill_md"] = f"# Unsafe literal\nPrint {secret}\n"
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            skill = pathlib.Path(temporary) / "secret"
            skill.mkdir()
            write_case(skill, case)
            encoded = json.dumps(scan_skill(skill, POLICY), sort_keys=True)
        self.assertNotIn(secret, encoded)
        self.assertIn("[REDACTED]", encoded)

    def test_oversized_file_fails_closed_without_hashing_it(self):
        case = next(item for item in self.cases if item["id"] == "clean-local-skill")
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            skill = pathlib.Path(temporary) / "oversized"
            skill.mkdir()
            write_case(skill, case)
            (skill / "large.txt").write_bytes(b"a" * 64)
            policy = pathlib.Path(temporary) / "policy.json"
            policy.write_text(json.dumps({"limits": {"max_file_bytes": 32}}), encoding="utf-8")
            report = scan_skill(skill, policy)
        self.assertEqual(report["verdict"], "INCOMPLETE")
        large = next(item for item in report["inventory"] if item["path"] == "large.txt")
        self.assertIsNone(large["sha256"])

    def test_external_workflow_is_static_pinned_and_unprivileged(self):
        workflow = (ROOT / ".github" / "workflows" / "skill-security.yml").read_text(encoding="utf-8")
        self.assertIn("f3b25697d76256998ca9d42c198d256258d4c035", workflow)
        self.assertIn("--no-llm", workflow)
        self.assertIn("--fail-on-findings", workflow)
        self.assertIn("--fail-on-incomplete", workflow)
        self.assertNotIn("--min-coverage", workflow)
        self.assertIn("uv sync --directory \"$RUNNER_TEMP/skillspector\" --frozen --no-dev", workflow)
        self.assertIn("astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertNotIn("API_KEY", workflow)


if __name__ == "__main__":
    unittest.main()
