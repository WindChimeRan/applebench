#!/bin/bash
# AppleBench configuration — sourced by all scripts

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAMEWORKS_DIR="$PROJECT_DIR/.frameworks"
VENVS_DIR="$PROJECT_DIR/.venvs"
MODELS_DIR="$PROJECT_DIR/.models"
RESULTS_DIR="$PROJECT_DIR/results"
SCRIPTS_DIR="$PROJECT_DIR/scripts"

# Ports (one per framework)
LLAMACPP_PORT=8001
MLX_LM_PORT=8002
MISTRALRS_PORT=8003
VLLM_METAL_PORT=8004

# Model
MODEL_NAME="Qwen3-0.6B"
GGUF_REPO="unsloth/Qwen3-0.6B-GGUF"
GGUF_FILE="Qwen3-0.6B-Q4_K_M.gguf"
GGUF_MODEL="$MODELS_DIR/$GGUF_FILE"
MLX_REPO="mlx-community/Qwen3-0.6B-4bit"
MLX_MODEL="$MODELS_DIR/Qwen3-0.6B-4bit-mlx"
HF_REPO="Qwen/Qwen3-0.6B"
HF_MODEL="$MODELS_DIR/Qwen3-0.6B"

# Benchmark
CONCURRENCY_LEVELS="16 8 1"
COOLDOWN_SECONDS=30
WARMUP_REQUESTS=3
BENCHMARK_REQUESTS=10  # per concurrency level

# Ensure directories exist
mkdir -p "$FRAMEWORKS_DIR" "$VENVS_DIR" "$MODELS_DIR" "$RESULTS_DIR"
