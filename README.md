# AppleBench

Benchmark local LLM inference frameworks on Apple Silicon, side by side.

## Frameworks

| Framework | Backend | Model Format |
|-----------|---------|-------------|
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | C++ / Metal | GGUF |
| [mlx_lm](https://github.com/ml-explore/mlx-examples) | MLX / Metal | MLX 4-bit |
| [mistral.rs](https://github.com/EricLBuehler/mistral.rs) | Rust / Metal | GGUF |
| [vllm-metal](https://github.com/vllm-project/vllm-metal) | Python / MLX | Safetensors |

## Quick Start

```bash
# 1. Install everything
scripts/install_bench.sh      # benchmark dependencies
scripts/install_llamacpp.sh
scripts/install_mlx_lm.sh
scripts/install_mistralrs.sh
scripts/install_vllm_metal.sh
scripts/download_model.sh     # Qwen3-0.6B in all formats

# 2. Run full benchmark
scripts/run_all.sh

# 3. View results
cat results/REPORT.md
```

## Run a single framework

```bash
scripts/serve_llamacpp.sh
source .venvs/bench/bin/activate
python scripts/benchmark.py --framework llamacpp --port 8001 --concurrency 16,8,1
scripts/stop_llamacpp.sh
```

## Metrics

- **TTFT** — Time to first token (ms)
- **Throughput** — Tokens per second (per request, decode phase)
- **Aggregate throughput** — Total tokens / wall time across concurrent requests
- **ITL** — Inter-token latency (ms)
- **Latency** — End-to-end request latency (s)

Tested at concurrency levels: 16, 8, 1.

## Ports

| Framework | Port |
|-----------|------|
| llama.cpp | 8001 |
| mlx_lm | 8002 |
| mistral.rs | 8003 |
| vllm-metal | 8004 |

## Requirements

- macOS on Apple Silicon (M1/M2/M3/M4)
- [uv](https://docs.astral.sh/uv/) (Python env management)
- [Rust toolchain](https://rustup.rs/) (for mistral.rs)
- [Homebrew](https://brew.sh/) + cmake (for llama.cpp)
