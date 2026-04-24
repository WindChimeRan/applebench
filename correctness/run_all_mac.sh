#!/bin/bash
# Correctness eval across all 9 AppleBench frameworks on Mac.
# Mirrors scripts/run_all.sh structure (serve → eval → stop → cleanup →
# cooldown per framework) but evaluates F1 on GMRID_v3 classification
# instead of perf.
#
# Usage:
#   bash correctness/run_all_mac.sh                              # all 9 frameworks, 0-shot + 5-shot
#   bash correctness/run_all_mac.sh llamacpp omlx                # restrict to a subset
#   bash correctness/run_all_mac.sh --skip-existing              # resume — skip (fw × shot) cells already scored
#   bash correctness/run_all_mac.sh --overwrite-responses llamacpp  # force re-run after a fix
#   bash correctness/run_all_mac.sh --max-rows 20                # smoke test
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPLEBENCH_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ONLY_FRAMEWORKS=()
SHOTS_LIST="0 5"
CONCURRENCY=8
MAX_ROWS=0
SKIP_EXISTING=false
OVERWRITE_RESPONSES=""
EVAL_TIMEOUT_SECONDS=7200

while [[ $# -gt 0 ]]; do
    case "$1" in
        --model)
            export APPLEBENCH_MODEL="$2"
            shift 2 ;;
        --shots)
            SHOTS_LIST="$2"
            shift 2 ;;
        --concurrency)
            CONCURRENCY="$2"
            shift 2 ;;
        --max-rows)
            MAX_ROWS="$2"
            shift 2 ;;
        --eval-timeout)
            EVAL_TIMEOUT_SECONDS="$2"
            shift 2 ;;
        --skip-existing)
            SKIP_EXISTING=true
            shift ;;
        --overwrite-responses)
            OVERWRITE_RESPONSES="--overwrite"
            shift ;;
        *)
            ONLY_FRAMEWORKS+=("$1")
            shift ;;
    esac
done

source "$APPLEBENCH_ROOT/scripts/config.sh"

# Activate correctness venv if present, else fall back to whatever Python is
# in PATH (will fail loudly on missing aiohttp/sklearn — which is fine).
CORRECTNESS_VENV="$APPLEBENCH_ROOT/.venvs/correctness"
if [ -d "$CORRECTNESS_VENV" ]; then
    source "$CORRECTNESS_VENV/bin/activate"
fi
export PYTHONUNBUFFERED=1

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
    sleep 5
}

# Same framework array as scripts/run_all.sh — duplicated intentionally so
# correctness/ stays deletable without touching scripts/.
FRAMEWORKS=(
    "vllm_metal:$VLLM_METAL_PORT:serve_vllm_metal.sh:stop_vllm_metal.sh:"
    "llamacpp:$LLAMACPP_PORT:serve_llamacpp.sh:stop_llamacpp.sh:"
    "mlx_lm:$MLX_LM_PORT:serve_mlx_lm.sh:stop_mlx_lm.sh:$MLX_MODEL"
    "mistralrs:$MISTRALRS_PORT:serve_mistralrs.sh:stop_mistralrs.sh:"
    "omlx:$OMLX_PORT:serve_omlx.sh:stop_omlx.sh:"
    "ollama:$OLLAMA_PORT:serve_ollama.sh:stop_ollama.sh:$OLLAMA_MODEL_NAME"
    "inferrs:$INFERRS_PORT:serve_inferrs.sh:stop_inferrs.sh:"
    "vllm_mlx:$VLLM_MLX_PORT:serve_vllm_mlx.sh:stop_vllm_mlx.sh:$MLX_MODEL"
    "hf_transformers:$HF_TRANSFORMERS_PORT:serve_hf_transformers.sh:stop_hf_transformers.sh:$HF_MODEL"
)

RESULTS_DIR="$SCRIPT_DIR/results"
mkdir -p "$RESULTS_DIR"

# Slug for result-dir names — matches run.sh's scheme
MODEL_SLUG="$MODEL_NAME"

echo "========================================="
echo " Correctness Eval — All Frameworks (Mac)"
echo " Model: $MODEL_NAME"
echo " Shots: $SHOTS_LIST"
echo " Concurrency: $CONCURRENCY"
echo " Skip-existing: $SKIP_EXISTING"
echo " Overwrite-responses: ${OVERWRITE_RESPONSES:-no}"
echo " Eval timeout: ${EVAL_TIMEOUT_SECONDS}s"
if [ "$MAX_ROWS" -gt 0 ]; then
    echo " Max rows: $MAX_ROWS (SMOKE TEST)"
fi
echo " $(date)"
echo "========================================="
echo ""

# Fetch dataset if missing
if [ ! -f "$SCRIPT_DIR/data/GMRID_v3-test.csv" ] || [ ! -f "$SCRIPT_DIR/data/categories.json" ]; then
    echo "=== Fetching dataset ==="
    bash "$SCRIPT_DIR/scripts/fetch_data.sh"
    echo ""
fi

# Build prompts once (idempotent)
MAX_ARG=""
if [ "$MAX_ROWS" -gt 0 ]; then
    MAX_ARG="--max-rows $MAX_ROWS"
fi
for N in $SHOTS_LIST; do
    echo "=== Building ${N}-shot prompts ==="
    python3 "$SCRIPT_DIR/scripts/build_prompts.py" --shots "$N" $MAX_ARG
    echo ""
done

cleanup

for entry in "${FRAMEWORKS[@]}"; do
    IFS=':' read -r name port serve stop model_override <<< "$entry"

    if [ ${#ONLY_FRAMEWORKS[@]} -gt 0 ]; then
        match=false
        for f in "${ONLY_FRAMEWORKS[@]}"; do
            [ "$f" = "$name" ] && match=true
        done
        $match || continue
    fi

    # Determine which shot cells need to run for this framework
    shots_needed=()
    for N in $SHOTS_LIST; do
        scores_file="$RESULTS_DIR/${name}_${MODEL_SLUG}_${N}shot/scores.json"
        if [ "$SKIP_EXISTING" = "true" ] && [ -f "$scores_file" ]; then
            echo "Skipping $name ${N}-shot — scores.json exists"
            continue
        fi
        shots_needed+=("$N")
    done

    if [ ${#shots_needed[@]} -eq 0 ]; then
        echo "All shots done for $name — not booting server."
        echo ""
        continue
    fi

    echo "==========================================="
    echo " $name (port $port) — shots needed: ${shots_needed[*]}"
    echo "==========================================="

    echo "Starting $name server..."
    if ! bash "$APPLEBENCH_ROOT/scripts/$serve"; then
        echo "  FAILED to start $name — skipping."
        cleanup
        echo ""
        continue
    fi
    echo ""

    MODEL_FLAG=""
    if [ -n "$model_override" ]; then
        MODEL_FLAG="--model $model_override"
    else
        # Ask the server what model name it expects
        MODEL_FLAG="--model $(curl -sf "http://localhost:${port}/v1/models" \
            | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data'][0]['id'])" \
            2>/dev/null || echo "unknown")"
    fi

    for N in "${shots_needed[@]}"; do
        RESULT_DIR="$RESULTS_DIR/${name}_${MODEL_SLUG}_${N}shot"
        mkdir -p "$RESULT_DIR"

        echo "--- ${name} ${N}-shot eval (timeout ${EVAL_TIMEOUT_SECONDS}s) ---"
        rc=0
        perl -e 'alarm shift; exec @ARGV' "$EVAL_TIMEOUT_SECONDS" \
            python3 "$SCRIPT_DIR/scripts/run_eval.py" \
            --base-url "http://localhost:${port}" \
            $MODEL_FLAG \
            --prompts "$SCRIPT_DIR/prompts/${N}shot/prompts.jsonl" \
            --output "$RESULT_DIR/responses.jsonl" \
            --concurrency "$CONCURRENCY" \
            $OVERWRITE_RESPONSES || rc=$?
        # rc=142 means perl's alarm fired (128 + SIGALRM=14) — i.e. hit --eval-timeout.
        if [ "$rc" = "142" ]; then
            echo "  TIMEOUT after ${EVAL_TIMEOUT_SECONDS}s — will score whatever was written so far"
        elif [ "$rc" != "0" ]; then
            echo "  eval exited rc=$rc — will score whatever was written so far"
        fi

        echo "--- ${name} ${N}-shot score ---"
        python3 "$SCRIPT_DIR/scripts/score_f1.py" \
            --responses "$RESULT_DIR/responses.jsonl" \
            --labels "$SCRIPT_DIR/prompts/${N}shot/labels.jsonl" \
            --output "$RESULT_DIR/scores.json" || true
        echo ""
    done

    echo "Stopping $name server..."
    bash "$APPLEBENCH_ROOT/scripts/$stop" || true
    cleanup
    echo "Cooling down ${COOLDOWN_SECONDS}s..."
    sleep "$COOLDOWN_SECONDS"
    echo ""
done

echo "==========================================="
echo " Aggregating scores"
echo "==========================================="
python3 "$SCRIPT_DIR/scripts/aggregate_scores.py" \
    --results-dir "$RESULTS_DIR" \
    --model "$MODEL_SLUG" \
    --shots "$SHOTS_LIST"

echo ""
echo "========================================="
echo " Correctness eval complete"
echo "========================================="
