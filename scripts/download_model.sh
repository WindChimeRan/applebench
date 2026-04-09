#!/bin/bash
# Download model in all required formats
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Accept --model flag
while [[ $# -gt 0 ]]; do
    case "$1" in
        --model) export APPLEBENCH_MODEL="$2"; shift 2 ;;
        *) shift ;;
    esac
done

source "$SCRIPT_DIR/config.sh"

echo "=== Downloading $MODEL_NAME models ==="

# GGUF for llama.cpp / mistral.rs
if [ ! -f "$GGUF_MODEL" ]; then
    echo "Downloading GGUF model from $GGUF_REPO..."
    hf download "$GGUF_REPO" "$GGUF_FILE" --local-dir "$MODELS_DIR"
    echo "GGUF model downloaded: $GGUF_MODEL"
else
    echo "GGUF model already exists: $GGUF_MODEL"
fi

# MLX format for mlx_lm
if [ ! -d "$MLX_MODEL" ]; then
    echo "Downloading MLX model from $MLX_REPO..."
    hf download "$MLX_REPO" --local-dir "$MLX_MODEL"
    echo "MLX model downloaded: $MLX_MODEL"
else
    echo "MLX model already exists: $MLX_MODEL"
fi

# Safetensors for vllm-metal
if [ ! -d "$HF_MODEL" ]; then
    echo "Downloading HF model from $HF_REPO..."
    hf download "$HF_REPO" --local-dir "$HF_MODEL"
    echo "HF model downloaded: $HF_MODEL"
else
    echo "HF model already exists: $HF_MODEL"
fi

echo "=== All models downloaded ==="
