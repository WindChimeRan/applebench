#!/bin/bash
# Update vllm-metal to latest
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "=== Updating vllm-metal ==="

# Re-run official installer to get latest
rm -rf ~/.venv-vllm-metal
curl -fsSL https://raw.githubusercontent.com/vllm-project/vllm-metal/main/install.sh | bash

echo "=== vllm-metal updated ==="
