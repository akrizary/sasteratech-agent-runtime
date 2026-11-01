"""Build a pure-Python wheel with the standard library for offline verification.

The canonical PEP 517 configuration remains setuptools-based. This helper is a
reproducible, dependency-free validation path for restricted/offline builders.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import re
import tomllib
import zipfile
from pathlib import Path


ROOT = Path(__file__).parents[1]
FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def digest(data: bytes) -> str:
    encoded = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
    return f"sha256={encoded}"


def canonical(value: str) -> str:
    return re.sub(r"[-_.]+", "_", value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    distribution = canonical(project["name"])
    version = project["version"]
    dist_info = f"{distribution}-{version}.dist-info"
    filename = f"{distribution}-{version}-py3-none-any.whl"
    output = args.output_dir / filename

    metadata_lines = [
        "Metadata-Version: 2.4",
        f"Name: {project['name']}",
        f"Version: {version}",
        f"Summary: {project['description']}",
        f"Requires-Python: {project['requires-python']}",
        f"License-Expression: {project['license']}",
    ]
    for author in project.get("authors", []):
        metadata_lines.append(f"Author: {author['name']}")
    for extra, requirements in project.get("optional-dependencies", {}).items():
        normalized_extra = extra.replace("_", "-")
        metadata_lines.append(f"Provides-Extra: {normalized_extra}")
        for requirement in requirements:
            metadata_lines.append(f'Requires-Dist: {requirement}; extra == "{normalized_extra}"')
    metadata_lines.extend(["", (ROOT / "README.md").read_text(encoding="utf-8")])

    wheel_files: dict[str, bytes] = {}
    for source in sorted((ROOT / "src" / "sasteratech_runtime").rglob("*.py")):
        relative = source.relative_to(ROOT / "src").as_posix()
        wheel_files[relative] = source.read_bytes()
    wheel_files[f"{dist_info}/METADATA"] = "\n".join(metadata_lines).encode("utf-8")
    wheel_files[f"{dist_info}/WHEEL"] = (
        "Wheel-Version: 1.0\n"
        "Generator: sasteratech-offline-wheel 1\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n"
    ).encode("utf-8")
    wheel_files[f"{dist_info}/top_level.txt"] = b"sasteratech_runtime\n"
    wheel_files[f"{dist_info}/licenses/LICENSE"] = (ROOT / "LICENSE").read_bytes()

    record_path = f"{dist_info}/RECORD"
    record_buffer = io.StringIO(newline="")
    writer = csv.writer(record_buffer, lineterminator="\n")
    for relative, data in sorted(wheel_files.items()):
        writer.writerow((relative, digest(data), len(data)))
    writer.writerow((record_path, "", ""))
    wheel_files[record_path] = record_buffer.getvalue().encode("utf-8")

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative, data in sorted(wheel_files.items()):
            info = zipfile.ZipInfo(relative, FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)

    print(output)
    print(f"sha256={hashlib.sha256(output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()

