#!/bin/bash
# Install Ollama and pull the benchmark model from the official registry.
#
# Earlier iterations imported our local BF16 GGUF via a Modelfile with only
# a FROM line; Ollama's auto-template-from-GGUF-metadata didn't apply Qwen3's
# ChatML delimiters correctly, producing 92% parse-failure output on the
# correctness eval. Switching to `ollama pull <tag>` from the registry uses
# the manifest's chat template and stop tokens directly.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "=== Installing Ollama ==="

if command -v ollama &>/dev/null; then
    echo "Ollama already installed: $(ollama --version)"
else
    echo "Installing Ollama via brew..."
    brew install ollama
fi

# Stop any existing Ollama service to avoid port conflicts
pkill -f "ollama serve" 2>/dev/null || true
launchctl stop com.ollama 2>/dev/null || true
sleep 2

# Start a temporary server so `ollama pull` has something to talk to
OLLAMA_HOST="127.0.0.1:$OLLAMA_PORT" ollama serve &> /dev/null &
TMPID=$!
sleep 3

echo "Pulling '$OLLAMA_MODEL_NAME' from the Ollama registry..."
OLLAMA_HOST="127.0.0.1:$OLLAMA_PORT" ollama pull "$OLLAMA_MODEL_NAME"

# Stop temp server
kill "$TMPID" 2>/dev/null || true
wait "$TMPID" 2>/dev/null || true

echo "=== Ollama installed ==="
