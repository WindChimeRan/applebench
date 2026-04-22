---
name: weekly-bench
description: Run the weekly AppleBench pipeline unattended — update frameworks, benchmark all 9, diagnose and fix per-framework failures, commit fixes as separate commits, sync results. Use this when the user says "run the weekly benchmark" or similar.
---

# Weekly Bench Orchestrator

You are orchestrating AppleBench's weekly benchmark run. Your job is to execute the full pipeline (`update_all.sh` → `run_all.sh` for each split → `sync_github.sh`) unattended, recover from per-framework failures with targeted fixes when you can, and produce a structured journal so the user can review what happened on Monday morning.

This skill is for this repo only. It assumes `caffeinate`, bash, and all the scripts in `scripts/` exist.

## Splits

The benchmark runs over **two prompt splits** by default: `chat` (single-turn) and `agent` (multi-turn, ~4K input tokens, prefill-heavy). Each split lives in its own results subdirectory and produces its own `comparison.json` + `REPORT.md`:

```
results/<MODEL>/
├── chat/{<fw>_<ts>.json, comparison.json, REPORT.md}
├── agent/{<fw>_<ts>.json, comparison.json, REPORT.md}
├── weekly_<DATE>.log
└── weekly_<DATE>.journal.md
```

Treat the unit of success as the **(framework, split) cell**, not the framework. A framework can pass chat and fail agent — both must be tracked independently.

## Goal

Finish the weekly run with as many (framework, split) cells benchmarked as possible, leaving behind:
1. Updated `results/<MODEL>/<split>/comparison.json` and `REPORT.md` for each split
2. A structured journal at `results/<MODEL>/weekly_<YYYY-MM-DD>.journal.md`
3. Any auto-fix commits pushed to a `weekly/<YYYY-MM-DD>` branch (never main directly)

It is **not** your job to heroically fix every failure. A clear failure report is more valuable than a silent over-fix that hides a real regression.

## Phases

### Phase 0 — Set up

1. Determine today's date: `DATE=$(date +%Y-%m-%d)`
2. Read the model name from `scripts/config.sh` (or let the user specify). Default: whatever `APPLEBENCH_MODEL` resolves to.
3. `RESULTS_DIR=results/<MODEL_NAME>`
4. `JOURNAL=$RESULTS_DIR/weekly_$DATE.journal.md`
5. Check for prior journals in `$RESULTS_DIR/weekly_*.journal.md`. Read the most recent 1-2 to learn:
   - Which frameworks were skipped and why (don't re-fight the same battles)
   - What auto-fixes were applied previously (you may need to re-apply or roll forward)
6. Create a fresh `weekly/<DATE>` git branch. All auto-fix commits land here, not on main.
7. Initialize the journal with a preamble (see Journal Format below).

### Phase 1 — Kick off the happy path in background

Run `scripts/weekly_bench.sh` as a background process:

```bash
bash scripts/weekly_bench.sh 2>&1
```

Use `run_in_background: true`. Capture the bash job ID. Then use the `Monitor` tool to stream output. The wrapper runs **two full passes** of `run_all.sh` — one per split (chat, then agent) — so expect ~18 framework cycles total (9 frameworks × 2 splits) before `Weekly run finished`.

While monitoring, watch for these patterns:
- `"run_all.sh --split chat"` / `"run_all.sh --split agent"` — split boundary
- `" Benchmarking: <name>"` — a framework run is starting
- `" AppleBench complete!"` — one split finished cleanly
- Framework-level errors (non-zero exits from serve/benchmark — `run_all.sh` uses `|| true` per framework, so it will continue past failures)
- `"Weekly run finished"` — wrapper finished

**Do not intervene on normal failures** — let `run_all.sh` pass through all frameworks once, even if some fail. Recovery happens in Phase 2.

**Track the active split** so you know which subdirectory the current framework's results land in (`results/<MODEL>/chat/` vs `results/<MODEL>/agent/`).

**But do detect hangs.** Per-framework wall-time budget depends on the split:
- **chat split**: a single framework should complete in ~20-40 minutes. Hang threshold: 45 minutes for the same framework, or 30 minutes of unchanged log.
- **agent split**: prompts are ~4K input tokens — both prefill and decode are slower, and KV cache pressure at concurrency 16 is much higher. Allow up to ~60-90 minutes per framework before declaring a hang. Hang threshold: 90 minutes for the same framework, or 45 minutes of unchanged log.

Use `ScheduleWakeup` to check the log every 30 minutes. On each check, tail the log and compare to the previous check:
- If a new framework has started or completed → progress is normal, continue waiting.
- If the log is unchanged past the threshold for the active split → it is hung. Kill the `benchmark.py` process for that framework (`kill <PID>`), which will unblock `run_all.sh` to continue. Do **not** kill the orchestrator (`run_all.sh` / `weekly_bench.sh`).
- If the whole run has been silent for >20 minutes with no output, tail the log file (`results/<MODEL>/weekly_<DATE>.log`) via Read to check state. If truly hung (no process activity), fall back to Phase 3 (post-mortem).

### Phase 2 — Identify failures

When Phase 1 finishes, inventory what succeeded and what didn't, **per (framework, split)**:

```bash
# A (framework, split) cell succeeded if a result file from the last 24h exists
# in results/<MODEL>/<split>/
for split in chat agent; do
    for fw in llamacpp mlx_lm mistralrs vllm_metal vllm_mlx omlx ollama inferrs hf_transformers; do
        recent=$(find "results/<MODEL>/$split" -maxdepth 1 -name "${fw}_*.json" -mtime -1 2>/dev/null | head -1)
        if [ -n "$recent" ]; then
            echo "ok      $split $fw $(basename $recent)"
        else
            echo "FAILED  $split $fw"
        fi
    done
done
```

For each of the 9 frameworks × 2 splits = 18 cells, classify:
- **ok** — has a result file from the last 24h in the split's subdirectory
- **failed** — no recent result file in that split's subdirectory

A framework can be `ok` in chat and `failed` in agent (or vice versa). Treat these as independent diagnoses — the agent split's larger context (~4K input tokens) exposes failure modes (KV cache OOM, prompt-length limits, tokenizer bugs on multi-turn payloads) that chat doesn't.

For each failed cell, gather evidence before deciding:

```bash
# 1. The framework's serve log (if the serve script captures it)
find . -name "*<fw>*.log" -mtime -1

# 2. The weekly log tail
tail -200 results/<MODEL>/weekly_<DATE>.log

# 3. Upstream changelog since the last successful run
cd .frameworks/<fw>
git log --oneline -30
git diff HEAD~10..HEAD -- CHANGELOG.md RELEASE_NOTES.md 2>/dev/null

# 4. What local script changes were made since the last successful run
git log --oneline scripts/*<fw>*.sh

# 5. Prior journal notes (already loaded in Phase 0)

# 6. Jetsam kills (macOS memory-pressure terminations). A jetsam'd process
#    looks identical to a plain crash in our logs, but the fix is different:
#    it's OOM, not a bug. Correlate any hits below by timestamp with when
#    this framework ran. Process names to grep for: python (mlx_lm, omlx,
#    vllm_metal, vllm_mlx, hf_transformers), llama-server (llamacpp),
#    ollama, mistralrs, inferrs.
log show --last 24h --predicate 'eventMessage CONTAINS "jetsam"' 2>/dev/null | head -50

# 7. Metalstat sidecar artifacts for this (framework, split) cell, if the run had
#    APPLEBENCH_METALSTAT=1 (default for weekly_bench.sh). Paths:
#      results/<MODEL>/<split>/<fw>_<ts>_metalstat.jsonl   (per-second metrics)
#      results/<MODEL>/<split>/<fw>_<ts>_metalstat.meta.json
#    Read the jsonl to inspect gpu_util, gpu_freq_mhz, mem_used_gb, mem_pressure_level,
#    gpu_mem_allocated_gb, gpu_w. Useful for distinguishing "server crashed mid-benchmark"
#    (util drops to 0) vs "throttled hard" (freq drops, util stays high) vs "OOM-adjacent"
#    (mem_pressure_level=warn/critical, compressed grows). Complements step 6: jetsam
#    tells you the kernel killed the process; metalstat shows the pressure trajectory
#    that led up to it.
```

### Phase 3 — Diagnose and decide (per failed framework)

This is the judgment phase. You have the error, the upstream history, and the local script history. Decide one of three actions.

**OOM pre-check.** Before applying (A)/(B)/(C), re-read Phase 2 step 6. If the jetsam log shows a kill for this framework's process during its run window, short-circuit: classify the cell as **oom** in the journal (a distinct status, not `skipped`). The framework code is probably fine; the machine just did not have RAM for (model × concurrency × prompt length). Auto-fixing a jetsam'd cell would chase a ghost regression. Do not retry, do not edit scripts, and record the jetsam log line plus timestamps in the OOM Cells section of the journal.

#### (A) Auto-fix — you're confident about the root cause and the fix

Apply only when **all** of these are true:
- You can point at a specific upstream commit, changelog entry, or diff that explains the failure
- The fix is local to an adapter script (not changing benchmark logic)
- You can verify the fix works in isolation (see Phase 4)

**Scope of writes** — you may freely edit:
- `scripts/serve_<fw>.sh`
- `scripts/install_<fw>.sh`
- `scripts/update_<fw>.sh`
- `scripts/stop_<fw>.sh`
- `models/<profile>.sh`

**Do not edit**:
- `scripts/benchmark.py`, `scripts/collect_results.py`, `scripts/generate_report.py` (framework-agnostic, load-bearing)
- `scripts/config.sh` (shared config, high blast radius)
- `scripts/run_all.sh`, `scripts/weekly_bench.sh` (orchestration)
- Anything inside `.frameworks/` (upstream source trees)
- `prompts/` (dataset — unrelated to framework fixes)

If a fix would require editing one of the forbidden files, escalate — go to (C).

#### (B) Retry — you believe it's transient

Apply when:
- The error looks transient (network, OOM, port collision, thermal)
- You have no reason to believe a second attempt will fail the same way

Do not retry more than once. If the retry fails, fall through to (C).

#### (C) Skip — you're unsure, or the fix is out of scope

Apply when:
- The error is unfamiliar and you can't confidently diagnose
- The root cause is in the framework itself (not the adapter)
- The fix would require editing a forbidden file
- This framework was also skipped last week for the same reason (don't loop)
- You see "suspicious success" — the server ran but produced tokens/sec 10x off from last week (log prominently, don't fix, continue)

Skipping is a valid outcome. It's not failure — it's a clear signal for the user to triage.

### Phase 4 — Verify the fix (for Action A only)

Before re-running the full benchmark, verify in isolation. **Use the same split that failed** — a chat-only verify will not catch agent-specific regressions (longer context, multi-turn payloads).

```bash
# 1. Start the server manually
bash scripts/serve_<fw>.sh

# 2. Wait for readiness, then hit /v1/models
sleep 10
curl -s http://localhost:<port>/v1/models

# 3. Run a handful of quick requests via benchmark.py against the failing split.
# (use --requests 3 --concurrency 1 --warmup 0 to make it fast)
source .venvs/bench/bin/activate
python scripts/benchmark.py --framework <fw> --port <port> \
    --requests 3 --concurrency 1 --warmup 0 \
    --results-dir /tmp/fix_verify_$$ --split <chat|agent> || echo "verify failed"

# 4. Stop the server
bash scripts/stop_<fw>.sh

# 5. Clean up the verify results directory
rm -rf /tmp/fix_verify_$$
```

If the fix is supposed to repair both splits (e.g., a server-side flag change), verify both — run step 3 twice, once with `--split chat` and once with `--split agent`.

If verification fails:
- Revert the fix: `git checkout -- <files>`
- Fall through to Action (C), skip.

If verification succeeds:
- Commit the fix: `git add <files> && git commit -m "auto-fix(<fw>, <split>): <what changed> <why>"` — clear, specific messages. Mention which split(s) the fix is verified against. Reference the upstream commit or changelog entry if you have one.
- Continue to Phase 5.

### Phase 5 — Retry the failed/fixed cells

For each (framework, split) cell that (a) had a fix applied and verified, or (b) is being retried once for transient reasons, relaunch `run_all.sh` **targeted at one split**, listing only the frameworks that need to retry on that split:

```bash
# Retry chat-only failures
bash scripts/run_all.sh --split chat --skip-existing <fw1> <fw2> ...

# Retry agent-only failures (separate invocation)
bash scripts/run_all.sh --split agent --skip-existing <fw3> <fw4> ...
```

The `--skip-existing` flag ensures successful cells from Phase 1 (within that split's subdirectory) are preserved. Note that `--skip-existing` is per-split — it looks at `results/<MODEL>/<split>/`, so a chat retry will not touch agent results and vice versa.

After this retry pass, re-inventory all 18 cells. Update the journal with final status.

### Phase 6 — Finalize

1. Regenerate `comparison.json` and `REPORT.md` **per split** (the final `run_all.sh` call already does this for any split it ran, but re-run for any split you retried anything in):
   ```bash
   source .venvs/bench/bin/activate
   for split in chat agent; do
       if [ -d "$RESULTS_DIR/$split" ] && ls "$RESULTS_DIR/$split"/*_*.json &>/dev/null; then
           python scripts/collect_results.py --results-dir "$RESULTS_DIR/$split"
           python scripts/generate_report.py --results-dir "$RESULTS_DIR/$split"
       fi
   done
   ```

2. Write the final journal (see format below). One journal covers both splits.

3. Commit + push:
   - `git add $RESULTS_DIR && git commit -m "results: weekly run <DATE> (chat + agent)"` on the `weekly/<DATE>` branch (omit the part in parens if you only ran one split)
   - `git push -u origin weekly/<DATE>`
   - Do **not** merge to main automatically. The user reviews the branch.

4. Summary to user: how many cells ok / fixed / skipped per split, where the two REPORT.md files live, where the journal lives, what they should review.

## Journal Format

Write to `$RESULTS_DIR/weekly_<DATE>.journal.md` (one journal at the model level — covers both splits). Structure:

```markdown
# Weekly Bench Run — <DATE>

## Summary
- Started: <ISO timestamp>
- Finished: <ISO timestamp>
- Model: <MODEL_NAME>
- Splits run: <chat, agent | chat | agent>
- Status: <completed|completed_with_fixes|completed_with_skips|completed_with_oom|partial>
- Branch: weekly/<DATE>
- Reports: results/<MODEL>/chat/REPORT.md, results/<MODEL>/agent/REPORT.md

Cell status values: `ok` (benchmarked), `fixed` (auto-fix applied and verified), `skipped` (diagnosed but not fixed), `oom` (macOS jetsam killed the serving process during the run; distinct from `skipped` because the framework code is likely fine).

## Frameworks — chat split
| Framework | Status | Notes |
|-----------|--------|-------|
| llamacpp | ok | — |
| mlx_lm | ok | — |
| mistralrs | fixed | <short note, commit SHA> |
| vllm_metal | skipped | <short reason> |
| vllm_mlx | ok | — |
| omlx | ok | — |
| ollama | ok | — |
| inferrs | ok | — |
| hf_transformers | ok | — |

## Frameworks — agent split
| Framework | Status | Notes |
|-----------|--------|-------|
| llamacpp | ok | — |
| mlx_lm | ok | — |
| mistralrs | oom | jetsam killed mistralrs at 02:14 during agent concurrency 16 |
| vllm_metal | ok | — |
| vllm_mlx | ok | — |
| omlx | ok | — |
| ollama | ok | — |
| inferrs | skipped | needs --paged-attention for 4K prompts |
| hf_transformers | ok | — |

## Fixes Applied

### <framework> (<split>)
- **Error**: <first ~5 lines of error>
- **Diagnosis**: <your reasoning, 1-3 sentences>
- **Reference**: <upstream commit URL, changelog link, or "none found">
- **Fix**: <file path + brief description>
- **Verification**: <what tests passed, which split(s)>
- **Commit**: <SHA and message>

## Skipped Cells

### <framework> (<split>)
- **Error**: <first ~5 lines of error>
- **Why skipped**: <your reasoning>
- **Prior occurrences**: <if this also happened in previous weeks, in the same split>
- **Relevant logs**: <file paths + key excerpts>

## OOM Cells

(Cells where macOS jetsam terminated the serving process. Not auto-fixed. The framework code is likely fine; the machine ran out of memory. Mitigation usually means reducing concurrency, picking a smaller model, or upgrading the host.)

### <framework> (<split>)
- **Jetsam line**: <raw `log show` line with process name, pid, and timestamp>
- **Run window**: <when the framework started vs. when it died>
- **Likely cause**: <one-sentence hypothesis, e.g. weights + KV cache at concurrency 16 exceeded free RAM>
- **Prior OOMs**: <if this cell OOM'd in previous weeks>

## Suspicious Successes

(Cells that ran but produced unusual numbers — flag for human review. Always compare chat-to-chat and agent-to-agent only — never cross-compare splits.)

### <framework> (<split>)
- **Observation**: <metric>: this week <N>, last week <M> (<X>x change)
- **Note**: Not auto-fixed. Please review.

## Timeline
- HH:MM:SS — <event>
- HH:MM:SS — <event>
...
```

Keep the journal terse. It's a log for the user (and future Claude), not an essay.

## Principles

- **Finish the run, even if imperfect.** Don't let one broken cell block the others. A chat failure does not stop agent from running, and vice versa.
- **One fix attempt per (framework, split) cell per run.** No loops.
- **The unit of success is the cell, not the framework.** Track and report each (framework, split) independently — chat success doesn't excuse agent failure.
- **Never modify forbidden files** even if it would fix the issue. Escalate instead.
- **Branch, don't push to main.** All auto-fix commits land on `weekly/<DATE>` for user review.
- **Log everything.** If it's not in the journal, it didn't happen.
- **Suspicious success ≠ success.** Tokens/sec 10x off from last week is a signal, not a fix target. Compare chat-to-chat and agent-to-agent only — never cross-compare splits, since prefill-heavy agent prompts produce systematically different numbers. When metalstat sidecar data is present, cross-check: GPU-util at 100% with throughput down suggests a real regression; GPU-util near-idle suggests a serving-side bug (batching broken, client-side bottleneck, etc.); GPU freq dropping mid-run suggests thermal throttling.
- **Prior skips matter.** If a (framework, split) cell was skipped last week for reason Y and reason Y still holds, skip again silently (one line in the journal). Don't re-diagnose from scratch.

## When to bail out completely

Stop the whole workflow and surface a clear message to the user if:
- You cannot create the `weekly/<DATE>` branch (uncommitted changes on main, etc.)
- The bench venv is broken and `install_bench.sh` fails
- `caffeinate` is not available (running on non-macOS)
- `weekly_bench.sh` fails to start at all (script permissions, missing file, etc.)
- All 9 frameworks fail in Phase 1 (something systemic is wrong — maybe the model download, maybe a shared dep)

In these cases, the right answer is to stop and tell the user what's wrong, not to keep trying.
