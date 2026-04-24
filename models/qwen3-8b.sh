# Model profile: Qwen3-8B (BF16, 8B dense)
MODEL_NAME="Qwen3-8B"
GGUF_REPO="unsloth/Qwen3-8B-GGUF"
GGUF_FILE="Qwen3-8B-BF16.gguf"
MLX_REPO="mlx-community/Qwen3-8B-bf16"
MLX_DIR_NAME="Qwen3-8B-bf16-mlx"
HF_REPO="Qwen/Qwen3-8B"
HF_DIR_NAME="Qwen3-8B"
# See qwen3-0.6b.sh for the rationale; pulling fp16 from the registry so we
# get a working chat template without hand-writing a Modelfile.
OLLAMA_MODEL_NAME="qwen3:8b-fp16"
