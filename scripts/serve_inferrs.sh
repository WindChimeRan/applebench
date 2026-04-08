#!/bin/bash
# Start inferrs server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

if ! command -v inferrs &>/dev/null; then
    echo "Error: inferrs not found. Run install_inferrs.sh first."
    exit 1
fi

echo "=== Starting inferrs server on port $INFERRS_PORT ==="

inferrs serve "$HF_MODEL" \
    --port "$INFERRS_PORT" \
    --host 0.0.0.0 \
    --device metal \
    --dtype bf16 \
    --max-seq-len 4096 \
    --initial-blocks 512 \
    --paged-attention \
    &> "$PROJECT_DIR/.frameworks/inferrs_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/inferrs_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/inferrs_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 120); do
    if curl -s "http://localhost:$INFERRS_PORT/v1/models" > /dev/null 2>&1; then
        echo "inferrs server is ready on port $INFERRS_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 120 seconds"
cat "$PROJECT_DIR/.frameworks/inferrs_server.log"
exit 1
