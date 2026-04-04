#!/bin/bash
# Update llama.cpp to latest and rebuild
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REPO_DIR="$FRAMEWORKS_DIR/llama.cpp"

echo "=== Updating llama.cpp ==="

cd "$REPO_DIR"
git pull
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release -j$(sysctl -n hw.ncpu)

echo "=== llama.cpp updated ==="
