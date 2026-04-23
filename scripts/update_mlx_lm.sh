#!/bin/bash
# Update mlx_lm to latest
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/mlx_lm"

echo "=== Updating mlx_lm ==="

source "$VENV_DIR/bin/activate"
# Pin mlx to 0.31.1 — see install_mlx_lm.sh for the rationale (GPU stream
# thread-local change in 0.31.2 breaks mlx_lm.server's BatchGenerator).
uv pip install --upgrade mlx-lm "mlx==0.31.1" "mlx-metal==0.31.1"

echo "=== mlx_lm updated ==="
