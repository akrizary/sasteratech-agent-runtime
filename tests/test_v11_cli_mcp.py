import contextlib
import io
import json
import os
import pathlib
import sqlite3
import tempfile
import tomllib
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))

from sasteratech_runtime.cli import main
from sasteratech_runtime.mcp_server import create_mcp_server, validate_run_contract
from sasteratech_runtime.state_paths import resolve_state_dir
from tests.async_support import run_immediate


class CliAndStatePathTests(unittest.TestCase):
    def test_explicit_state_path_precedes_environment_without_creating_it(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            root = pathlib.Path(temporary)
            explicit = root / "explicit"
            with mock.patch.dict(os.environ, {"SASTERATECH_STATE_DIR": str(root / "environment")}):
                self.assertEqual(resolve_state_dir(explicit), explicit.resolve())
            self.assertFalse(explicit.exists())

    def test_doctor_and_empty_status_are_read_only_json(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            state = pathlib.Path(temporary) / "missing-state"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["doctor", "--state-dir", str(state)]), 0)
            doctor = json.loads(output.getvalue())
            self.assertEqual(doctor["network_access"], "NOT_ATTEMPTED")
            self.assertEqual(doctor["provider_dispatch"], "DISABLED")
            self.assertFalse(state.exists())

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["status", "--state-dir", str(state)]), 0)
            status = json.loads(output.getvalue())
            self.assertEqual(status["credentials"], [])
            self.assertEqual(status["provider_dispatch"], "DISABLED")
            self.assertFalse(state.exists())

    def test_packaging_declares_cli_and_exact_mcp_extra(self):
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual(project["scripts"]["sasteratech-runtime"], "sasteratech_runtime.cli:main")
        self.assertEqual(project["optional-dependencies"]["mcp"], ["mcp==2.3.0"])

    def test_status_reads_existing_metadata_database_without_changing_it(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            state = pathlib.Path(temporary) / "state"
            state.mkdir()
            database = state / "local_byok_metadata.db"
            connection = sqlite3.connect(database)
            try:
                connection.execute(
                    "CREATE TABLE credential_metadata ("
                    "credential_id TEXT, provider TEXT, masked_suffix TEXT, status TEXT)"
                )
                connection.execute(
                    "INSERT INTO credential_metadata VALUES (?, ?, ?, ?)",
                    ("cred_redacted", "deepseek", "...1234", "ACTIVE"),
                )
                connection.commit()
            finally:
                connection.close()
            before = database.read_bytes()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["status", "--state-dir", str(state)]), 0)
            status = json.loads(output.getvalue())
            self.assertEqual(status["credentials"], [["deepseek", "...1234", "ACTIVE"]])
            self.assertEqual(database.read_bytes(), before)


class McpContractTests(unittest.TestCase):
    def test_contract_validator_is_fail_closed(self):
        self.assertTrue(validate_run_contract("READ_ONLY", "deepseek:deepseek-flash")["allowed"])
        self.assertFalse(validate_run_contract("READ_ONLY", "deepseek:deepseek-flash", True)["allowed"])
        self.assertFalse(validate_run_contract("WRITE", "deepseek:deepseek-flash")["allowed"])
        self.assertFalse(validate_run_contract("READ_ONLY", "deepseek:other")["allowed"])

    def test_mcp_exports_only_three_read_only_tools(self):
        try:
            import mcp  # noqa: F401
        except ImportError:
            self.skipTest("optional MCP SDK is not installed")
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            server = create_mcp_server(pathlib.Path(temporary) / "state")
            tools = run_immediate(server.list_tools())
        self.assertEqual(
            {tool.name for tool in tools},
            {"runtime_health", "runtime_status", "validate_run_contract"},
        )
        for tool in tools:
            self.assertTrue(tool.annotations.read_only_hint)
            self.assertFalse(tool.annotations.destructive_hint)
            self.assertTrue(tool.annotations.idempotent_hint)
            self.assertFalse(tool.annotations.open_world_hint)


if __name__ == "__main__":
    unittest.main()
