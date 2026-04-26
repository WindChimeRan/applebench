#!/bin/bash
# Install mlx_lm in its own venv
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$VENVS_DIR/mlx_lm"

echo "=== Installing mlx_lm ==="

if [ -d "$VENV_DIR" ]; then
    echo "Venv already exists at $VENV_DIR"
else
    uv venv "$VENV_DIR" --python 3.12
fi

source "$VENV_DIR/bin/activate"
# Track mlx-lm's git main instead of the PyPI release. PyPI 0.31.2 uses
# mx.new_stream for the generation stream, which breaks under mlx 0.31.2+
# (thread-local streams) because the server's BatchGenerator worker thread
# can't reach a stream created on the main thread. Upstream fix landed on
# main as ed1fca4 ("Thread local generation stream", #1090) — switches to
# mx.new_thread_local_stream + threads the stream through BatchGenerator.
# Revert to plain `mlx-lm` once a PyPI release contains that commit.
uv pip install "mlx-lm @ git+https://github.com/ml-explore/mlx-lm"

echo "=== mlx_lm installed ==="

# Sibling venv for mlx-vlm. Multimodal MLX ports (e.g.
# mlx-community/gemma-4-e4b-it-bf16) embed weights with the multimodal
# layout (`language_model.model.<X>`, `vision_tower.*`, `audio_tower.*`)
# that mlx_lm's text-only loader doesn't recognize. mlx-vlm understands
# that layout and exposes the same /v1/chat/completions endpoint, so we
# can route by MLX_BACKEND=mlx_vlm in the model profile without touching
# benchmark code.
VLM_VENV="$VENVS_DIR/mlx_vlm"
echo "=== Installing mlx_vlm (sibling venv for multimodal MLX ports) ==="
if [ -d "$VLM_VENV" ]; then
    echo "Venv already exists at $VLM_VENV"
else
    uv venv "$VLM_VENV" --python 3.12
fi
source "$VLM_VENV/bin/activate"
# torch + torchvision are pulled in for HF transformers' video processor
# class hierarchy (e.g. Qwen3VLVideoProcessor used by Qwen3.5 multimodal
# packages even when serving text-only). mlx-vlm itself doesn't need
# torch at runtime, but AutoProcessor.from_pretrained instantiates the
# video processor as a sub-processor and crashes on import without it.
uv pip install mlx-vlm torch torchvision
echo "=== mlx_vlm installed ==="
