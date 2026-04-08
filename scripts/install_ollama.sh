#!/bin/bash
# Install Ollama and import the benchmark model
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "=== Installing Ollama ==="

# Install via brew if not already present
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

# Start server temporarily to import model
OLLAMA_HOST="127.0.0.1:$OLLAMA_PORT" ollama serve &> /dev/null &
TMPID=$!
sleep 3

# Create Modelfile pointing to existing GGUF
MODELFILE="$FRAMEWORKS_DIR/ollama_Modelfile"
cat > "$MODELFILE" <<EOF
FROM $GGUF_MODEL
EOF

echo "Importing GGUF model as '$OLLAMA_MODEL_NAME'..."
OLLAMA_HOST="127.0.0.1:$OLLAMA_PORT" ollama create "$OLLAMA_MODEL_NAME" -f "$MODELFILE"

# Stop temp server
kill "$TMPID" 2>/dev/null || true
wait "$TMPID" 2>/dev/null || true

echo "=== Ollama installed ==="
