#!/usr/bin/env python3
"""Issue 3 prompts to mlx_lm.server in sequential or concurrent mode.

Records per-request t_submit / t_done so the plot can annotate request
boundaries. Wrapped by `metalstat run` to capture the memory timeline.
"""
import argparse
import asyncio
import json
import time
from pathlib import Path

import aiohttp

RESULTS = Path(__file__).parent / "results"


async def fire(session, base_url, model, prompt, max_tokens):
    t_submit = time.perf_counter()
    async with session.post(
        f"{base_url}/v1/completions",
        json={"model": model, "prompt": prompt, "max_tokens": max_tokens, "stream": False},
    ) as resp:
        resp.raise_for_status()
        await resp.read()
    return {"t_submit": t_submit, "t_done": time.perf_counter()}


async def run(mode, base_url, model, max_tokens):
    prompts = json.loads((RESULTS / "prompts.json").read_text())
    timeout = aiohttp.ClientTimeout(total=900)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async def go(p):
            r = await fire(session, base_url, model, p["text"], max_tokens)
            print(f"  done {p['name']:6s}  elapsed={r['t_done']-r['t_submit']:.2f}s")
            return {"name": p["name"], **r}

        t0 = time.perf_counter()
        if mode == "sequential":
            results = [await go(p) for p in prompts]
        else:
            results = await asyncio.gather(*(go(p) for p in prompts))
        wall = time.perf_counter() - t0

    (RESULTS / f"{mode}_workload.json").write_text(
        json.dumps({"mode": mode, "wall_time": wall, "wall_t0": t0, "results": results}, indent=2)
    )
    print(f"Wall time: {wall:.2f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["sequential", "concurrent"], required=True)
    ap.add_argument("--base-url", default="http://localhost:8002")
    ap.add_argument("--model", required=True)
    ap.add_argument("--max-tokens", type=int, default=16)
    args = ap.parse_args()
    asyncio.run(run(args.mode, args.base_url, args.model, args.max_tokens))
