#!/bin/bash
# Start llama.cpp server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

SERVER="$FRAMEWORKS_DIR/llama.cpp/build/bin/llama-server"

if [ ! -f "$SERVER" ]; then
    echo "Error: llama-server not found. Run install_llamacpp.sh first."
    exit 1
fi

if [ ! -f "$GGUF_MODEL" ]; then
    echo "Error: GGUF model not found. Run download_model.sh first."
    exit 1
fi

echo "=== Starting llama.cpp server on port $LLAMACPP_PORT ==="

"$SERVER" \
    -m "$GGUF_MODEL" \
    --port "$LLAMACPP_PORT" \
    --host 0.0.0.0 \
    -ngl 99 \
    --parallel 4 \
    &> "$PROJECT_DIR/.frameworks/llamacpp_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/llamacpp_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/llamacpp_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 60); do
    if curl -s "http://localhost:$LLAMACPP_PORT/v1/models" > /dev/null 2>&1; then
        echo "llama.cpp server is ready on port $LLAMACPP_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 60 seconds"
cat "$PROJECT_DIR/.frameworks/llamacpp_server.log"
exit 1
