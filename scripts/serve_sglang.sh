#!/bin/bash
# Start sglang server with MLX backend on Apple Silicon.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/sglang"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: sglang venv not found. Run install_sglang.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "=== Starting sglang server on port $SGLANG_PORT ==="

# SGLANG_USE_MLX=1 routes the model forward pass through MLX instead of MPS torch.
# --disable-radix-cache / --disable-cuda-graph / --tp-size 1 are the verified
# args from the Apple-Silicon roadmap (issue #19137); the cuda-graph flag is a
# no-op on MPS but the launcher still expects it.
SGLANG_USE_MLX=1 python -m sglang.launch_server \
    --model-path "$HF_MODEL" \
    --host 0.0.0.0 \
    --port "$SGLANG_PORT" \
    --trust-remote-code \
    --disable-radix-cache \
    --disable-cuda-graph \
    --tp-size 1 \
    &> "$PROJECT_DIR/.frameworks/sglang_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/sglang_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/sglang_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 300); do
    if curl -s "http://localhost:$SGLANG_PORT/v1/models" > /dev/null 2>&1; then
        echo "sglang server is ready on port $SGLANG_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 300 seconds"
cat "$PROJECT_DIR/.frameworks/sglang_server.log"
exit 1
