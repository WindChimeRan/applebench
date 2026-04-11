#!/bin/bash
# Update vllm-mlx to latest
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/vllm_mlx"

echo "=== Updating vllm-mlx ==="

if [ ! -d "$VENV_DIR" ]; then
    echo "Venv not found at $VENV_DIR — running install instead"
    bash "$SCRIPT_DIR/install_vllm_mlx.sh"
    exit 0
fi

source "$VENV_DIR/bin/activate"
uv pip install --upgrade --force-reinstall "git+https://github.com/waybarrios/vllm-mlx.git"

echo "=== vllm-mlx updated ==="
