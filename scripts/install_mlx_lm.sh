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
# Track mlx-lm's git main instead of the PyPI release. PyPI 0.31.2 uses
# mx.new_stream for the generation stream, which breaks under mlx 0.31.2+
# (thread-local streams) because the server's BatchGenerator worker thread
# can't reach a stream created on the main thread. Upstream fix landed on
# main as ed1fca4 ("Thread local generation stream", #1090) — switches to
# mx.new_thread_local_stream + threads the stream through BatchGenerator.
# Revert to plain `mlx-lm` once a PyPI release contains that commit.
uv pip install "mlx-lm @ git+https://github.com/ml-explore/mlx-lm"

echo "=== mlx_lm installed ==="
