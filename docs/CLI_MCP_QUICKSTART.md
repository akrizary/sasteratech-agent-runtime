# CLI and read-only MCP quickstart

This alpha adapter lets local Codex and Claude Code sessions inspect the
SasteraTech runtime and validate proposed run contracts. It does not expose
credentials, call a model, dispatch a provider, execute tools, or mutate files.

## Install the public alpha release

Create a virtual environment and install the checksum-bound public wheel with
its exact MCP SDK dependency:

```powershell
$wheel = "https://github.com/akrizary/sasteratech-agent-runtime/releases/download/v1.1.0a2/sasteratech_agent_runtime-1.1.0a2-py3-none-any.whl#sha256=adb689e9a75c1b80e473e740ba4e09ae21a55b84145e30e7be363fc10c29edb3"
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install "sasteratech-agent-runtime[mcp] @ $wheel"
```

Linux or macOS:

```bash
wheel='https://github.com/akrizary/sasteratech-agent-runtime/releases/download/v1.1.0a2/sasteratech_agent_runtime-1.1.0a2-py3-none-any.whl#sha256=adb689e9a75c1b80e473e740ba4e09ae21a55b84145e30e7be363fc10c29edb3'
python3 -m venv .venv
.venv/bin/python -m pip install "sasteratech-agent-runtime[mcp] @ ${wheel}"
```

## Install from a source checkout

Create a virtual environment, then install the package with its exact MCP SDK:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
```

The editable form is intended for contributors. End users should prefer the
checksum-bound public wheel above. MCP remains an optional extra; omit `[mcp]`
when only the core CLI is needed.

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
