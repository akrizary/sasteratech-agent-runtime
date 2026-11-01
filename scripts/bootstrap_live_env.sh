#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to generate the hashed runtime lock before live validation." >&2
  exit 1
fi
"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python scripts/generate_runtime_lock.py
python -m pip install --require-hashes -r requirements/runtime-lock.txt
python scripts/capture_live_environment.py || true
python scripts/probe_runtime_import.py
