#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE_NAME="${1:-ngo_intel_bundle}"
BUNDLE_DIR="$ROOT_DIR/$BUNDLE_NAME"
TMP_DIR="$ROOT_DIR/.bundle_tmp"
VENV_DIR="$TMP_DIR/venv"

echo "==> Preparing bundle workspace"
rm -rf "$BUNDLE_DIR" "$TMP_DIR" "$ROOT_DIR/${BUNDLE_NAME}.zip"
mkdir -p "$BUNDLE_DIR/scripts" "$TMP_DIR"

echo "==> Creating isolated virtual environment"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements.txt"
pip freeze > "$TMP_DIR/requirements.lock"
deactivate

echo "==> Copying project files"
cp "$ROOT_DIR/README.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/requirements.txt" "$BUNDLE_DIR/"
cp "$TMP_DIR/requirements.lock" "$BUNDLE_DIR/"

cp "$ROOT_DIR/ngo_dashboard.py" "$BUNDLE_DIR/"
cp "$ROOT_DIR/master_scraper.py" "$BUNDLE_DIR/"
cp "$ROOT_DIR/master_scraper_data.py" "$BUNDLE_DIR/"
cp "$ROOT_DIR/master_scraper_viz.py" "$BUNDLE_DIR/"

mkdir -p "$BUNDLE_DIR/data"
rsync -a --exclude '__pycache__' --exclude 'session_*' \
  "$ROOT_DIR/data/demo_data" "$BUNDLE_DIR/data/"

rsync -a --exclude '__pycache__' "$ROOT_DIR/scripts" "$BUNDLE_DIR/"

if [ -d "$ROOT_DIR/viz" ]; then
  rsync -a --exclude '__pycache__' "$ROOT_DIR/viz" "$BUNDLE_DIR/"
fi

if [ -d "$ROOT_DIR/auth" ]; then
  rsync -a --exclude 'config/auth.json' "$ROOT_DIR/auth" "$BUNDLE_DIR/"
fi

echo "==> Embedding virtual environment"
cp -R "$VENV_DIR" "$BUNDLE_DIR/.venv"
rm -rf "$TMP_DIR"

echo "==> Creating launch scripts"
cp "$ROOT_DIR/packaging/run_dashboard.sh" "$BUNDLE_DIR/scripts/run_dashboard.sh"
chmod +x "$BUNDLE_DIR/scripts/run_dashboard.sh"
cp "$ROOT_DIR/packaging/run_dashboard.bat" "$BUNDLE_DIR/scripts/run_dashboard.bat"

echo "==> Creating zip archive"
cd "$ROOT_DIR"
rm -f "${BUNDLE_NAME}.zip"
python3 -m zipfile -c "${BUNDLE_NAME}.zip" "$BUNDLE_NAME"

echo "Bundle ready at $ROOT_DIR/${BUNDLE_NAME}.zip"
