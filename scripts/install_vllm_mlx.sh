#!/bin/bash
# Install vllm-mlx in its own venv (vLLM plugin with MLX backend for Apple Silicon)
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/vllm_mlx"

echo "=== Installing vllm-mlx ==="

if [ -d "$VENV_DIR" ]; then
    echo "Venv already exists at $VENV_DIR"
else
    uv venv "$VENV_DIR" --python 3.12
fi

source "$VENV_DIR/bin/activate"
uv pip install "git+https://github.com/waybarrios/vllm-mlx.git"

echo "=== vllm-mlx installed ==="
