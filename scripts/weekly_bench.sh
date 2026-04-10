#!/bin/bash
# AppleBench — Weekly unattended benchmark run
#
# Runs update_all.sh → run_all.sh → sync_github.sh end-to-end, under
# `caffeinate -i` to prevent sleep, with all output tee'd to a dated log.
# This is the happy-path wrapper. Intelligent failure recovery lives in
# the /weekly-bench skill, not here.
#
# Usage: bash scripts/weekly_bench.sh [--skip-update] [--model MODEL] [--split SPLIT]
#                                     [--skip-existing] [framework ...]
#
# Examples:
#   bash scripts/weekly_bench.sh                         # full weekly run
#   bash scripts/weekly_bench.sh --skip-update           # skip update_all.sh
#   bash scripts/weekly_bench.sh --skip-existing         # resume today's run
#   bash scripts/weekly_bench.sh --model qwen3-30b-a3b   # specific model

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse wrapper-only flags before sourcing config
SKIP_UPDATE=false
RUN_ALL_ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-update)
            SKIP_UPDATE=true
            shift
            ;;
        --model)
            export APPLEBENCH_MODEL="$2"
            RUN_ALL_ARGS+=("$1" "$2")
            shift 2
            ;;
        *)
            RUN_ALL_ARGS+=("$1")
            shift
            ;;
    esac
done

source "$SCRIPT_DIR/config.sh"

DATE=$(date +%Y-%m-%d)
START_TS=$(date +%Y-%m-%dT%H:%M:%S)
LOG="$RESULTS_DIR/weekly_${DATE}.log"
mkdir -p "$(dirname "$LOG")"

# Verify caffeinate is available (macOS only)
if ! command -v caffeinate &>/dev/null; then
    echo "warning: caffeinate not found — Mac may sleep during long runs"
    CAFFEINATE=""
else
    # -i: prevent idle sleep; -m: prevent disk sleep
    CAFFEINATE="caffeinate -i -m"
fi

run_step() {
    local label="$1"
    shift
    echo ""
    echo "========================================="
    echo " [$(date +%H:%M:%S)] $label"
    echo "========================================="
    if "$@"; then
        echo "[$(date +%H:%M:%S)] $label: OK"
        return 0
    else
        local rc=$?
        echo "[$(date +%H:%M:%S)] $label: FAILED (exit $rc)"
        return $rc
    fi
}

{
    echo "========================================="
    echo " AppleBench — Weekly Run"
    echo " Started: $START_TS"
    echo " Model: $MODEL_NAME"
    echo " Log: $LOG"
    echo " Skip update: $SKIP_UPDATE"
    echo " Run args: ${RUN_ALL_ARGS[*]}"
    echo "========================================="

    # Step 1: update frameworks (optional)
    if [ "$SKIP_UPDATE" = "false" ]; then
        run_step "update_all.sh" $CAFFEINATE bash "$SCRIPT_DIR/update_all.sh" || \
            echo "update_all.sh failed — continuing to benchmark anyway"
    else
        echo ""
        echo "Skipping update_all.sh (--skip-update)"
    fi

    # Step 2: run benchmarks
    # Don't abort on failure — the skill layer decides what to do next.
    run_step "run_all.sh" $CAFFEINATE bash "$SCRIPT_DIR/run_all.sh" "${RUN_ALL_ARGS[@]}" || \
        echo "run_all.sh had failures — results may be incomplete"

    # Step 3: sync results (only if REPORT.md exists, meaning something ran)
    if [ -f "$RESULTS_DIR/REPORT.md" ]; then
        run_step "sync_github.sh" bash "$SCRIPT_DIR/sync_github.sh" || \
            echo "sync_github.sh failed — results saved locally but not pushed"
    else
        echo ""
        echo "Skipping sync_github.sh — no REPORT.md found"
    fi

    echo ""
    echo "========================================="
    echo " Weekly run finished: $(date +%Y-%m-%dT%H:%M:%S)"
    echo "========================================="
} 2>&1 | tee -a "$LOG"
