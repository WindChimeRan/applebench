#!/bin/bash
# AppleBench — Run full benchmark across all (or selected) frameworks
# Usage: bash scripts/run_all.sh [--model MODEL] [--split SPLIT] [--skip-existing] [framework ...]
# Examples:
#   bash scripts/run_all.sh                          # run all, default model
#   bash scripts/run_all.sh --model qwen3-30b-a3b    # run all, specific model
#   bash scripts/run_all.sh --model qwen3-0.6b llamacpp mlx_lm
#   bash scripts/run_all.sh --skip-existing          # resume — skip frameworks done today
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse flags before sourcing config
ONLY_FRAMEWORKS=()
SPLIT="chat"
SKIP_EXISTING=false
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
        --skip-existing)
            SKIP_EXISTING=true
            shift
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
    pkill -f "vllm-mlx serve" 2>/dev/null || true
    pkill -f "transformers serve" 2>/dev/null || true
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
    "vllm_mlx:$VLLM_MLX_PORT:serve_vllm_mlx.sh:stop_vllm_mlx.sh:$MLX_MODEL"
    "hf_transformers:$HF_TRANSFORMERS_PORT:serve_hf_transformers.sh:stop_hf_transformers.sh:$HF_MODEL"
)

CONCURRENCY_ARG=$(echo $CONCURRENCY_LEVELS | tr ' ' ',')

# Bump context window for agent split — prompts reach ~8.8K tokens.
# llamacpp's --parallel 4 divides ctx across slots, so 65536 = 16384/slot.
if [ "$SPLIT" = "agent" ]; then
    export VLLM_METAL_MAX_MODEL_LEN=16384
    export LLAMACPP_CTX_SIZE=65536
    export OLLAMA_CONTEXT_LENGTH=16384
fi

# Per-split output directory: results/<MODEL>/<split>/
SPLIT_RESULTS_DIR="$RESULTS_DIR/$SPLIT"
mkdir -p "$SPLIT_RESULTS_DIR"

echo "========================================="
echo " AppleBench — Full Benchmark Run"
echo " Model: $MODEL_NAME"
echo " Split: $SPLIT"
echo " Output: $SPLIT_RESULTS_DIR"
echo " Skip-existing: $SKIP_EXISTING"
echo " $(date)"
echo "========================================="
echo ""

# Clean old result files so comparison.json reflects this run only
# (skipped in resume mode so prior successful frameworks stay intact)
if [ "$SKIP_EXISTING" = "false" ]; then
    echo "Cleaning old result files..."
    rm -f "$SPLIT_RESULTS_DIR"/*_*.json "$SPLIT_RESULTS_DIR"/*_metalstat.jsonl "$SPLIT_RESULTS_DIR/comparison.json"
else
    echo "Resume mode — keeping existing results."
fi

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

    # Skip if --skip-existing and a result file from the last 24h exists
    if [ "$SKIP_EXISTING" = "true" ]; then
        recent=$(find "$SPLIT_RESULTS_DIR" -maxdepth 1 -name "${name}_*.json" ! -name "*_metalstat.*" -mtime -1 2>/dev/null | head -1)
        if [ -n "$recent" ]; then
            echo "Skipping $name — recent result exists: $(basename "$recent")"
            continue
        fi
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

    # Shared timestamp so the benchmark JSON and the metalstat sidecar artifacts share a suffix
    RUN_TS=$(date +%Y%m%d_%H%M%S)
    BENCH_OUT="$SPLIT_RESULTS_DIR/${name}_${RUN_TS}.json"

    # Optional metalstat sidecar (gated — A/B showed wrapping perturbs tok/s ~10%; sidecar is <1%)
    METAL_PID=""
    if [ "${APPLEBENCH_METALSTAT:-0}" = "1" ]; then
        METAL_PREFIX="$SPLIT_RESULTS_DIR/${name}_${RUN_TS}_metalstat"
        metalstat --meta-json > "${METAL_PREFIX}.meta.json" 2>/dev/null || true
        metalstat --jsonl -i 1 --show-all > "${METAL_PREFIX}.jsonl" 2>/dev/null &
        METAL_PID=$!
    fi

    python "$SCRIPT_DIR/benchmark.py" \
        --framework "$name" \
        --port "$port" \
        --concurrency "$CONCURRENCY_ARG" \
        --requests "$BENCHMARK_REQUESTS" \
        --warmup "$WARMUP_REQUESTS" \
        --output "$BENCH_OUT" \
        --split "$SPLIT" \
        $MODEL_FLAG || true

    if [ -n "$METAL_PID" ]; then
        kill -TERM "$METAL_PID" 2>/dev/null || true
        wait "$METAL_PID" 2>/dev/null || true
    fi
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
python "$SCRIPT_DIR/collect_results.py" --results-dir "$SPLIT_RESULTS_DIR"
python "$SCRIPT_DIR/generate_report.py" --results-dir "$SPLIT_RESULTS_DIR"

echo ""
echo "========================================="
echo " AppleBench complete!"
echo "========================================="
