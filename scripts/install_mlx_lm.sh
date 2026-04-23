#!/bin/bash
# Install mlx_lm in its own venv
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/mlx_lm"

echo "=== Installing mlx_lm ==="

if [ -d "$VENV_DIR" ]; then
    echo "Venv already exists at $VENV_DIR"
else
    uv venv "$VENV_DIR" --python 3.12
fi

source "$VENV_DIR/bin/activate"
# mlx-lm==0.31.2 works only with mlx==0.31.1 — mlx 0.31.2 made GPU streams
# thread-local and mlx_lm.server's BatchGenerator worker thread then fails
# with "There is no Stream(gpu, 0) in current thread." at mx.eval time,
# causing silent-failure hangs. Pin mlx until upstream mlx_lm matches.
uv pip install mlx-lm "mlx==0.31.1" "mlx-metal==0.31.1"

echo "=== mlx_lm installed ==="
