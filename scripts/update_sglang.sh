#!/bin/bash
# Update sglang to latest
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/sglang"
REPO_DIR="$FRAMEWORKS_DIR/sglang"

echo "=== Updating sglang ==="

if [ ! -d "$VENV_DIR" ] || [ ! -d "$REPO_DIR" ]; then
    echo "Venv or repo not found — running install instead"
    bash "$SCRIPT_DIR/install_sglang.sh"
    exit 0
fi

cd "$REPO_DIR"
# git pull will leave python/pyproject.toml dirty (we swapped it at install
# time). Stash the swap, pull, then re-apply.
if git diff --quiet -- python/pyproject.toml 2>/dev/null && [ ! -f python/pyproject_other.toml ]; then
    # Pristine state (already swapped, working tree clean): restore the upstream
    # name so git pull merges cleanly.
    git checkout -- python/pyproject.toml 2>/dev/null || true
fi
git pull --ff-only

# Re-apply the MPS pyproject swap.
if [ -f "$REPO_DIR/python/pyproject_other.toml" ]; then
    rm -f "$REPO_DIR/python/pyproject.toml"
    mv "$REPO_DIR/python/pyproject_other.toml" "$REPO_DIR/python/pyproject.toml"
fi

source "$VENV_DIR/bin/activate"
uv pip install --upgrade -e "$REPO_DIR/python[all_mps]"
uv pip install --upgrade mlx mlx-lm

echo "=== sglang updated ==="
