#!/bin/bash
# Update omlx to latest
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/omlx"
OMLX_REPO_DIR="$FRAMEWORKS_DIR/omlx"

echo "=== Updating omlx ==="

cd "$OMLX_REPO_DIR"
git pull

source "$VENV_DIR/bin/activate"
uv pip install -e "$OMLX_REPO_DIR"

echo "=== omlx updated ==="
