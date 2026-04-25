# Model profile: Gemma-4-E4B-it (BF16, dense 4.5B-effective / 8B-total)
#
# Multimodal (text/image/audio/video) but we benchmark text-only — the
# framework serve scripts don't load the vision/audio projectors, so the
# *.gguf is enough; mmproj-*.gguf files in the unsloth repo are not fetched.
MODEL_NAME="Gemma-4-E4B-it"
GGUF_REPO="unsloth/gemma-4-E4B-it-GGUF"
GGUF_FILE="gemma-4-E4B-it-BF16.gguf"
MLX_REPO="mlx-community/gemma-4-e4b-it-bf16"
MLX_DIR_NAME="gemma-4-e4b-it-bf16-mlx"
HF_REPO="google/gemma-4-E4B-it"
HF_DIR_NAME="Gemma-4-E4B-it"
# The mlx-community port is a multimodal mlx-vlm package (vision_tower,
# audio_tower, language_model.* keys). mlx_lm's text-only loader rejects
# it; route the mlx_lm framework slot through mlx_vlm.server instead.
export MLX_BACKEND="mlx_vlm"
# Ollama not in the "fast engines" chorus for this model; if it lands
# later, use the official registry tag (e.g. gemma-4:e4b-it-fp16) instead
# of falling back to the bare-FROM Modelfile path that broke Qwen3.
