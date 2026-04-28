#!/bin/bash
# AppleBench — Verify system prerequisites and framework readiness
# Exit 1 on hard errors (missing system tools), 0 otherwise.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

ERRORS=0
WARNINGS=0

ok()   { echo "  [ok]   $1"; }
fail() { echo "  [FAIL] $1"; echo "         $2"; ERRORS=$((ERRORS + 1)); }
warn() { echo "  [warn] $1"; echo "         $2"; WARNINGS=$((WARNINGS + 1)); }

check_cmd() {
    local label="$1" cmd="$2" hint="$3"
    if command -v "$cmd" &>/dev/null; then
        ok "$label"
    else
        fail "$label not found" "Install: $hint"
    fi
}

echo "=== AppleBench Environment Check ==="
echo ""

# --- Platform ---
echo "Platform:"
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    ok "Apple Silicon ($ARCH)"
else
    fail "Requires Apple Silicon (found: $ARCH)" ""
fi

if xcode-select -p &>/dev/null; then
    ok "Xcode Command Line Tools"
else
    warn "Xcode Command Line Tools not found" "Run: xcode-select --install"
fi
echo ""

# --- System tools ---
echo "Required tools:"
check_cmd "uv"              "uv"              "curl -LsSf https://astral.sh/uv/install.sh | sh"
# cmake/cargo are build-time only — warn instead of fail if frameworks already built
if command -v cmake &>/dev/null; then
    ok "cmake"
elif [ -f "$FRAMEWORKS_DIR/llama.cpp/build/bin/llama-server" ]; then
    warn "cmake not found (llama.cpp already built)" "brew install cmake"
else
    fail "cmake not found" "Install: brew install cmake"
fi

if command -v cargo &>/dev/null; then
    ok "cargo"
elif [ -f "$FRAMEWORKS_DIR/mistral.rs/target/release/mistralrs" ]; then
    warn "cargo not found (mistral.rs already built)" "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
else
    fail "cargo not found" "Install: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
fi
check_cmd "huggingface-cli (hf)" "hf" "uv tool install huggingface_hub"
echo ""

# --- Python 3.12 ---
echo "Python:"
if command -v uv &>/dev/null && uv python find 3.12 &>/dev/null 2>&1; then
    ok "Python 3.12 ($(uv python find 3.12 2>/dev/null))"
elif command -v python3.12 &>/dev/null; then
    ok "Python 3.12 ($(python3.12 --version 2>&1))"
else
    fail "Python 3.12 not found" "Install: uv python install 3.12"
fi
echo ""

# --- Framework installs ---
echo "Frameworks (run install scripts if missing):"

if [ -f "$FRAMEWORKS_DIR/llama.cpp/build/bin/llama-server" ]; then
    ok "llama.cpp"
else
    warn "llama.cpp not built" "Run: scripts/install_llamacpp.sh"
fi

if [ -d "$VENVS_DIR/mlx_lm" ]; then
    ok "mlx_lm"
else
    warn "mlx_lm venv not found" "Run: scripts/install_mlx_lm.sh"
fi

if [ -f "$FRAMEWORKS_DIR/mistral.rs/target/release/mistralrs" ]; then
    ok "mistral.rs"
else
    warn "mistral.rs not built" "Run: scripts/install_mistralrs.sh"
fi

if [ -d "$HOME/.venv-vllm-metal" ]; then
    ok "vllm-metal"
else
    warn "vllm-metal not installed" "Run: scripts/install_vllm_metal.sh"
fi

if [ -d "$VENVS_DIR/omlx" ]; then
    ok "omlx"
else
    warn "omlx venv not found" "Run: scripts/install_omlx.sh"
fi

if command -v ollama &>/dev/null; then
    ok "ollama"
else
    warn "ollama not found" "Run: scripts/install_ollama.sh"
fi

if [ -f "$FRAMEWORKS_DIR/inferrs/target/release/inferrs" ]; then
    ok "inferrs"
else
    warn "inferrs binary not found" "Run: scripts/install_inferrs.sh"
fi

if [ -d "$VENVS_DIR/vllm_mlx" ]; then
    ok "vllm-mlx"
else
    warn "vllm-mlx venv not found" "Run: scripts/install_vllm_mlx.sh"
fi

if [ -d "$VENVS_DIR/hf_transformers" ]; then
    ok "hf_transformers"
else
    warn "hf_transformers venv not found" "Run: scripts/install_hf_transformers.sh"
fi

if [ -d "$VENVS_DIR/sglang" ]; then
    ok "sglang"
else
    warn "sglang venv not found" "Run: scripts/install_sglang.sh"
fi
echo ""

# --- Models ---
echo "Models (run scripts/download_model.sh if missing):"

if [ -f "$GGUF_MODEL" ]; then
    ok "GGUF: $GGUF_FILE"
else
    warn "GGUF model missing" "$GGUF_MODEL"
fi

if [ -d "$MLX_MODEL" ]; then
    ok "MLX: $(basename "$MLX_MODEL")"
else
    warn "MLX model missing" "$MLX_MODEL"
fi

if [ -d "$HF_MODEL" ]; then
    ok "HF: $(basename "$HF_MODEL")"
else
    warn "HF model missing" "$HF_MODEL"
fi
echo ""

# --- Benchmark venv ---
echo "Benchmark:"
if [ -d "$VENVS_DIR/bench" ]; then
    ok "bench venv"
else
    warn "bench venv not found" "Run: scripts/install_bench.sh"
fi
echo ""

# --- Summary ---
echo "==========================================="
if [ $ERRORS -gt 0 ]; then
    echo " $ERRORS error(s), $WARNINGS warning(s)"
    echo " Fix errors before proceeding."
    echo "==========================================="
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo " All prerequisites met, $WARNINGS warning(s)"
    echo "==========================================="
    exit 0
else
    echo " All checks passed"
    echo "==========================================="
    exit 0
fi
