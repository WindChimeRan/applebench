# AppleBench

Benchmarks 8 local LLM inference frameworks on Apple Silicon side-by-side, re-run weekly by a Claude Code agent so the numbers don't rot. Measures throughput, TTFT, ITL, and latency under concurrent load on both a classic chat workload and a multi-turn agentic workload composed from popular tool-calling benchmarks.

Run the whole weekly pipeline — update, benchmark, diagnose failures, fix, publish — with one command: **`/weekly-bench`** in Claude Code.

Latest results: **[REPORT.md](results/qwen3-0.6b/REPORT.md)**

## Frameworks

| Framework | Backend | Model Format |
|-----------|---------|-------------|
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | C++ / Metal | GGUF |
| [mlx_lm](https://github.com/ml-explore/mlx-examples) | MLX / Metal | MLX BF16 |
| [mistral.rs](https://github.com/EricLBuehler/mistral.rs) | Rust / Metal | GGUF |
| [vllm-metal](https://github.com/vllm-project/vllm-metal) | Python / MLX | Safetensors |
| [vllm-mlx](https://github.com/waybarrios/vllm-mlx) | Python / MLX (vLLM plugin) | MLX BF16 |
| [omlx](https://github.com/jundot/omlx) | MLX / Metal | MLX BF16 |
| [ollama](https://github.com/ollama/ollama) | Go + Metal | GGUF |
| [inferrs](https://github.com/ericcurtin/inferrs) | Rust + Candle / Metal | Safetensors |

All frameworks serve an OpenAI-compatible API. The benchmark hits `/v1/chat/completions` with streaming enabled and measures from the client side — no special instrumentation per framework.

## Workloads

Two splits, 100 prompts each. Select with `--split chat|agent`.

### Chat split

Single-turn prompts sampled from [Open-Orca/OpenOrca](https://huggingface.co/datasets/Open-Orca/OpenOrca) and [CNN/DailyMail](https://huggingface.co/datasets/abisee/cnn_dailymail), distributed across four input-length buckets and two output-length targets:

| Bucket | Input tokens | Output tokens | Count |
|--------|-------------|--------------|-------|
| Short | 10–80 | 64 / 256 | 20 |
| Medium | 80–500 | 64 / 256 | 20 |
| Long | 500–2,000 | 64 / 256 | 30 |
| Very long | 2,000–4,000 | 64 / 256 | 30 |

Covers realistic workloads from quick Q&A through long-document processing. All prompts are real natural language (not synthetic tokens), seeded for reproducibility.

### Agent split

Multi-turn agentic prompts with tool calls and tool responses already baked into the conversation history. Tests how frameworks handle realistic agent workloads — long contexts, tool-calling payloads, heterogeneous roles — without needing an actual agent runtime to drive the loop. Composed from three popular agentic benchmarks:

| Source | Count | Content |
|--------|-------|---------|
| [BFCL V3 multi-turn](https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html) | 35 | File system, trading, travel, vehicle control, messaging tools |
| [Hermes Agent Reasoning Traces](https://huggingface.co/datasets/lambda/hermes-agent-reasoning-traces) | 35 | Real multi-turn agent sessions with tool calls + results |
| [ClawsBench](https://clawsbench.benchflow.ai) | 30 | Gmail, Slack, Calendar, Drive, Docs productivity tasks |

Average ~4K input tokens, ~12 messages per prompt, 99/100 contain tool_calls and tool response messages in the conversation history. The model's job is to generate the next assistant turn.

## Model

[Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) in BF16 across three formats. Small enough for fast weekly runs (~1.2 GB), available in every format we need, and runs without quantization for a fair apple-to-apple comparison.

| Format | Source | Used by |
|--------|--------|---------|
| GGUF BF16 | [unsloth/Qwen3-0.6B-GGUF](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) | llama.cpp, mistral.rs, ollama |
| MLX BF16 | [mlx-community/Qwen3-0.6B-bf16](https://huggingface.co/mlx-community/Qwen3-0.6B-bf16) | mlx_lm, omlx, vllm-mlx |
| Safetensors BF16 | [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) | vllm-metal, inferrs |

Other model profiles live in `models/` — notably a larger [Qwen3-30B-A3B](https://huggingface.co/Qwen/Qwen3-30B-A3B) MoE for when you want to measure how frameworks handle a heavier model.

## Metrics

- **TTFT** — time to first token (ms)
- **Throughput** — tokens per second per request, decode phase
- **Aggregate throughput** — total tokens / wall time across concurrent requests
- **ITL** — inter-token latency (ms)
- **Latency** — end-to-end request latency (s)

Tested at concurrency 1, 8, 16. Each level runs 100 requests with 3 warmup. A 60-second cooldown between frameworks keeps thermal throttling from skewing results.

## How it stays fresh

AppleBench is re-run weekly by a Claude Code agent. The agent:

1. **Updates** each framework from upstream (`update_all.sh`)
2. **Runs** the full benchmark across all 8 frameworks (`run_all.sh`, resumable via `--skip-existing`)
3. **Diagnoses** per-framework failures by reading the error, the framework's upstream changelog, and prior journals
4. **Fixes** adapter scripts when it can (a renamed CLI flag, a new required parameter) within a tightly scoped write allowlist — never touching `benchmark.py`, `config.sh`, or framework source
5. **Verifies** each fix in isolation by starting the server and running a few requests before committing
6. **Commits** auto-fixes to a dated `weekly/<date>` branch so the human reviews before anything lands on main
7. **Publishes** a structured journal at `results/<MODEL>/weekly_<date>.journal.md` recording what succeeded, what was fixed, what was skipped, and why

Skipping a framework is a valid outcome — if the agent can't confidently diagnose a failure, it logs the evidence and moves on, rather than over-fixing and masking a real regression. The full skill prompt lives at [`.claude/skills/weekly-bench/SKILL.md`](.claude/skills/weekly-bench/SKILL.md) if you're curious how it's instructed.

Invoke it with `/weekly-bench` from Claude Code in this repo. Or for the happy-path-only wrapper (no intelligence layer), just run `scripts/weekly_bench.sh`.

## Requirements

macOS 15+ on Apple Silicon. Developer setup, script layout, known framework quirks, and extension guides live in [CLAUDE.md](CLAUDE.md).
