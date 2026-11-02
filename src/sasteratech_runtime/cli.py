"""Installed command-line entry point for safe local onboarding."""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Sequence

from .local_api import local_status
from .state_paths import resolve_state_dir


PACKAGE_NAME = "sasteratech-agent-runtime"


def package_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "source-tree"


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def doctor_payload(state_dir: Path) -> dict[str, object]:
    return {
        "status": "OK",
        "version": package_version(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "state_dir": str(state_dir),
        "state_dir_exists": state_dir.is_dir(),
        "optional_dependencies": {
            "mcp": _module_available("mcp.server.mcpserver"),
            "keyring": _module_available("keyring"),
        },
        "network_access": "NOT_ATTEMPTED",
        "provider_dispatch": "DISABLED",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sasteratech-runtime")
    parser.add_argument("--version", action="version", version=f"%(prog)s {package_version()}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("doctor", "inspect local readiness without changing state"),
        ("status", "read redacted local runtime status"),
        ("mcp", "serve the read-only MCP adapter over stdio"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("--state-dir", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    state_dir = resolve_state_dir(args.state_dir)
    if args.command == "doctor":
        print(json.dumps(doctor_payload(state_dir), indent=2, sort_keys=True))
        return 0
    if args.command == "status":
        print(json.dumps(local_status(state_dir), indent=2, sort_keys=True))
        return 0
    if args.command == "mcp":
        try:
            from .mcp_server import serve_stdio

            serve_stdio(state_dir)
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
