#!/bin/bash
# Install vllm-metal using the official install script
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "=== Installing vllm-metal ==="

# Use the official installer (creates ~/.venv-vllm-metal)
curl -fsSL https://raw.githubusercontent.com/vllm-project/vllm-metal/main/install.sh | bash

echo "=== vllm-metal installed ==="
echo "Venv: ~/.venv-vllm-metal"
