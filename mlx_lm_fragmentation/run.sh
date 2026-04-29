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
if [ -n "${FRAGMENTATION_RESULTS_SUBDIR:-}" ]; then
    RESULTS="$RESULTS/$FRAGMENTATION_RESULTS_SUBDIR"
fi
mkdir -p "$RESULTS"
export FRAGMENTATION_RESULTS_DIR="$RESULTS"
LOG=$RESULTS/server.log
MLX_PYTHON="$VENVS_DIR/mlx_lm/bin/python"
BENCH_PYTHON="$VENVS_DIR/bench/bin/python"
export PATH="$VENVS_DIR/bench/bin:$PATH"

echo "[1/4] Building prompts (results: $RESULTS) ..."
MLX_MODEL="$MLX_MODEL" "$MLX_PYTHON" make_prompts.py

echo "[2/4] Starting mlx_lm.server on :$MLX_LM_PORT (prompt-cache disabled, prefill-step ${MLX_PREFILL_STEP_SIZE:-2048}, prompt-concurrency ${MLX_PROMPT_CONCURRENCY:-8}) ..."
"$MLX_PYTHON" -m mlx_lm.server \
    --model "$MLX_MODEL" \
    --port "$MLX_LM_PORT" \
    --prompt-cache-bytes 1 \
    --prefill-step-size "${MLX_PREFILL_STEP_SIZE:-2048}" \
    --prompt-concurrency "${MLX_PROMPT_CONCURRENCY:-8}" \
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
