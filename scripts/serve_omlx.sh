#!/bin/bash
# Start omlx server
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/omlx"
OMLX_MODEL_DIR="$MODELS_DIR/omlx"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: omlx venv not found. Run install_omlx.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

# omlx is a multi-model server that auto-discovers everything in its
# --model-dir at startup. Refresh the symlink for the currently active
# MLX_MODEL so adding a new model profile doesn't silently fall back to
# whatever symlink already happens to be there (e.g. Qwen3-0.6B served
# as "Gemma-4" because no Gemma symlink existed).
mkdir -p "$OMLX_MODEL_DIR"
ACTIVE_LINK="$OMLX_MODEL_DIR/$(basename "$MLX_MODEL")"
ln -snf "$MLX_MODEL" "$ACTIVE_LINK"
echo "Refreshed omlx symlink: $ACTIVE_LINK -> $MLX_MODEL"

echo "=== Starting omlx server on port $OMLX_PORT ==="

omlx serve \
    --model-dir "$OMLX_MODEL_DIR" \
    --port "$OMLX_PORT" \
    --host 0.0.0.0 \
    &> "$PROJECT_DIR/.frameworks/omlx_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/omlx_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/omlx_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 300); do
    if curl -s "http://localhost:$OMLX_PORT/v1/models" > /dev/null 2>&1; then
        echo "omlx server is ready on port $OMLX_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 300 seconds"
cat "$PROJECT_DIR/.frameworks/omlx_server.log"
exit 1
