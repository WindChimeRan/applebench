#!/bin/bash
# Start vllm-mlx server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/vllm_mlx"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: vllm-mlx venv not found. Run install_vllm_mlx.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "=== Starting vllm-mlx server on port $VLLM_MLX_PORT ==="

vllm-mlx serve "$MLX_MODEL" \
    --port "$VLLM_MLX_PORT" \
    --continuous-batching \
    &> "$PROJECT_DIR/.frameworks/vllm_mlx_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/vllm_mlx_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/vllm_mlx_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 300); do
    if curl -s "http://localhost:$VLLM_MLX_PORT/v1/models" > /dev/null 2>&1; then
        echo "vllm-mlx server is ready on port $VLLM_MLX_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 300 seconds"
cat "$PROJECT_DIR/.frameworks/vllm_mlx_server.log"
exit 1
