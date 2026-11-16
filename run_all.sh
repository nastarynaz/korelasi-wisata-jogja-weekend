#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
"$PYTHON_BIN" src/build_tourism_notebook.py
"$PYTHON_BIN" src/execute_tourism_notebook.py
