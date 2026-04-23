#!/bin/bash
# Update mlx_lm to latest
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/mlx_lm"

echo "=== Updating mlx_lm ==="

source "$VENV_DIR/bin/activate"
# Track mlx-lm's git main (see install_mlx_lm.sh for the rationale —
# PyPI release predates the thread-local-stream fix).
uv pip install --upgrade "mlx-lm @ git+https://github.com/ml-explore/mlx-lm"

echo "=== mlx_lm updated ==="
