#!/bin/bash
# Install omlx in its own venv
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/omlx"
OMLX_REPO_DIR="$FRAMEWORKS_DIR/omlx"
OMLX_MODEL_DIR="$MODELS_DIR/omlx"

echo "=== Installing omlx ==="

# Clone repo if needed
if [ -d "$OMLX_REPO_DIR" ]; then
    echo "omlx repo already cloned at $OMLX_REPO_DIR"
else
    git clone https://github.com/jundot/omlx.git "$OMLX_REPO_DIR"
fi

# Create venv
if [ -d "$VENV_DIR" ]; then
    echo "Venv already exists at $VENV_DIR"
else
    uv venv "$VENV_DIR" --python 3.12
fi

source "$VENV_DIR/bin/activate"
uv pip install -e "$OMLX_REPO_DIR"

# Create omlx model directory with symlink to shared MLX model
mkdir -p "$OMLX_MODEL_DIR"
if [ ! -L "$OMLX_MODEL_DIR/Qwen3-0.6B-bf16-mlx" ] && [ ! -d "$OMLX_MODEL_DIR/Qwen3-0.6B-bf16-mlx" ]; then
    ln -sf "$MLX_MODEL" "$OMLX_MODEL_DIR/Qwen3-0.6B-bf16-mlx"
    echo "Created symlink: $OMLX_MODEL_DIR/Qwen3-0.6B-bf16-mlx -> $MLX_MODEL"
fi

echo "=== omlx installed ==="
