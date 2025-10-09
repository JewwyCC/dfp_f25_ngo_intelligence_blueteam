#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ ! -d "$ROOT_DIR/.venv" ]; then
  echo "Embedded virtual environment not found at $ROOT_DIR/.venv"
  exit 1
fi

source "$ROOT_DIR/.venv/bin/activate"
exec streamlit run "$ROOT_DIR/ngo_dashboard.py"
