# Model profile: Qwen3-0.6B (BF16, no quantization)
MODEL_NAME="Qwen3-0.6B"
GGUF_REPO="unsloth/Qwen3-0.6B-GGUF"
GGUF_FILE="Qwen3-0.6B-BF16.gguf"
MLX_REPO="mlx-community/Qwen3-0.6B-bf16"
MLX_DIR_NAME="Qwen3-0.6B-bf16-mlx"
HF_REPO="Qwen/Qwen3-0.6B"
HF_DIR_NAME="Qwen3-0.6B"
# Ollama pulls from the official registry instead of importing our GGUF so
# the chat template and stop tokens come from the published manifest. FP16
# matches the BF16 used by other frameworks within 16-bit rounding.
OLLAMA_MODEL_NAME="qwen3:0.6b-fp16"
