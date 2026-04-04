#!/bin/bash
# Install mistral.rs from source
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REPO_DIR="$FRAMEWORKS_DIR/mistral.rs"

echo "=== Installing mistral.rs ==="

if [ -d "$REPO_DIR" ]; then
    echo "mistral.rs already cloned, run update_mistralrs.sh to update"
else
    git clone https://github.com/EricLBuehler/mistral.rs.git "$REPO_DIR"
fi

cd "$REPO_DIR"
# MISTRALRS_METAL_PRECOMPILE=0 avoids needing full Xcode (Command Line Tools suffice)
MISTRALRS_METAL_PRECOMPILE=0 cargo build --release --features "metal accelerate"

echo "=== mistral.rs installed ==="
echo "Server binary: $REPO_DIR/target/release/mistralrs"
