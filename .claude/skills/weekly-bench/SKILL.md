---
name: weekly-bench
description: Run the weekly AppleBench pipeline unattended — update frameworks, benchmark all 7, diagnose and fix per-framework failures, commit fixes as separate commits, sync results. Use this when the user says "run the weekly benchmark" or similar.
---

# Weekly Bench Orchestrator

You are orchestrating AppleBench's weekly benchmark run. Your job is to execute the full pipeline (`update_all.sh` → `run_all.sh` → `sync_github.sh`) unattended, recover from per-framework failures with targeted fixes when you can, and produce a structured journal so the user can review what happened on Monday morning.

This skill is for this repo only. It assumes `caffeinate`, bash, and all the scripts in `scripts/` exist.

## Goal

Finish the weekly run with as many frameworks benchmarked as possible, leaving behind:
1. Updated `results/<MODEL>/comparison.json` and `REPORT.md`
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

Use `run_in_background: true`. Capture the bash job ID. Then use the `Monitor` tool to stream output.

While monitoring, watch for these patterns:
- `" Benchmarking: <name>"` — a framework run is starting
- `" AppleBench complete!"` — the whole run finished cleanly
- Framework-level errors (non-zero exits from serve/benchmark — `run_all.sh` uses `|| true` per framework, so it will continue past failures)
- `"Weekly run finished"` — wrapper finished

**Do not intervene mid-run.** Let `run_all.sh` pass through all frameworks once, even if some fail. Recovery happens in Phase 2.

If the whole run has been silent for >20 minutes with no output, tail the log file (`results/<MODEL>/weekly_<DATE>.log`) via Read to check state. If truly hung (no process activity), fall back to Phase 3 (post-mortem).

### Phase 2 — Identify failures

When Phase 1 finishes, inventory what succeeded and what didn't:

```bash
# Frameworks with a result file from the last 24h = succeeded
ls -la results/<MODEL>/<fw>_*.json
find results/<MODEL> -maxdepth 1 -name '<fw>_*.json' -mtime -1
```

For each of the 7 frameworks (`llamacpp`, `mlx_lm`, `mistralrs`, `vllm_metal`, `omlx`, `ollama`, `inferrs`), classify:
- **ok** — has a result file from the last 24h
- **failed** — no recent result file

For each failed framework, gather evidence before deciding:

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
```

### Phase 3 — Diagnose and decide (per failed framework)

This is the judgment phase. You have the error, the upstream history, and the local script history. Decide one of three actions:

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

Before re-running the full benchmark, verify in isolation:

```bash
# 1. Start the server manually
bash scripts/serve_<fw>.sh

# 2. Wait for readiness, then hit /v1/models
sleep 10
curl -s http://localhost:<port>/v1/models

# 3. Run a handful of quick requests via benchmark.py
# (use --requests 3 --concurrency 1 --warmup 0 to make it fast)
source .venvs/bench/bin/activate
python scripts/benchmark.py --framework <fw> --port <port> \
    --requests 3 --concurrency 1 --warmup 0 \
    --results-dir /tmp/fix_verify_$$ --split chat || echo "verify failed"

# 4. Stop the server
bash scripts/stop_<fw>.sh

# 5. Clean up the verify results directory
rm -rf /tmp/fix_verify_$$
```

If verification fails:
- Revert the fix: `git checkout -- <files>`
- Fall through to Action (C), skip.

If verification succeeds:
- Commit the fix: `git add <files> && git commit -m "auto-fix(<fw>): <what changed> <why>"` — clear, specific messages. Reference the upstream commit or changelog entry if you have one.
- Continue to Phase 5.

### Phase 5 — Retry the failed/fixed frameworks

For each framework that (a) had a fix applied and verified, or (b) is being retried once for transient reasons, relaunch `run_all.sh` targeted at just those frameworks:

```bash
bash scripts/run_all.sh --skip-existing <fw1> <fw2> ...
```

The `--skip-existing` flag ensures successful frameworks from Phase 1 are preserved.

After this retry pass, re-inventory. Update the journal with final status.

### Phase 6 — Finalize

1. Regenerate `comparison.json` and `REPORT.md` (the final `run_all.sh` call already does this, but run it again if you retried anything):
   ```bash
   source .venvs/bench/bin/activate
   python scripts/collect_results.py --results-dir $RESULTS_DIR
   python scripts/generate_report.py --results-dir $RESULTS_DIR
   ```

2. Write the final journal (see format below).

3. Commit + push:
   - `git add $RESULTS_DIR && git commit -m "results: weekly run <DATE>"` on the `weekly/<DATE>` branch
   - `git push -u origin weekly/<DATE>`
   - Do **not** merge to main automatically. The user reviews the branch.

4. Summary to user: how many ok / fixed / skipped, where the journal lives, what they should review.

## Journal Format

Write to `$RESULTS_DIR/weekly_<DATE>.journal.md`. Structure:

```markdown
# Weekly Bench Run — <DATE>

## Summary
- Started: <ISO timestamp>
- Finished: <ISO timestamp>
- Model: <MODEL_NAME>
- Split: <chat|agent>
- Status: <completed|completed_with_fixes|completed_with_skips|partial>
- Branch: weekly/<DATE>

## Frameworks
| Framework | Status | Notes |
|-----------|--------|-------|
| llamacpp | ok | — |
| mlx_lm | ok | — |
| mistralrs | fixed | <short note, commit SHA> |
| vllm_metal | skipped | <short reason> |
| omlx | ok | — |
| ollama | ok | — |
| inferrs | ok | — |

## Fixes Applied

### <framework>
- **Error**: <first ~5 lines of error>
- **Diagnosis**: <your reasoning, 1-3 sentences>
- **Reference**: <upstream commit URL, changelog link, or "none found">
- **Fix**: <file path + brief description>
- **Verification**: <what tests passed>
- **Commit**: <SHA and message>

## Skipped Frameworks

### <framework>
- **Error**: <first ~5 lines of error>
- **Why skipped**: <your reasoning>
- **Prior occurrences**: <if this also happened in previous weeks>
- **Relevant logs**: <file paths + key excerpts>

## Suspicious Successes

(Frameworks that ran but produced unusual numbers — flag for human review)

### <framework>
- **Observation**: <metric>: this week <N>, last week <M> (<X>x change)
- **Note**: Not auto-fixed. Please review.

## Timeline
- HH:MM:SS — <event>
- HH:MM:SS — <event>
...
```

Keep the journal terse. It's a log for the user (and future Claude), not an essay.

## Principles

- **Finish the run, even if imperfect.** Don't let one broken framework block the others.
- **One fix attempt per framework per run.** No loops.
- **Never modify forbidden files** even if it would fix the issue. Escalate instead.
- **Branch, don't push to main.** All auto-fix commits land on `weekly/<DATE>` for user review.
- **Log everything.** If it's not in the journal, it didn't happen.
- **Suspicious success ≠ success.** Tokens/sec 10x off from last week is a signal, not a fix target.
- **Prior skips matter.** If framework X was skipped last week for reason Y and reason Y still holds, skip again silently (one line in the journal). Don't re-diagnose from scratch.

## When to bail out completely

Stop the whole workflow and surface a clear message to the user if:
- You cannot create the `weekly/<DATE>` branch (uncommitted changes on main, etc.)
- The bench venv is broken and `install_bench.sh` fails
- `caffeinate` is not available (running on non-macOS)
- `weekly_bench.sh` fails to start at all (script permissions, missing file, etc.)
- All 7 frameworks fail in Phase 1 (something systemic is wrong — maybe the model download, maybe a shared dep)

In these cases, the right answer is to stop and tell the user what's wrong, not to keep trying.
