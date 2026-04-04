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
# 1. Install frameworks
scripts/install_bench.sh        # benchmark dependencies
scripts/install_llamacpp.sh
scripts/install_mlx_lm.sh
scripts/install_mistralrs.sh
scripts/install_vllm_metal.sh

# 2. Download model + prepare dataset
scripts/download_model.sh       # Qwen3-0.6B in all formats
scripts/prepare_dataset.py      # 100 prompts from OpenOrca + CNN/DailyMail

# 3. Run full benchmark
scripts/run_all.sh

# 4. View results
cat results/REPORT.md
```

## Run a single framework

```bash
scripts/serve_llamacpp.sh
source .venvs/bench/bin/activate
python scripts/benchmark.py --framework llamacpp --port 8001 --concurrency 16,8,1 --requests 100
scripts/stop_llamacpp.sh
```

## Dataset

100 prompts sampled from [Open-Orca/OpenOrca](https://huggingface.co/datasets/Open-Orca/OpenOrca) and [CNN/DailyMail](https://huggingface.co/datasets/abisee/cnn_dailymail), distributed across input/output length buckets:

| Bucket | Input tokens | Output tokens | Count |
|--------|-------------|--------------|-------|
| Short | 10–80 | 64 / 256 | 20 |
| Medium | 80–500 | 64 / 256 | 20 |
| Long | 500–2,000 | 64 / 256 | 30 |
| Very long | 2,000–4,000 | 64 / 256 | 30 |

This covers realistic workloads from quick Q&A through long-document processing, with both short and long generation targets. All prompts are real natural language (not synthetic tokens), seeded for reproducibility.

Run `scripts/prepare_dataset.py` to regenerate. Cached data is stored in `.models/` (gitignored).

## Metrics

- **TTFT** — Time to first token (ms)
- **Throughput** — Tokens per second (per request, decode phase)
- **Aggregate throughput** — Total tokens / wall time across concurrent requests
- **ITL** — Inter-token latency (ms)
- **Latency** — End-to-end request latency (s)

Tested at concurrency levels: 16, 8, 1. Each level runs 100 requests with 3 warmup requests. A 30-second cooldown between frameworks prevents thermal throttling from skewing results.

## Model

[Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) — small enough for fast benchmark runs, available in all required formats:

| Format | Source | Used by |
|--------|--------|---------|
| GGUF Q4_K_M | [unsloth/Qwen3-0.6B-GGUF](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) | llama.cpp, mistral.rs |
| MLX 4-bit | [mlx-community/Qwen3-0.6B-4bit](https://huggingface.co/mlx-community/Qwen3-0.6B-4bit) | mlx_lm |
| Safetensors | [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) | vllm-metal |

## Ports

| Framework | Port |
|-----------|------|
| llama.cpp | 8001 |
| mlx_lm | 8002 |
| mistral.rs | 8003 |
| vllm-metal | 8004 |

## Scripts

| Script | Purpose |
|--------|---------|
| `install_<fw>.sh` | First-time setup for each framework |
| `update_<fw>.sh` | Pull latest version and rebuild |
| `serve_<fw>.sh` / `stop_<fw>.sh` | Start/stop framework server |
| `download_model.sh` | Download Qwen3-0.6B in all formats |
| `prepare_dataset.py` | Sample prompts from HuggingFace datasets |
| `benchmark.py` | Run benchmark against any OpenAI-compatible endpoint |
| `collect_results.py` | Aggregate per-framework results into comparison JSON |
| `generate_report.py` | Generate markdown report from comparison |
| `sync_github.sh` | Commit and push results to GitHub |
| `run_all.sh` | Full pipeline: serve → benchmark → stop → next framework |

## Weekly updates

To benchmark the latest versions of all frameworks:

```bash
scripts/update_llamacpp.sh
scripts/update_mlx_lm.sh
scripts/update_mistralrs.sh
scripts/update_vllm_metal.sh
scripts/run_all.sh
scripts/sync_github.sh
```

## Requirements

- macOS on Apple Silicon (M1/M2/M3/M4)
- [uv](https://docs.astral.sh/uv/) (Python env management)
- [Rust toolchain](https://rustup.rs/) (for mistral.rs)
- [Homebrew](https://brew.sh/) + cmake (for llama.cpp)
