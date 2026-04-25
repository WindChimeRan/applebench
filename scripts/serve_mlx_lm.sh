#!/bin/bash
# Start mlx_lm server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# MLX_BACKEND controls which library serves the model:
#   "mlx_lm"  (default) → text-only via mlx_lm.server. Used by Qwen3 etc.
#   "mlx_vlm"           → mlx_vlm.server. Required for multimodal MLX ports
#                         like mlx-community/gemma-4-e4b-it-bf16, whose
#                         weight layout mlx_lm's loader rejects.
MLX_BACKEND="${MLX_BACKEND:-mlx_lm}"
VENV_DIR="$VENVS_DIR/$MLX_BACKEND"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: $MLX_BACKEND venv not found at $VENV_DIR. Run install_mlx_lm.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "=== Starting $MLX_BACKEND server on port $MLX_LM_PORT ==="

python -m "$MLX_BACKEND".server \
    --model "$MLX_MODEL" \
    --port "$MLX_LM_PORT" \
    &> "$PROJECT_DIR/.frameworks/mlx_lm_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/mlx_lm_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/mlx_lm_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 300); do
    if curl -s "http://localhost:$MLX_LM_PORT/v1/models" > /dev/null 2>&1; then
        echo "mlx_lm server is ready on port $MLX_LM_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 300 seconds"
cat "$PROJECT_DIR/.frameworks/mlx_lm_server.log"
exit 1
