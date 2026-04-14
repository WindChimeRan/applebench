#!/bin/bash
# Update inferrs to latest and rebuild
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REPO_DIR="$FRAMEWORKS_DIR/inferrs"

# Ensure cargo is on PATH (rustup installs to ~/.cargo/bin but unattended
# shells like weekly_bench.sh don't source ~/.zshrc)
[ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env"

echo "=== Updating inferrs ==="

if [ ! -d "$REPO_DIR" ]; then
    echo "inferrs repo not found at $REPO_DIR — running install instead"
    bash "$SCRIPT_DIR/install_inferrs.sh"
    exit 0
fi

cd "$REPO_DIR"
git pull
cargo build --release

echo "=== inferrs updated ==="
