#!/bin/bash
# Start HuggingFace transformers serve (continuous batching + paged|sdpa on MPS)
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/hf_transformers"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: hf_transformers venv not found. Run install_hf_transformers.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "=== Starting hf_transformers server on port $HF_TRANSFORMERS_PORT ==="

PYTORCH_ENABLE_MPS_FALLBACK=1 transformers serve \
    --continuous-batching \
    --device mps \
    --dtype bfloat16 \
    --attn-implementation sdpa \
    --port "$HF_TRANSFORMERS_PORT" \
    "$HF_MODEL" \
    &> "$PROJECT_DIR/.frameworks/hf_transformers_server.log" &

echo $! > "$PROJECT_DIR/.frameworks/hf_transformers_server.pid"
echo "PID: $(cat "$PROJECT_DIR/.frameworks/hf_transformers_server.pid")"

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 300); do
    if curl -s "http://localhost:$HF_TRANSFORMERS_PORT/v1/models" > /dev/null 2>&1; then
        echo "hf_transformers server is ready on port $HF_TRANSFORMERS_PORT"
        exit 0
    fi
    sleep 1
done

echo "Error: Server failed to start within 300 seconds"
cat "$PROJECT_DIR/.frameworks/hf_transformers_server.log"
exit 1
