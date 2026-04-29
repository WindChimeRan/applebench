#!/bin/bash
# Orchestrate the fragmentation experiment:
#  1. Build prompts (uses mlx_lm venv tokenizer)
#  2. Start mlx_lm.server with LRU prompt cache disabled
#  3. Run sequential workload wrapped in `metalstat run`
#  4. Run concurrent workload wrapped in `metalstat run`
set -euo pipefail
cd "$(dirname "$0")"
source ../scripts/config.sh

RESULTS=$(pwd)/results
LOG=$RESULTS/server.log
MLX_PYTHON="$VENVS_DIR/mlx_lm/bin/python"
BENCH_PYTHON="$VENVS_DIR/bench/bin/python"

echo "[1/4] Building prompts ..."
"$MLX_PYTHON" make_prompts.py

echo "[2/4] Starting mlx_lm.server on :$MLX_LM_PORT (prompt-cache disabled) ..."
"$MLX_PYTHON" -m mlx_lm.server \
    --model "$MLX_MODEL" \
    --port "$MLX_LM_PORT" \
    --prompt-cache-bytes 1 \
    > "$LOG" 2>&1 &
SERVER_PID=$!
echo "  server PID: $SERVER_PID"
trap "kill $SERVER_PID 2>/dev/null || true" EXIT

for i in $(seq 1 120); do
    if curl -s "http://localhost:$MLX_LM_PORT/v1/models" > /dev/null 2>&1; then
        echo "  ready in ${i}s"
        break
    fi
    sleep 1
done
if ! curl -s "http://localhost:$MLX_LM_PORT/v1/models" > /dev/null 2>&1; then
    echo "Server failed to start. Tail of log:"; tail -50 "$LOG"; exit 1
fi
sleep 2

echo "[3/4] Running sequential workload (metalstat sampling) ..."
metalstat run \
    -o "$RESULTS/sequential" \
    -i 0.1 \
    -- "$BENCH_PYTHON" workload.py --mode sequential --base-url "http://localhost:$MLX_LM_PORT" --model "$MLX_MODEL"

echo "  idle pause 3s ..."
sleep 3

echo "[4/4] Running concurrent workload (metalstat sampling) ..."
metalstat run \
    -o "$RESULTS/concurrent" \
    -i 0.1 \
    -- "$BENCH_PYTHON" workload.py --mode concurrent --base-url "http://localhost:$MLX_LM_PORT" --model "$MLX_MODEL"

echo
echo "Done. Files in $RESULTS:"
ls -la "$RESULTS"
