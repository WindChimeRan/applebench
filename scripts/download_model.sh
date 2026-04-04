#!/bin/bash
# Download Qwen3-0.6B in all required formats
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "=== Downloading Qwen3-0.6B models ==="

# GGUF for llama.cpp / mistral.rs
if [ ! -f "$GGUF_MODEL" ]; then
    echo "Downloading GGUF model from $GGUF_REPO..."
    huggingface-cli download "$GGUF_REPO" "$GGUF_FILE" --local-dir "$MODELS_DIR"
    echo "GGUF model downloaded: $GGUF_MODEL"
else
    echo "GGUF model already exists: $GGUF_MODEL"
fi

# MLX format for mlx_lm
if [ ! -d "$MLX_MODEL" ]; then
    echo "Downloading MLX model from $MLX_REPO..."
    huggingface-cli download "$MLX_REPO" --local-dir "$MLX_MODEL"
    echo "MLX model downloaded: $MLX_MODEL"
else
    echo "MLX model already exists: $MLX_MODEL"
fi

# Safetensors for vllm-metal
if [ ! -d "$HF_MODEL" ]; then
    echo "Downloading HF model from $HF_REPO..."
    huggingface-cli download "$HF_REPO" --local-dir "$HF_MODEL"
    echo "HF model downloaded: $HF_MODEL"
else
    echo "HF model already exists: $HF_MODEL"
fi

echo "=== All models downloaded ==="
