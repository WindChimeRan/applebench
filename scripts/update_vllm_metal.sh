#!/bin/bash
# Update vllm-metal to latest
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "=== Updating vllm-metal ==="

# Download installer first, before removing old venv
INSTALL_SCRIPT=$(mktemp)
curl -fsSL https://raw.githubusercontent.com/vllm-project/vllm-metal/main/install.sh > "$INSTALL_SCRIPT" || {
    echo "Error: failed to download vllm-metal installer"
    rm -f "$INSTALL_SCRIPT"
    exit 1
}

# Back up old venv, install new, remove backup on success
if [ -d ~/.venv-vllm-metal ]; then
    mv ~/.venv-vllm-metal ~/.venv-vllm-metal.bak
fi

if bash "$INSTALL_SCRIPT"; then
    rm -rf ~/.venv-vllm-metal.bak
else
    echo "Error: vllm-metal install failed, restoring backup"
    rm -rf ~/.venv-vllm-metal
    [ -d ~/.venv-vllm-metal.bak ] && mv ~/.venv-vllm-metal.bak ~/.venv-vllm-metal
    rm -f "$INSTALL_SCRIPT"
    exit 1
fi
rm -f "$INSTALL_SCRIPT"

echo "=== vllm-metal updated ==="
