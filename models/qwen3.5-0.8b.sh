# Model profile: Qwen3.5-0.8B (BF16, dense, hybrid Gated-DeltaNet attention)
#
# Multimodal (text/image/video, Qwen3_5ForConditionalGeneration) but we
# benchmark text-only — the framework serve scripts don't load the vision
# projector, so the *.gguf is enough; mmproj-*.gguf in the unsloth repo is
# not fetched.
MODEL_NAME="Qwen3.5-0.8B"
GGUF_REPO="unsloth/Qwen3.5-0.8B-GGUF"
GGUF_FILE="Qwen3.5-0.8B-BF16.gguf"
MLX_REPO="mlx-community/Qwen3.5-0.8B-bf16"
MLX_DIR_NAME="Qwen3.5-0.8B-bf16-mlx"
HF_REPO="Qwen/Qwen3.5-0.8B"
HF_DIR_NAME="Qwen3.5-0.8B"
# The mlx-community port is a multimodal mlx-vlm package (vision_tower,
# language_model.* keys). mlx_lm's text-only loader rejects it; route the
# mlx_lm framework slot through mlx_vlm.server instead — same pattern as
# gemma-4-e4b-it.
export MLX_BACKEND="mlx_vlm"
# Ollama and the slow engines (mistralrs, inferrs, vllm_mlx, hf_transformers)
# are out of scope for this profile — the user asked for the four fast Mac
# engines only. No OLLAMA_MODEL_NAME set.
