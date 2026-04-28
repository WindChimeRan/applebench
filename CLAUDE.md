# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

AppleBench benchmarks 10 local LLM inference frameworks on Apple Silicon side-by-side: llama.cpp, mlx_lm, mistral.rs, vllm-metal, vllm-mlx, omlx, ollama, inferrs, hf_transformers, sglang. All frameworks serve an OpenAI-compatible API; the benchmark hits `/v1/chat/completions` with streaming and measures TTFT, throughput, ITL, and latency at concurrency levels 1/8/16.

## Key Commands

```bash
# Full benchmark (one split at a time; default: chat, Qwen3-0.6B)
scripts/run_all.sh

# Agent split (multi-turn, ~4K input tokens, prefill-heavy)
scripts/run_all.sh --split agent

# Resume an interrupted run (skip frameworks with results <24h old, scoped to the split)
scripts/run_all.sh --skip-existing

# Specific model
scripts/run_all.sh --model qwen3-30b-a3b

# Specific frameworks
scripts/run_all.sh llamacpp omlx
scripts/run_all.sh --split agent --model qwen3-30b-a3b llamacpp

# Unattended weekly run — runs BOTH splits (chat then agent) by default,
# wraps update → run (×2) → sync under caffeinate + logging
scripts/weekly_bench.sh
scripts/weekly_bench.sh --split chat                     # constrain to one split
scripts/weekly_bench.sh --skip-update --skip-existing    # resume-only mode

# Install / update everything
scripts/install_all.sh
scripts/update_all.sh

# Download model files for a specific profile
scripts/download_model.sh --model qwen3-30b-a3b

# Manual single-framework test
scripts/serve_llamacpp.sh
scripts/stop_llamacpp.sh
```

## Architecture

**Config chain:** `config.sh` sources a model profile from `models/<name>.sh`, which sets repo URLs and filenames. All other scripts source `config.sh` to get derived paths (`$GGUF_MODEL`, `$MLX_MODEL`, `$HF_MODEL`, `$RESULTS_DIR`). The active model is controlled by `APPLEBENCH_MODEL` env var or `--model` CLI flag (default: `qwen3-0.6b`).

**Per-framework scripts** follow a strict pattern — each framework has exactly 4 scripts:
- `install_<fw>.sh` — first-time setup (clone/brew/venv)
- `serve_<fw>.sh` — start server in background, save PID, poll `/v1/models` for readiness
- `stop_<fw>.sh` — kill by PID with SIGTERM→wait→SIGKILL fallback
- `update_<fw>.sh` — pull latest + rebuild/reinstall

**Benchmark pipeline** (`run_all.sh`): one split per invocation. For each framework → serve → `benchmark.py` → stop → cleanup → cooldown. Results go to `results/<MODEL_NAME>/<split>/<framework>_<timestamp>.json`. Then `collect_results.py` picks the latest per framework (by mtime, scoped to the split's subdir) into `<split>/comparison.json`, and `generate_report.py` renders `<split>/REPORT.md`. `sync_github.sh` commits and pushes the `results/` tree. `--skip-existing` makes the pipeline resumable per-split: frameworks with result files newer than 24h in the active split's subdir are skipped, and old results are preserved rather than deleted at startup.

**Results layout** (per model):
```
results/<MODEL_NAME>/
├── chat/{<fw>_<ts>.json, comparison.json, REPORT.md}
├── agent/{<fw>_<ts>.json, comparison.json, REPORT.md}
├── weekly_<DATE>.log
└── weekly_<DATE>.journal.md
```
`comparison.json` and `REPORT.md` are per-split — there is no model-level aggregate. Weekly logs and journals stay at the model level since a single weekly run covers both splits.

**Weekly workflow:** `scripts/weekly_bench.sh` is the unattended wrapper — it runs `update_all.sh → run_all.sh --split chat → run_all.sh --split agent → sync_github.sh` under `caffeinate -i -m` (prevents Mac sleep) and tees all output to `results/<MODEL>/weekly_<date>.log`. Both splits run by default; pass `--split chat` or `--split agent` to constrain to one. It continues past per-framework failures so a single broken cell doesn't block the rest, and chat failures don't stop agent from running. Intelligent recovery (diagnose failures per `(framework, split)` cell, apply scoped fixes, verify against the matching split, retry with `--skip-existing`) lives in the `.claude/skills/weekly-bench/` skill, invoked as `/weekly-bench`. The skill commits auto-fixes to a `weekly/<date>` branch (never main) and produces a structured journal at `results/<MODEL>/weekly_<date>.journal.md` with separate per-split status tables.

**Benchmark defaults** (in `config.sh`): `CONCURRENCY_LEVELS="1 8 16"`, `BENCHMARK_REQUESTS=100` per level, `WARMUP_REQUESTS=3`, `COOLDOWN_SECONDS=60` between frameworks. Override via `benchmark.py` flags (`--concurrency`, `--requests`, `--warmup`) when running a single framework manually.

**Cache layout** (all gitignored):
- `.frameworks/` — cloned source trees (llama.cpp, mistral.rs, inferrs, etc.)
- `.venvs/` — per-framework Python venvs plus the shared `bench/` venv used by `benchmark.py`, `collect_results.py`, `generate_report.py`. `run_all.sh` auto-creates `bench/` via `install_bench.sh` on first run.
- `.models/` — downloaded model files (GGUF, MLX, Safetensors); shared across frameworks.
- Exception: **vllm-metal** uses `~/.venv-vllm-metal` (global), not `.venvs/`.

**Prompt splits:** Two datasets live in `prompts/`, selected via `--split` (default `chat`):
- `chat_benchmark_prompts.json` — 100 single-turn prompts from OpenOrca + CNN/DailyMail (generated by `prepare_dataset.py`)
- `agent_benchmark_prompts.json` — 100 multi-turn agentic prompts composed from BFCL V3 multi-turn (35), Hermes Agent Reasoning Traces (35), and ClawsBench (30) via `compose_agent_prompts.py`. Tool calls and tool responses are baked into the conversation history, so no agent runtime is needed — the model just generates the next assistant turn. Avg ~4K input tokens, ~12 messages per prompt.

**Model formats:** Three formats are downloaded per model profile. GGUF (llama.cpp, mistral.rs, ollama), MLX (mlx_lm, omlx), Safetensors/HF (vllm-metal, inferrs). All use BF16 for fair comparison.

**Ports:** 8001-8007 in framework order (llamacpp through inferrs). Defined in `config.sh`.

## Adding a New Framework

1. Create `scripts/install_<fw>.sh`, `serve_<fw>.sh`, `stop_<fw>.sh`, `update_<fw>.sh`
2. Add port in `config.sh`
3. Add entry to `FRAMEWORKS` array in `run_all.sh` and `cleanup()` function
4. Add check in `env_check.sh`
5. Add to `install_all.sh` and `update_all.sh` loops

No changes needed to `benchmark.py`, `collect_results.py`, or `generate_report.py` — they are framework-agnostic.

## Adding a New Model

Create `models/<name>.sh` with: `MODEL_NAME`, `GGUF_REPO`, `GGUF_FILE`, `MLX_REPO`, `MLX_DIR_NAME`, `HF_REPO`, `HF_DIR_NAME`. Then `scripts/download_model.sh --model <name>`.

## Benchmark Safeguards

- **Silent failure detection:** requests returning 0-1 tokens raise `RuntimeError` (counted as failures)
- **Sanity checks:** warns if avg tokens/request < 10% of max_tokens, or throughput/ITL are inconsistent
- **Adaptive skip:** if a concurrency level exceeds `--max-wall-time` (default 2400s), remaining levels are auto-skipped
- **Stale result cleanup:** `run_all.sh` deletes old result files in the model's results directory before starting

## Known Framework Quirks

- **inferrs:** Very slow (~4.5 tok/s). `--think-filter` strips Qwen3 thinking tokens by default; `--think-filter=false` is documented but broken. Needs `--paged-attention` and `--initial-blocks 512` for prompts >256 tokens.
- **ollama:** Needs launchctl service stopped before custom-port serve. Model imported via Modelfile pointing to shared GGUF.
- **mistral.rs:** Crashes at concurrency 16. Requires `cargo` for build.
- **vllm-metal:** Uses global venv at `~/.venv-vllm-metal` (not in project `.venvs/`). Update script backs up before reinstalling.
- **omlx:** Multi-model server; uses symlink in `.models/omlx/` pointing to the shared MLX model directory.
