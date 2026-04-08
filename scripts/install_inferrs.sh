#!/bin/bash
# Install inferrs via brew
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "=== Installing inferrs ==="

if command -v inferrs &>/dev/null; then
    echo "inferrs already installed: $(inferrs --version 2>&1 || echo 'unknown version')"
else
    echo "Installing inferrs via brew..."
    brew tap ericcurtin/inferrs
    brew install inferrs
fi

echo "=== inferrs installed ==="
