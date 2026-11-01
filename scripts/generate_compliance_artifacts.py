"""Generate a CycloneDX SBOM and notices from the hashed runtime lock."""

from __future__ import annotations

import importlib.metadata as metadata
import json
import re
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).parents[1]
LOCK = ROOT / "requirements" / "runtime-lock.txt"

CLASSIFIER_MAP = {
    "Apache Software License": "Apache-2.0",
    "BSD License": "BSD-3-Clause",
    "ISC License (ISCL)": "ISC",
    "MIT License": "MIT",
    "Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "Python Software Foundation License": "PSF-2.0",
    "The Unlicense (Unlicense)": "Unlicense",
}


def locked_packages() -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    pattern = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s;\\]+)")
    for line in LOCK.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if match:
            found[match.group(1).lower()] = match.group(2)
    return sorted(found.items())


def licence_for(distribution: metadata.Distribution) -> str:
    meta = distribution.metadata
    expression = (meta.get("License-Expression") or "").strip()
    if expression:
        return expression
    classifiers = [
        value.rsplit(" :: ", 1)[-1]
        for value in meta.get_all("Classifier", [])
        if value.startswith("License ::")
    ]
    mapped = [CLASSIFIER_MAP[value] for value in classifiers if value in CLASSIFIER_MAP]
    if mapped:
        return " OR ".join(sorted(set(mapped)))
    raw = (meta.get("License") or "").strip()
    upper = raw.upper()
    first_line = raw.splitlines()[0].strip().upper() if raw else ""
    exact_prefixes = (
        ("MIT", "MIT"),
        ("APACHE", "Apache-2.0"),
        ("MPL", "MPL-2.0"),
        ("MOZILLA PUBLIC LICENSE", "MPL-2.0"),
        ("BSD", "BSD-3-Clause"),
        ("ISC", "ISC"),
        ("PYTHON SOFTWARE FOUNDATION", "PSF-2.0"),
        ("UNLICENSE", "Unlicense"),
    )
    for prefix, identifier in exact_prefixes:
        if first_line.startswith(prefix):
            return identifier
    heuristics = (
        ("APACHE", "Apache-2.0"),
        ("MOZILLA PUBLIC LICENSE", "MPL-2.0"),
        ("MIT", "MIT"),
        ("MPL", "MPL-2.0"),
        ("BSD", "BSD-3-Clause"),
        ("ISC", "ISC"),
        ("PYTHON SOFTWARE FOUNDATION", "PSF-2.0"),
        ("UNLICENSE", "Unlicense"),
    )
    for needle, identifier in heuristics:
        if needle in upper:
            return identifier
    raise RuntimeError(f"No normalized licence metadata for {distribution.metadata['Name']}")


def main() -> None:
    components = []
    for locked_name, locked_version in locked_packages():
        distribution = metadata.distribution(locked_name)
        installed_version = distribution.version
        if installed_version != locked_version:
            raise RuntimeError(
                f"Installed version mismatch for {locked_name}: "
                f"{installed_version} != {locked_version}"
            )
        licence = licence_for(distribution)
        license_entry = (
            {"expression": licence}
            if " OR " in licence or " AND " in licence
            else {"license": {"id": licence}}
        )
        components.append(
            {
                "type": "library",
                "name": locked_name,
                "version": locked_version,
                "purl": f"pkg:pypi/{locked_name}@{locked_version}",
                "licenses": [license_entry],
            }
        )

    generated = datetime.now(UTC).replace(microsecond=0).isoformat()
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": "urn:uuid:00000000-0000-4000-8000-000000000011",
        "version": 1,
        "metadata": {
            "timestamp": generated,
            "component": {
                "type": "application",
                "name": "sasteratech-agent-runtime",
                "version": "1.1.0a0",
                "licenses": [{"license": {"id": "Apache-2.0"}}],
            },
        },
        "components": components,
    }
    (ROOT / "sbom.cdx.json").write_text(
        json.dumps(sbom, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    lines = [
        "# Third-Party Notices",
        "",
        "Generated from `requirements/runtime-lock.txt` and installed package metadata.",
        "These packages are dependencies, not vendored source in this repository.",
        "Consult each distribution for its authoritative licence text.",
        "",
        "| Package | Version | Licence metadata |",
        "|---|---:|---|",
    ]
    for component in components:
        licence_block = component["licenses"][0]
        licence = licence_block.get("expression") or licence_block["license"]["id"]
        lines.append(f"| `{component['name']}` | `{component['version']}` | `{licence}` |")
    lines.extend(
        [
            "",
            "## Important redistribution note",
            "",
            "The source repository does not bundle these distributions. Binary, container or",
            "offline redistributions must reassess their actual bundled files and preserve all",
            "applicable licence texts, copyright notices and source-availability obligations.",
            "`certifi` is identified as MPL-2.0 and requires particular attention when its",
            "covered files are redistributed.",
            "",
        ]
    )
    (ROOT / "THIRD_PARTY_NOTICES.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote SBOM and notices for {len(components)} locked packages")


if __name__ == "__main__":
    main()

