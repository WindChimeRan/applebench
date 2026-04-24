#!/bin/bash
# End-to-end correctness eval: fetch (if needed) → build 0/5-shot prompts →
# run_eval against an OpenAI-compatible endpoint → score F1.
#
# Results land in: correctness/results/<backend>_<model_slug>_<Nshot>/{responses.jsonl,scores.json}
#
# Usage:
#   bash correctness/run.sh --backend vllm-nvidia --model Qwen/Qwen3-0.6B \
#                           --base-url http://localhost:8000
#
# Optional flags:
#   --shots "0 5"        Space-separated list of shot counts (default: "0 5")
#   --concurrency N      Parallel requests (default: 8)
#   --max-rows N         Cap dataset size (default: 0 = all 1147 rows)
#   --overwrite          Wipe existing responses.jsonl before re-running

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

BACKEND=""
MODEL=""
BASE_URL=""
SHOTS_LIST="0 5"
CONCURRENCY=8
MAX_ROWS=0
OVERWRITE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --backend)     BACKEND="$2"; shift 2 ;;
        --model)       MODEL="$2"; shift 2 ;;
        --base-url)    BASE_URL="$2"; shift 2 ;;
        --shots)       SHOTS_LIST="$2"; shift 2 ;;
        --concurrency) CONCURRENCY="$2"; shift 2 ;;
        --max-rows)    MAX_ROWS="$2"; shift 2 ;;
        --overwrite)   OVERWRITE="--overwrite"; shift ;;
        *)             echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

if [ -z "$BACKEND" ] || [ -z "$MODEL" ] || [ -z "$BASE_URL" ]; then
    echo "Usage: $0 --backend NAME --model MODEL --base-url URL [--shots '0 5'] [--concurrency 8] [--max-rows 0] [--overwrite]" >&2
    exit 1
fi

# Slugify the model name for directory use (strip "org/" prefix, replace special chars)
MODEL_SLUG=$(echo "$MODEL" | sed 's|.*/||' | tr -c 'A-Za-z0-9._-' '_')

# 1. Fetch dataset if not already present
if [ ! -f "$SCRIPT_DIR/data/GMRID_v3-test.csv" ] || [ ! -f "$SCRIPT_DIR/data/categories.json" ]; then
    echo "=== Fetching dataset ==="
    bash "$SCRIPT_DIR/scripts/fetch_data.sh"
    echo ""
fi

# 2. Build prompts for each shot count (idempotent — rebuilds every run so
# changes to build_prompts.py take effect; cheap, <1s for 1147 rows).
for N in $SHOTS_LIST; do
    MAX_ARG=""
    if [ "$MAX_ROWS" -gt 0 ]; then
        MAX_ARG="--max-rows $MAX_ROWS"
    fi
    echo "=== Building ${N}-shot prompts ==="
    python3 "$SCRIPT_DIR/scripts/build_prompts.py" --shots "$N" $MAX_ARG
    echo ""
done

# 3. Eval + score per shot count
for N in $SHOTS_LIST; do
    RESULT_DIR="$SCRIPT_DIR/results/${BACKEND}_${MODEL_SLUG}_${N}shot"
    mkdir -p "$RESULT_DIR"

    echo "=== Running eval (${N}-shot) → $RESULT_DIR ==="
    python3 "$SCRIPT_DIR/scripts/run_eval.py" \
        --base-url "$BASE_URL" \
        --model "$MODEL" \
        --prompts "$SCRIPT_DIR/prompts/${N}shot/prompts.jsonl" \
        --output "$RESULT_DIR/responses.jsonl" \
        --concurrency "$CONCURRENCY" \
        $OVERWRITE
    echo ""

    echo "=== Scoring (${N}-shot) ==="
    python3 "$SCRIPT_DIR/scripts/score_f1.py" \
        --responses "$RESULT_DIR/responses.jsonl" \
        --labels "$SCRIPT_DIR/prompts/${N}shot/labels.jsonl" \
        --output "$RESULT_DIR/scores.json"
    echo ""
done

echo "========================================="
echo " Correctness eval complete"
echo " Results:"
for N in $SHOTS_LIST; do
    RESULT_DIR="$SCRIPT_DIR/results/${BACKEND}_${MODEL_SLUG}_${N}shot"
    echo "   ${N}-shot: $RESULT_DIR/scores.json"
done
echo "========================================="
