# CLI and read-only MCP quickstart

This alpha adapter lets local Codex and Claude Code sessions inspect the
SasteraTech runtime and validate proposed run contracts. It does not expose
credentials, call a model, dispatch a provider, execute tools, or mutate files.

## Install from source

Create a virtual environment, then install the package with its exact MCP SDK:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
```

On Linux or macOS, use `.venv/bin/python` instead. The published wheel may be
installed with `pip`; MCP remains an optional extra.

## Check the installation

```text
sasteratech-runtime doctor
sasteratech-runtime status
```

Both commands are read-only. State resolution uses `--state-dir` first,
`SASTERATECH_STATE_DIR` second, an existing `./state` directory third, and the
platform user-state directory last. The commands never create the directory.

## Codex

Add this to user or project `config.toml`:

```toml
[mcp_servers.sasteratech]
command = "sasteratech-runtime"
args = ["mcp"]
enabled_tools = ["runtime_health", "runtime_status", "validate_run_contract"]
default_tools_approval_mode = "prompt"
```

Then run `codex mcp list`. If the command is not on `PATH`, replace it with the
absolute path to the virtual environment's `sasteratech-runtime` executable.

## Claude Code

From the project where the adapter should be available:

```text
claude mcp add --transport stdio sasteratech -- sasteratech-runtime mcp
claude mcp list
```

Claude Code may require workspace trust and explicit approval before a
project-scoped server starts. Review the command before approving it.

## Exposed tools

| Tool | Effect |
|---|---|
| `runtime_health` | reports package version and enforced disabled capabilities |
| `runtime_status` | reads redacted local credential metadata, budgets and kill switches |
| `validate_run_contract` | validates a proposal without storing or dispatching it |

All three tools declare read-only, non-destructive, idempotent and closed-world
MCP annotations. Provider dispatch remains disabled even for an accepted
contract.
