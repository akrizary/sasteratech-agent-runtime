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

    def test_private_runtime_material_is_absent(self):
        for relative in (".venv", "evidence", "state", "live_inputs"):
            self.assertFalse((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()

