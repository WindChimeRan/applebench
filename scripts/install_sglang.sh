#!/bin/bash
# Install sglang from source with the MLX backend (Apple Silicon).
# Follows docs/platforms/apple_metal.md: swap pyproject_other.toml in for the
# default (CUDA) pyproject.toml, then `uv pip install -e python[all_mps]`.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/sglang"
REPO_DIR="$FRAMEWORKS_DIR/sglang"

echo "=== Installing sglang ==="

# Clone repo
if [ -d "$REPO_DIR" ]; then
    echo "sglang repo already cloned at $REPO_DIR"
else
    git clone https://github.com/sgl-project/sglang.git "$REPO_DIR"
fi

# Swap in the MPS pyproject.toml. Idempotent: only acts if pyproject_other.toml
# is still present (a fresh clone has it; a subsequent install_*.sh re-run does not).
if [ -f "$REPO_DIR/python/pyproject_other.toml" ]; then
    rm -f "$REPO_DIR/python/pyproject.toml"
    mv "$REPO_DIR/python/pyproject_other.toml" "$REPO_DIR/python/pyproject.toml"
    echo "Swapped pyproject_other.toml -> pyproject.toml (MPS build)"
fi

# Python 3.11 — issue #19137 explicitly notes other versions are known-broken.
if [ -d "$VENV_DIR" ]; then
    echo "Venv already exists at $VENV_DIR"
else
    uv venv "$VENV_DIR" --python 3.11
fi

source "$VENV_DIR/bin/activate"
uv pip install --upgrade pip
uv pip install -e "$REPO_DIR/python[all_mps]"

# Belt-and-suspenders: the MLX backend tracks fast-moving mlx/mlx-lm releases
# and the pinned versions in pyproject often lag what actually works.
uv pip install --upgrade mlx mlx-lm

echo "=== sglang installed ==="
