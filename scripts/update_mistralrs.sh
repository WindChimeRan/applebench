#!/bin/bash
# Update mistral.rs to latest and rebuild
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REPO_DIR="$FRAMEWORKS_DIR/mistral.rs"

echo "=== Updating mistral.rs ==="

cd "$REPO_DIR"
git pull
MISTRALRS_METAL_PRECOMPILE=0 cargo build --release --features "metal accelerate"

echo "=== mistral.rs updated ==="
