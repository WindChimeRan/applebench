#!/bin/bash
# Start mistral.rs server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

SERVER="$FRAMEWORKS_DIR/mistral.rs/target/release/mistralrs"

if [ ! -f "$SERVER" ]; then
    echo "Error: mistralrs binary not found. Run install_mistralrs.sh first."
    exit 1
fi

if [ ! -f "$GGUF_MODEL" ]; then
    echo "Error: GGUF model not found. Run download_model.sh first."
    exit 1
fi

echo "=== Starting mistral.rs server on port $MISTRALRS_PORT ==="

"$SERVER" serve \
    -p "$MISTRALRS_PORT" \
    -m "$HF_REPO" \
    --format gguf \
    -f "$GGUF_MODEL" \
    &> "$PROJECT_DIR/.frameworks/mistralrs_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/mistralrs_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/mistralrs_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 300); do
    if curl -s "http://localhost:$MISTRALRS_PORT/v1/models" > /dev/null 2>&1; then
        echo "mistral.rs server is ready on port $MISTRALRS_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 300 seconds"
cat "$PROJECT_DIR/.frameworks/mistralrs_server.log"
exit 1
