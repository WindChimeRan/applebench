#!/bin/bash
# AppleBench — Run full benchmark across all (or selected) frameworks
# Usage: bash scripts/run_all.sh [--model MODEL] [framework ...]
# Examples:
#   bash scripts/run_all.sh                          # run all, default model
#   bash scripts/run_all.sh --model qwen3-30b-a3b    # run all, specific model
#   bash scripts/run_all.sh --model qwen3-0.6b llamacpp mlx_lm
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse --model and --split flags before sourcing config
ONLY_FRAMEWORKS=()
SPLIT="chat"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --model)
            export APPLEBENCH_MODEL="$2"
            shift 2
            ;;
        --split)
            SPLIT="$2"
            shift 2
            ;;
        *)
            ONLY_FRAMEWORKS+=("$1")
            shift
            ;;
    esac
done

source "$SCRIPT_DIR/config.sh"

BENCH_VENV="$VENVS_DIR/bench"

# Pre-flight check
bash "$SCRIPT_DIR/env_check.sh"
echo ""

# Auto-create bench venv if missing
if [ ! -d "$BENCH_VENV" ]; then
    echo "Bench venv not found — installing..."
    bash "$SCRIPT_DIR/install_bench.sh"
fi

source "$BENCH_VENV/bin/activate"
export PYTHONUNBUFFERED=1

# Hard cleanup: kill any leftover inference processes
cleanup() {
    echo "  Cleaning up all inference processes..."
    pkill -f llama-server 2>/dev/null || true
    pkill -f mlx_lm 2>/dev/null || true
    pkill -f mistralrs 2>/dev/null || true
    pkill -f "vllm serve" 2>/dev/null || true
    pkill -f "omlx serve" 2>/dev/null || true
    pkill -f "ollama serve" 2>/dev/null || true
    pkill -f "inferrs serve" 2>/dev/null || true
    sleep 5  # let processes die and release memory
}

# Frameworks to benchmark: name, port, serve_script, stop_script, model_override
# model_override is optional — used when auto-detection picks the wrong model
FRAMEWORKS=(
    "llamacpp:$LLAMACPP_PORT:serve_llamacpp.sh:stop_llamacpp.sh:"
    "mlx_lm:$MLX_LM_PORT:serve_mlx_lm.sh:stop_mlx_lm.sh:$MLX_MODEL"
    "mistralrs:$MISTRALRS_PORT:serve_mistralrs.sh:stop_mistralrs.sh:"
    "vllm_metal:$VLLM_METAL_PORT:serve_vllm_metal.sh:stop_vllm_metal.sh:"
    "omlx:$OMLX_PORT:serve_omlx.sh:stop_omlx.sh:"
    "ollama:$OLLAMA_PORT:serve_ollama.sh:stop_ollama.sh:$OLLAMA_MODEL_NAME"
    "inferrs:$INFERRS_PORT:serve_inferrs.sh:stop_inferrs.sh:"
)

CONCURRENCY_ARG=$(echo $CONCURRENCY_LEVELS | tr ' ' ',')

echo "========================================="
echo " AppleBench — Full Benchmark Run"
echo " Model: $MODEL_NAME"
echo " Split: $SPLIT"
echo " $(date)"
echo "========================================="
echo ""

# Clean old result files so comparison.json reflects this run only
echo "Cleaning old result files..."
rm -f "$RESULTS_DIR"/*_*.json "$RESULTS_DIR/comparison.json"

# Initial cleanup
cleanup

for entry in "${FRAMEWORKS[@]}"; do
    IFS=':' read -r name port serve stop model_override <<< "$entry"

    # Skip if user specified frameworks and this isn't one of them
    if [ ${#ONLY_FRAMEWORKS[@]} -gt 0 ]; then
        match=false
        for f in "${ONLY_FRAMEWORKS[@]}"; do
            [ "$f" = "$name" ] && match=true
        done
        $match || continue
    fi

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
        --results-dir "$RESULTS_DIR" \
        --split "$SPLIT" \
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
python "$SCRIPT_DIR/collect_results.py" --results-dir "$RESULTS_DIR"
python "$SCRIPT_DIR/generate_report.py" --results-dir "$RESULTS_DIR"

echo ""
echo "========================================="
echo " AppleBench complete!"
echo "========================================="
