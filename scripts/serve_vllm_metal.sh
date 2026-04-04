#!/bin/bash
# Start vllm-metal server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$HOME/.venv-vllm-metal"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: vllm-metal venv not found. Run install_vllm_metal.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "=== Starting vllm-metal server on port $VLLM_METAL_PORT ==="

VLLM_METAL_USE_PAGED_ATTENTION=1 \
VLLM_METAL_MEMORY_FRACTION=0.3 \
vllm serve "$HF_REPO" \
    --port "$VLLM_METAL_PORT" \
    --host 0.0.0.0 \
    &> "$PROJECT_DIR/.frameworks/vllm_metal_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/vllm_metal_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/vllm_metal_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 180); do
    if curl -s "http://localhost:$VLLM_METAL_PORT/v1/models" > /dev/null 2>&1; then
        echo "vllm-metal server is ready on port $VLLM_METAL_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 180 seconds"
cat "$PROJECT_DIR/.frameworks/vllm_metal_server.log"
exit 1
