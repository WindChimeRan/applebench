#!/bin/bash
# Start Ollama server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

if ! command -v ollama &>/dev/null; then
    echo "Error: Ollama not found. Run install_ollama.sh first."
    exit 1
fi

# Stop any existing Ollama service to avoid port conflicts
pkill -f "ollama serve" 2>/dev/null || true
launchctl stop com.ollama 2>/dev/null || true
sleep 2

echo "=== Starting Ollama server on port $OLLAMA_PORT ==="

OLLAMA_HOST="0.0.0.0:$OLLAMA_PORT" \
OLLAMA_NUM_PARALLEL=16 \
OLLAMA_KEEP_ALIVE="10m" \
    ollama serve &> "$PROJECT_DIR/.frameworks/ollama_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/ollama_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/ollama_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 60); do
    if curl -s "http://localhost:$OLLAMA_PORT/v1/models" > /dev/null 2>&1; then
        echo "Ollama server is ready on port $OLLAMA_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 60 seconds"
cat "$PROJECT_DIR/.frameworks/ollama_server.log"
exit 1
