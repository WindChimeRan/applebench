#!/bin/bash
# Install inferrs from source
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REPO_DIR="$FRAMEWORKS_DIR/inferrs"

echo "=== Installing inferrs ==="

if [ -d "$REPO_DIR" ]; then
    echo "inferrs already cloned, run update_inferrs.sh to update"
else
    git clone https://github.com/ericcurtin/inferrs.git "$REPO_DIR"
fi

cd "$REPO_DIR"
cargo build --release

echo "=== inferrs installed ==="
echo "Server binary: $REPO_DIR/target/release/inferrs"
