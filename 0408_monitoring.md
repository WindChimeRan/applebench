# AppleBench Monitoring Log — 2026-04-08

## Benchmark: Qwen3-0.6B (all 7 frameworks)

### Run Started
- **Time:** 2026-04-08 21:57 PDT
- **Command:** `scripts/run_all.sh --model qwen3-0.6b`
- **Frameworks:** llamacpp, mlx_lm, mistralrs, vllm_metal, omlx, ollama, inferrs
- **Concurrency levels:** 1, 8, 16

---

### Monitoring Log

#### 21:57 — Run started
- Env checks passed (1 warning, non-blocking)
- All models present (GGUF, MLX, HF)
- Benchmark PID: 21684
- llamacpp server started successfully (PID 21745), waiting for readiness

#### 22:28 — Check #1 (30 min)
- **Status:** Still running (PID 21684), currently on ollama c=16
- **Completed:** llamacpp, mlx_lm, mistralrs, vllm_metal, omlx (5/7)
- **Results so far:**

| Framework | c=1 ok/fail | c=8 ok/fail | c=16 ok/fail | Status |
|-----------|------------|------------|-------------|--------|
| llamacpp | 0/100 | 0/100 | 0/100 | BUG: 503 all requests |
| mlx_lm | 19/81 | 22/78 | 19/81 | BUG: silent failures |
| mistralrs | 100/0 | 53/47 | 0/100 | Known: crashes at high concurrency |
| vllm_metal | 100/0 | 100/0 | 100/0 | CLEAN |
| omlx | 100/0 | 100/0 | 100/0 | CLEAN |
| ollama | running... | - | - | - |
| inferrs | pending | - | - | - |

**BUG #1: llamacpp 100% failure (503 Service Unavailable)**
- Root cause: Server responded to `/v1/models` health check before model/KV cache fully loaded. New llama.cpp version starts HTTP listener early while still allocating KV cache for 40960-token context.
- Fix applied: Changed `serve_llamacpp.sh` readiness check from `/v1/models` to `/health` endpoint (which only returns OK after model is fully loaded). Also increased timeout from 60s to 120s.

**BUG #2: mlx_lm ~80% silent failures (0 tokens generated)**
- 81/100 requests return HTTP 200 but generate 0 tokens
- Not correlated with max_tokens (both 64 and 256 prompts fail)
- omlx (same MLX model) has 0 failures - so it's mlx_lm-specific, not model-specific
- Needs investigation: likely SSE streaming format issue with latest mlx_lm. Will debug after current run completes.

**Plan:** Let current run finish (ollama + inferrs remain). Then re-run llamacpp and mlx_lm with fixes.

**BUG #2 ROOT CAUSE FOUND: mlx_lm uses `delta.reasoning` key (not `delta.reasoning_content`)**
- mlx_lm sends Qwen3 thinking tokens as `delta.reasoning` in SSE chunks
- Our benchmark only checked `delta.content` and `delta.reasoning_content` — missed `delta.reasoning`
- So ALL thinking tokens were invisible to the benchmark. If the model spent all max_tokens on thinking, 0 tokens were counted = silent failure
- 19 requests succeeded because those prompts had short/no thinking and generated actual `content` tokens
- Fix applied: Added `delta.get("reasoning", "")` to benchmark.py token counting (line 72)

#### 22:58 — Check #2 (60 min)
- **Status:** Still running (PID 21684), currently on inferrs c=1
- **Completed:** llamacpp, mlx_lm, mistralrs, vllm_metal, omlx, ollama (6/7)
- **ollama results:** 100/0 at all concurrency levels - CLEAN
  - c=1: 1164.0 agg tok/s, 816.7ms TTFT
  - c=8: 185.6 agg tok/s, 2315.9ms TTFT
  - c=16: 98.2 agg tok/s, 4088.1ms TTFT
  - Note: ollama is slow at high concurrency (1.8 tok/s per-request at c=16), but no failures
- **inferrs:** Started, benchmark running at c=1. Expect this to be slow (~40min per concurrency level based on prior runs)

#### 00:11 — Check #3 (2h 13m elapsed)
- **Status:** Still running (PID 21684), inferrs c=8 in progress
- **inferrs c=1 completed:** 96/4 (ok/fail), 1830s wall time (under 2400s limit)
  - 4.7 tok/s per-request, 65.7 agg tok/s, 991.9ms TTFT
  - 4 silent failures (0 tokens for some prompts)
- inferrs c=8 now running — may take 30-40min. If wall time exceeds 2400s, c=16 will be auto-skipped
- No new fixes needed. Waiting for inferrs to finish, then will re-run llamacpp + debug mlx_lm

#### 00:42 — Check #4 (initial run COMPLETE, re-runs started)
- **Initial run finished** at 00:37 (total ~2h 40m)
- **inferrs final results:**
  - c=1: 96/4 (ok/fail), 65.7 agg tok/s, 1830s wall
  - c=8: 52/48, 9.5 agg tok/s, 2010s wall
  - c=16: 42/58, 5.1 agg tok/s, 822s wall
- **Re-runs started:**
  - llamacpp: benchmark running with fixed server (health check fix confirmed working)
  - mlx_lm: BUG #2 root cause identified and fixed in benchmark.py — `delta.reasoning` key
- **Fixes applied this session:**
  1. `serve_llamacpp.sh`: `/v1/models` -> `/health` readiness check + 120s timeout
  2. `benchmark.py`: Added `delta.get("reasoning", "")` to token counting

#### 00:45 — llamacpp re-run COMPLETE, mlx_lm re-run started
- **llamacpp re-run: PERFECT** - 100% success at all concurrency levels
  - c=1: 5843.2 agg tok/s, 179.7ms TTFT, 164.1 tok/s per-request
  - c=8: 2375.4 agg tok/s, 1893.3ms TTFT, 99.7 tok/s per-request
  - c=16: 1443.6 agg tok/s, 5064.2ms TTFT, 98.3 tok/s per-request
  - Health check fix confirmed working
- **mlx_lm re-run:** Started with `--model` flag set to correct path + fixed benchmark.py

#### 00:51 — mlx_lm re-run COMPLETE, report regenerated
- **mlx_lm re-run: PERFECT** - 100% success at all concurrency levels
  - c=1: 5745.5 agg tok/s, 296.2ms TTFT, 183.1 tok/s per-request
  - c=8: 1159.9 agg tok/s, 1322.0ms TTFT, 32.0 tok/s per-request
  - c=16: 630.9 agg tok/s, 2563.0ms TTFT, 19.2 tok/s per-request
  - `delta.reasoning` fix confirmed working
- **Report regenerated** with all 7 frameworks having valid data
- **All re-runs complete.** Qwen3-0.6B benchmark is DONE.

### Final Results Summary (Qwen3-0.6B, c=1 aggregate throughput)

| Rank | Framework | Agg tok/s | Status |
|------|-----------|-----------|--------|
| 1 | omlx | 7886.3 | CLEAN |
| 2 | llamacpp | 5843.2 | CLEAN (re-run) |
| 3 | mlx_lm | 5745.5 | CLEAN (re-run) |
| 4 | mistralrs | 2219.8 | crashes at c=16 |
| 5 | vllm_metal | 1325.4 | CLEAN |
| 6 | ollama | 1164.0 | CLEAN |
| 7 | inferrs | 65.7 | 4 failures, very slow |

### Fixes Applied

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `scripts/serve_llamacpp.sh` | Readiness check passed before model loaded (503s) | Changed `/v1/models` to `/health` endpoint, increased timeout to 120s |
| 2 | `scripts/benchmark.py` | mlx_lm thinking tokens not counted (uses `delta.reasoning`) | Added `delta.get("reasoning", "")` to token counting |

