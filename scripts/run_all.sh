#!/bin/bash
# AppleBench — Run full benchmark across all frameworks
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

BENCH_VENV="$VENVS_DIR/bench"

# Pre-flight check
bash "$SCRIPT_DIR/env_check.sh"
echo ""

source "$BENCH_VENV/bin/activate"
export PYTHONUNBUFFERED=1

# Hard cleanup: kill any leftover inference processes
cleanup() {
    echo "  Cleaning up all inference processes..."
    pkill -f llama-server 2>/dev/null || true
    pkill -f mlx_lm 2>/dev/null || true
    pkill -f mistralrs 2>/dev/null || true
    pkill -f "vllm serve" 2>/dev/null || true
    sleep 5  # let processes die and release memory
}

# Frameworks to benchmark: name, port, serve_script, stop_script, model_override
# model_override is optional — used when auto-detection picks the wrong model
FRAMEWORKS=(
    "llamacpp:$LLAMACPP_PORT:serve_llamacpp.sh:stop_llamacpp.sh:"
    "mlx_lm:$MLX_LM_PORT:serve_mlx_lm.sh:stop_mlx_lm.sh:$MLX_MODEL"
    "mistralrs:$MISTRALRS_PORT:serve_mistralrs.sh:stop_mistralrs.sh:"
    "vllm_metal:$VLLM_METAL_PORT:serve_vllm_metal.sh:stop_vllm_metal.sh:"
)

CONCURRENCY_ARG=$(echo $CONCURRENCY_LEVELS | tr ' ' ',')

echo "========================================="
echo " AppleBench — Full Benchmark Run"
echo " $(date)"
echo "========================================="
echo ""

# Initial cleanup
cleanup

for entry in "${FRAMEWORKS[@]}"; do
    IFS=':' read -r name port serve stop model_override <<< "$entry"

    echo "==========================================="
    echo " Benchmarking: $name (port $port)"
    echo "==========================================="

    # Start server
    echo "Starting $name server..."
    bash "$SCRIPT_DIR/$serve"
    echo ""

    # Run benchmark
    MODEL_FLAG=""
    if [ -n "$model_override" ]; then
        MODEL_FLAG="--model $model_override"
    fi
    python "$SCRIPT_DIR/benchmark.py" \
        --framework "$name" \
        --port "$port" \
        --concurrency "$CONCURRENCY_ARG" \
        --requests "$BENCHMARK_REQUESTS" \
        --warmup "$WARMUP_REQUESTS" \
        $MODEL_FLAG || true
    echo ""

    # Stop server gracefully
    echo "Stopping $name server..."
    bash "$SCRIPT_DIR/$stop"

    # Hard cleanup — kill orphans, release GPU memory
    cleanup

    # Cooldown — let GPU thermals and memory settle
    echo "Cooling down for ${COOLDOWN_SECONDS}s..."
    sleep "$COOLDOWN_SECONDS"
    echo ""
done

echo "==========================================="
echo " Collecting results and generating report"
echo "==========================================="
python "$SCRIPT_DIR/collect_results.py"
python "$SCRIPT_DIR/generate_report.py"

echo ""
echo "========================================="
echo " AppleBench complete!"
echo "========================================="
