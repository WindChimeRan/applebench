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

CTX_ARG=""
if [ -n "$LLAMACPP_CTX_SIZE" ]; then
    CTX_ARG="-c $LLAMACPP_CTX_SIZE"
fi

"$SERVER" \
    -m "$GGUF_MODEL" \
    --port "$LLAMACPP_PORT" \
    --host 0.0.0.0 \
    -ngl 99 \
    --parallel 4 \
    $CTX_ARG \
    &> "$PROJECT_DIR/.frameworks/llamacpp_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/llamacpp_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/llamacpp_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 300); do
    if curl -sf "http://localhost:$LLAMACPP_PORT/health" 2>/dev/null | grep -q '"ok"' 2>/dev/null; then
        echo "llama.cpp server is ready on port $LLAMACPP_PORT"
        exit 0
    fi
    sleep 1 || true
done

echo "Error: Server failed to start within 300 seconds"
cat "$PROJECT_DIR/.frameworks/llamacpp_server.log"
exit 1
