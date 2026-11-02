import pathlib
import tomllib
import unittest


ROOT = pathlib.Path(__file__).parents[1]


class PublicReleaseIdentityTests(unittest.TestCase):
    def test_canonical_identity_and_version(self):
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual(project["name"], "sasteratech-agent-runtime")
        self.assertEqual(project["version"], "1.1.0a2")
        self.assertEqual(project["license"], "Apache-2.0")

        runtime = (ROOT / "src" / "sasteratech_runtime" / "live_validation.py").read_text(encoding="utf-8")
        self.assertIn("ARTIFACT_VERSION = '1.1.0a1'", runtime)

    def test_public_install_docs_are_version_and_digest_bound(self):
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        version = project["version"]
        digest = "adb689e9a75c1b80e473e740ba4e09ae21a55b84145e30e7be363fc10c29edb3"
        wheel_url = (
            "https://github.com/akrizary/sasteratech-agent-runtime/releases/download/"
            f"v{version}/sasteratech_agent_runtime-{version}-py3-none-any.whl"
            f"#sha256={digest}"
        )
        for relative in ("README.md", "docs/CLI_MCP_QUICKSTART.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(wheel_url, text, relative)
            self.assertIn("sasteratech-agent-runtime[mcp] @ $wheel", text, relative)

    def test_private_runtime_material_is_absent(self):
        for relative in (".venv", "evidence", "state", "live_inputs"):
            self.assertFalse((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()

