#!/bin/bash
# Update inferrs to latest and rebuild
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REPO_DIR="$FRAMEWORKS_DIR/inferrs"

echo "=== Updating inferrs ==="

cd "$REPO_DIR"
git pull
cargo build --release

echo "=== inferrs updated ==="
