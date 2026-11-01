$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$Python = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "python" }
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw "uv is required to generate the hashed runtime lock before live validation." }
& $Python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
& .\.venv\Scripts\python.exe scripts\generate_runtime_lock.py
& .\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements\runtime-lock.txt
try { & .\.venv\Scripts\python.exe scripts\capture_live_environment.py } catch { }
& .\.venv\Scripts\python.exe scripts\probe_runtime_import.py
