#!/bin/bash
# AppleBench — Install all frameworks, models, and benchmark dependencies
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================="
echo " AppleBench — Installing everything"
echo " $(date)"
echo "========================================="
echo ""

for script in \
    install_bench.sh \
    install_llamacpp.sh \
    install_mlx_lm.sh \
    install_mistralrs.sh \
    install_vllm_metal.sh \
    install_omlx.sh \
    install_ollama.sh \
    install_inferrs.sh \
    install_vllm_mlx.sh \
    install_hf_transformers.sh \
    install_sglang.sh; do
    echo "==========================================="
    echo " Running $script"
    echo "==========================================="
    bash "$SCRIPT_DIR/$script"
    echo ""
done

echo "==========================================="
echo " Downloading models"
echo "==========================================="
bash "$SCRIPT_DIR/download_model.sh"
echo ""

echo "========================================="
echo " All installations complete!"
echo "========================================="
