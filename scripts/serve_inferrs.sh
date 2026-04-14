#!/bin/bash
# Start inferrs server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

SERVER="$FRAMEWORKS_DIR/inferrs/target/release/inferrs"

if [ ! -f "$SERVER" ]; then
    echo "Error: inferrs binary not found. Run install_inferrs.sh first."
    exit 1
fi

echo "=== Starting inferrs server on port $INFERRS_PORT ==="

"$SERVER" serve "$HF_MODEL" \
    --port "$INFERRS_PORT" \
    --host 0.0.0.0 \
    --device metal \
    --dtype bf16 \
    --max-seq-len 16384 \
    --initial-blocks 512 \
    --paged-attention \
    &> "$PROJECT_DIR/.frameworks/inferrs_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/inferrs_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/inferrs_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 300); do
    if curl -s "http://localhost:$INFERRS_PORT/v1/models" > /dev/null 2>&1; then
        echo "inferrs server is ready on port $INFERRS_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 300 seconds"
cat "$PROJECT_DIR/.frameworks/inferrs_server.log"
exit 1
