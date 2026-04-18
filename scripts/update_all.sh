#!/bin/bash
# AppleBench — Update all frameworks to latest versions
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================="
echo " AppleBench — Updating all frameworks"
echo " $(date)"
echo "========================================="
echo ""

for script in \
    update_llamacpp.sh \
    update_mlx_lm.sh \
    update_mistralrs.sh \
    update_vllm_metal.sh \
    update_omlx.sh \
    update_ollama.sh \
    update_inferrs.sh \
    update_vllm_mlx.sh \
    update_hf_transformers.sh; do
    echo "==========================================="
    echo " Running $script"
    echo "==========================================="
    bash "$SCRIPT_DIR/$script" || {
        echo "WARNING: $script failed, continuing..."
    }
    echo ""
done

echo "========================================="
echo " All updates complete!"
echo "========================================="
