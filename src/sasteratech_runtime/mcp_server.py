"""Read-only MCP adapter for local Codex and Claude Code workflows."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .local_api import local_status


PACKAGE_NAME = "sasteratech-agent-runtime"
ALLOWED_MODEL = "deepseek:deepseek-flash"
ALLOWED_MODES = frozenset({"READ_ONLY", "DRAFT"})


def package_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "source-tree"


def runtime_health() -> dict[str, Any]:
    return {
        "status": "OK",
        "version": package_version(),
        "transport": "STDIO",
        "network_scope": "LOCAL_PROCESS",
        "provider_dispatch": "DISABLED",
        "mutation_tools": "NONE",
    }


def validate_run_contract(mode: str, model: str, dispatch: bool = False) -> dict[str, Any]:
    """Validate a proposed contract without storing or dispatching it."""
    if dispatch:
        return {"allowed": False, "code": "PROVIDER_DISPATCH_DISABLED"}
    if mode not in ALLOWED_MODES or model != ALLOWED_MODEL:
        return {"allowed": False, "code": "POLICY_DENIED"}
    return {
        "allowed": True,
        "code": "READ_ONLY_CONTRACT_ACCEPTED",
        "mode": mode,
        "model": model,
        "provider_dispatch": "DISABLED",
    }


def create_mcp_server(state_dir: Path):
    """Create the optional MCP SDK server without making MCP a core dependency."""
    try:
        from mcp.server.mcpserver import MCPServer
        from mcp.types import ToolAnnotations
    except ImportError as exc:  # pragma: no cover - exercised by CLI subprocess installs
        raise RuntimeError(
            "MCP support is not installed; install sasteratech-agent-runtime[mcp]."
        ) from exc

    read_only = ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
    server = MCPServer(
        name="sasteratech-runtime",
        title="SasteraTech Agent Runtime",
        description="Read-only local runtime status and contract validation.",
        instructions=(
            "All tools are local and read-only. Provider dispatch, credential access, "
            "external mutations, and remote network actions are disabled."
        ),
        version=package_version(),
        log_level="ERROR",
    )

    @server.tool(name="runtime_health", annotations=read_only, structured_output=True)
    def runtime_health_tool() -> dict[str, Any]:
        """Report bounded runtime capabilities without network access."""
        return runtime_health()

    @server.tool(name="runtime_status", annotations=read_only, structured_output=True)
    def runtime_status_tool() -> dict[str, Any]:
        """Read redacted local status; never resolve credential values."""
        return local_status(state_dir)

    @server.tool(name="validate_run_contract", annotations=read_only, structured_output=True)
    def validate_run_contract_tool(mode: str, model: str, dispatch: bool = False) -> dict[str, Any]:
        """Validate a proposed run contract without executing or persisting it."""
        return validate_run_contract(mode=mode, model=model, dispatch=dispatch)

    return server


def serve_stdio(state_dir: Path) -> None:
    create_mcp_server(state_dir).run(transport="stdio")
