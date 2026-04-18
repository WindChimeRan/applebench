#!/bin/bash
# Update hf_transformers to latest
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/hf_transformers"

echo "=== Updating hf_transformers ==="

source "$VENV_DIR/bin/activate"
uv pip install --upgrade "transformers[serving]" torch

echo "=== hf_transformers updated ==="
