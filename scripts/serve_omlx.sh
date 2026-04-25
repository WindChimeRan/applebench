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

# omlx is a multi-model server that auto-discovers every subdir/symlink
# in --model-dir. Run_all_mac.sh picks `/v1/models data[0]` for the API
# `model` field, so a stale extra symlink (e.g. Qwen3-0.6B left from a
# prior profile) silently wins on alphabetical/discovery order and the
# benchmark scores the wrong model. Make the dir contain ONLY the active
# model so discovery is unambiguous.
mkdir -p "$OMLX_MODEL_DIR"
ACTIVE_NAME="$(basename "$MLX_MODEL")"
for entry in "$OMLX_MODEL_DIR"/*; do
    [ -e "$entry" ] || continue
    [ "$(basename "$entry")" = "$ACTIVE_NAME" ] && continue
    rm -rf "$entry"
done
ln -snf "$MLX_MODEL" "$OMLX_MODEL_DIR/$ACTIVE_NAME"
echo "omlx model dir reset to single entry: $ACTIVE_NAME -> $MLX_MODEL"

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
