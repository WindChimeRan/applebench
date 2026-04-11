#!/bin/bash
# AppleBench configuration — sourced by all scripts

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAMEWORKS_DIR="$PROJECT_DIR/.frameworks"
VENVS_DIR="$PROJECT_DIR/.venvs"
MODELS_DIR="$PROJECT_DIR/.models"
RESULTS_BASE_DIR="$PROJECT_DIR/results"
SCRIPTS_DIR="$PROJECT_DIR/scripts"

# Ports (one per framework)
LLAMACPP_PORT=8001
MLX_LM_PORT=8002
MISTRALRS_PORT=8003
VLLM_METAL_PORT=8004
OMLX_PORT=8005
OLLAMA_PORT=8006
INFERRS_PORT=8007
VLLM_MLX_PORT=8008

# Model profile — set APPLEBENCH_MODEL env var to switch models
# Default: qwen3-0.6b. See models/*.sh for available profiles.
APPLEBENCH_MODEL="${APPLEBENCH_MODEL:-qwen3-0.6b}"
MODEL_PROFILE="$PROJECT_DIR/models/${APPLEBENCH_MODEL}.sh"
if [ ! -f "$MODEL_PROFILE" ]; then
    echo "Error: model profile not found: $MODEL_PROFILE"
    echo "Available profiles:"
    ls "$PROJECT_DIR/models/"*.sh 2>/dev/null | xargs -n1 basename | sed 's/\.sh$//'
    exit 1
fi
source "$MODEL_PROFILE"

# Derived model paths
GGUF_MODEL="$MODELS_DIR/$GGUF_FILE"
MLX_MODEL="$MODELS_DIR/$MLX_DIR_NAME"
HF_MODEL="$MODELS_DIR/$HF_DIR_NAME"
RESULTS_DIR="$RESULTS_BASE_DIR/$MODEL_NAME"
OLLAMA_MODEL_NAME="$(echo "$MODEL_NAME" | tr '[:upper:]' '[:lower:]')-bf16"

# Benchmark
CONCURRENCY_LEVELS="1 8 16"
COOLDOWN_SECONDS=60
WARMUP_REQUESTS=3
BENCHMARK_REQUESTS=100  # per concurrency level

# Ensure directories exist
mkdir -p "$FRAMEWORKS_DIR" "$VENVS_DIR" "$MODELS_DIR" "$RESULTS_BASE_DIR" "$RESULTS_DIR"
