# AppleBench

Benchmark local LLM inference frameworks on Apple Silicon, side by side.

## Frameworks

| Framework | Backend | Model Format |
|-----------|---------|-------------|
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | C++ / Metal | GGUF |
| [mlx_lm](https://github.com/ml-explore/mlx-examples) | MLX / Metal | MLX BF16 |
| [mistral.rs](https://github.com/EricLBuehler/mistral.rs) | Rust / Metal | GGUF |
| [vllm-metal](https://github.com/vllm-project/vllm-metal) | Python / MLX | Safetensors |
| [omlx](https://github.com/jundot/omlx) | MLX / Metal | MLX BF16 |
| [ollama](https://github.com/ollama/ollama) | Go + Metal | GGUF |
| [inferrs](https://github.com/ericcurtin/inferrs) | Rust + Candle / Metal | Safetensors |

## Quick Start

```bash
# 1. Install everything (all frameworks + models)
scripts/install_all.sh

# 2. Run full benchmark (chat split, default)
scripts/run_all.sh

# 3. Run with agent split (multi-turn, tool-calling)
scripts/run_all.sh --split agent

# 4. View results
cat results/REPORT.md
```

## Run a single framework

```bash
scripts/run_all.sh llamacpp                    # just llama.cpp (chat split)
scripts/run_all.sh --split agent llamacpp      # agent split
scripts/run_all.sh omlx ollama                 # multiple specific frameworks
```

## Dataset

Two splits are available, each with 100 prompts:

### Chat split (default) — `prompts/chat_benchmark_prompts.json`

Single-turn prompts sampled from [Open-Orca/OpenOrca](https://huggingface.co/datasets/Open-Orca/OpenOrca) and [CNN/DailyMail](https://huggingface.co/datasets/abisee/cnn_dailymail), distributed across input/output length buckets:

| Bucket | Input tokens | Output tokens | Count |
|--------|-------------|--------------|-------|
| Short | 10–80 | 64 / 256 | 20 |
| Medium | 80–500 | 64 / 256 | 20 |
| Long | 500–2,000 | 64 / 256 | 30 |
| Very long | 2,000–4,000 | 64 / 256 | 30 |

Covers realistic workloads from quick Q&A through long-document processing, with both short and long generation targets. All prompts are real natural language (not synthetic tokens), seeded for reproducibility.

### Agent split — `prompts/agent_benchmark_prompts.json`

Multi-turn agentic prompts with tool calls and tool responses already baked into the conversation history. Tests how frameworks handle realistic agent workloads (long contexts, tool-calling payloads) without needing an actual agent runtime. Composed from three popular agentic benchmarks:

| Source | Count | Content |
|--------|-------|---------|
| [BFCL V3 multi-turn](https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html) | 35 | File system, trading, travel, vehicle control, messaging tools |
| [Hermes Agent Reasoning Traces](https://huggingface.co/datasets/lambda/hermes-agent-reasoning-traces) | 35 | Real multi-turn agent sessions with tool calls + results |
| [ClawsBench](https://clawsbench.benchflow.ai) | 30 | Gmail, Slack, Calendar, Drive, Docs productivity tasks |

Average ~4K input tokens, ~12 messages per prompt, 99/100 contain tool_calls and tool response messages. Regenerate with `scripts/compose_agent_prompts.py`.

## Metrics

- **TTFT** — Time to first token (ms)
- **Throughput** — Tokens per second (per request, decode phase)
- **Aggregate throughput** — Total tokens / wall time across concurrent requests
- **ITL** — Inter-token latency (ms)
- **Latency** — End-to-end request latency (s)

Tested at concurrency levels: 1, 8, 16. Each level runs 100 requests with 3 warmup requests. A 60-second cooldown between frameworks prevents thermal throttling from skewing results.

Sanity checks run after each concurrency level:
- Silent failure detection (servers returning 200 OK with 0 tokens)
- Token count validation (warns if output far below requested max_tokens)
- Throughput/ITL consistency check

If a concurrency level exceeds 40 minutes, remaining levels are auto-skipped (configurable via `--max-wall-time`).

Failures (400 errors, server crashes, connection resets) are reported as-is in the results — they're part of the benchmark. A framework that crashes under load gets that recorded.

## Server-side settings

Each framework runs with minimal tuning. Notable settings:

- **llama.cpp**: `--parallel 4 -ngl 99` (4 concurrent slots, all layers on GPU)
- **vllm-metal**: `VLLM_METAL_USE_PAGED_ATTENTION=1 VLLM_METAL_MEMORY_FRACTION=0.5`
- **omlx**: defaults (no SSD cache)
- **ollama**: `OLLAMA_NUM_PARALLEL=16`
- **inferrs**: `--paged-attention --max-seq-len 4096 --initial-blocks 512`
- **mlx_lm / mistral.rs**: defaults

## Model

[Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) — small enough for fast benchmark runs, available in all required formats:

All frameworks run BF16 (no quantization) for a fair apple-to-apple comparison. At 0.6B parameters, the model is only ~1.2GB — no reason to quantize.

| Format | Source | Used by |
|--------|--------|---------|
| GGUF BF16 | [unsloth/Qwen3-0.6B-GGUF](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) | llama.cpp, mistral.rs, ollama |
| MLX BF16 | [mlx-community/Qwen3-0.6B-bf16](https://huggingface.co/mlx-community/Qwen3-0.6B-bf16) | mlx_lm, omlx |
| Safetensors BF16 | [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) | vllm-metal, inferrs |

## Ports

| Framework | Port |
|-----------|------|
| llama.cpp | 8001 |
| mlx_lm | 8002 |
| mistral.rs | 8003 |
| vllm-metal | 8004 |
| omlx | 8005 |
| ollama | 8006 |
| inferrs | 8007 |

## Scripts

| Script | Purpose |
|--------|---------|
| `install_<fw>.sh` | First-time setup for each framework |
| `update_<fw>.sh` | Pull latest version and rebuild |
| `serve_<fw>.sh` / `stop_<fw>.sh` | Start/stop framework server |
| `download_model.sh` | Download Qwen3-0.6B in all formats |
| `prepare_dataset.py` | Sample chat-split prompts from OpenOrca + CNN/DailyMail |
| `compose_agent_prompts.py` | Compose agent-split prompts from BFCL V3, Hermes, ClawsBench |
| `benchmark.py` | Run benchmark against any OpenAI-compatible endpoint |
| `collect_results.py` | Aggregate per-framework results into comparison JSON |
| `generate_report.py` | Generate markdown report from comparison |
| `install_all.sh` | Install all frameworks + download models |
| `update_all.sh` | Update all frameworks to latest versions |
| `sync_github.sh` | Commit and push results to GitHub |
| `run_all.sh` | Full pipeline: serve → benchmark → stop → next framework |
| `env_check.sh` | Verify all prerequisites and framework installs |

## Weekly updates

```bash
scripts/update_all.sh
scripts/run_all.sh
scripts/sync_github.sh
```

## Requirements

- macOS 15.0+ on Apple Silicon (M1/M2/M3/M4)
- [uv](https://docs.astral.sh/uv/) (Python env management)
- [Rust toolchain](https://rustup.rs/) (for mistral.rs)
- [Homebrew](https://brew.sh/) + cmake (for llama.cpp, ollama, inferrs)
