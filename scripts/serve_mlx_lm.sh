#!/bin/bash
# Start mlx_lm server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/mlx_lm"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: mlx_lm venv not found. Run install_mlx_lm.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "=== Starting mlx_lm server on port $MLX_LM_PORT ==="

python -m mlx_lm.server \
    --model "$MLX_MODEL" \
    --port "$MLX_LM_PORT" \
    &> "$PROJECT_DIR/.frameworks/mlx_lm_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/mlx_lm_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/mlx_lm_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 120); do
    if curl -s "http://localhost:$MLX_LM_PORT/v1/models" > /dev/null 2>&1; then
        echo "mlx_lm server is ready on port $MLX_LM_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 120 seconds"
cat "$PROJECT_DIR/.frameworks/mlx_lm_server.log"
exit 1
