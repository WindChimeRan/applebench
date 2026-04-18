#!/bin/bash
# Install HuggingFace transformers (with serving extras) in its own venv
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/hf_transformers"

echo "=== Installing hf_transformers ==="

if [ -d "$VENV_DIR" ]; then
    echo "Venv already exists at $VENV_DIR"
else
    uv venv "$VENV_DIR" --python 3.12
fi

source "$VENV_DIR/bin/activate"
uv pip install "transformers[serving]" torch requests

echo "=== hf_transformers installed ==="
