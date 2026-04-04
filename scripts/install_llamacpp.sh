#!/bin/bash
# Install llama.cpp from source (for latest dev builds)
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REPO_DIR="$FRAMEWORKS_DIR/llama.cpp"

echo "=== Installing llama.cpp ==="

if [ -d "$REPO_DIR" ]; then
    echo "llama.cpp already cloned, run update_llamacpp.sh to update"
else
    git clone https://github.com/ggerganov/llama.cpp.git "$REPO_DIR"
fi

cd "$REPO_DIR"
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release -j$(sysctl -n hw.ncpu)

echo "=== llama.cpp installed ==="
echo "Server binary: $REPO_DIR/build/bin/llama-server"
