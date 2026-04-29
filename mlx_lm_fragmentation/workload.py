#!/usr/bin/env python3
"""Issue 3 prompts to mlx_lm.server in sequential or concurrent mode.

Records per-request t_submit / t_done so the plot can annotate request
boundaries. Wrapped by `metalstat run` to capture the memory timeline.
"""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path

import aiohttp

RESULTS = Path(os.environ.get("FRAGMENTATION_RESULTS_DIR", Path(__file__).parent / "results"))


async def fire(session, base_url, model, prompt, max_tokens):
    """Submit request, record TTFT (first 'data:' SSE line — keepalive comments
    starting with ':' are skipped) and t_done. Returns t_first_token=None /
    error string if the server died mid-request."""
    t_submit = time.perf_counter()
    error = None
    t_first_token = None
    try:
        async with session.post(
            f"{base_url}/v1/completions",
            json={"model": model, "prompt": prompt, "max_tokens": max_tokens, "stream": True},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.content:
                if t_first_token is None and line.startswith(b"data: ") and line.strip() != b"data: [DONE]":
                    t_first_token = time.perf_counter()
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    return {"t_submit": t_submit, "t_first_token": t_first_token,
            "t_done": time.perf_counter(), "error": error}


async def run(mode, base_url, model, max_tokens):
    prompts = json.loads((RESULTS / "prompts.json").read_text())
    timeout = aiohttp.ClientTimeout(total=900)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async def go(p):
            r = await fire(session, base_url, model, p["text"], max_tokens)
            if r["error"]:
                print(f"  FAIL {p['name']:8s}  {r['error']}")
            elif r["t_first_token"] is None:
                print(f"  NOTOK {p['name']:8s}  no first token (server closed stream)")
            else:
                print(f"  done {p['name']:8s}  ttft={r['t_first_token']-r['t_submit']:.2f}s  total={r['t_done']-r['t_submit']:.2f}s")
            return {"name": p["name"], **r}

        t0 = time.perf_counter()
        if mode == "sequential":
            results = [await go(p) for p in prompts]
        else:
            results = await asyncio.gather(*(go(p) for p in prompts), return_exceptions=False)
        wall = time.perf_counter() - t0

    (RESULTS / f"{mode}_workload.json").write_text(
        json.dumps({"mode": mode, "max_tokens": max_tokens, "wall_time": wall,
                    "wall_t0": t0, "results": results}, indent=2)
    )
    print(f"Wall time: {wall:.2f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["sequential", "concurrent"], required=True)
    ap.add_argument("--base-url", default="http://localhost:8002")
    ap.add_argument("--model", required=True)
    ap.add_argument("--max-tokens", type=int, default=256)
    args = ap.parse_args()
    asyncio.run(run(args.mode, args.base_url, args.model, args.max_tokens))
