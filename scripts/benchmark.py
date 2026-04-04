#!/usr/bin/env python3
"""
AppleBench — Benchmark an OpenAI-compatible LLM endpoint.

Measures TTFT, throughput (tok/s), inter-token latency, and total latency
at specified concurrency levels.
"""

import argparse
import asyncio
import json
import time
import sys
from pathlib import Path
from dataclasses import dataclass, asdict

import aiohttp


@dataclass
class RequestResult:
    prompt_name: str
    ttft: float          # seconds
    total_time: float    # seconds
    tokens_generated: int
    throughput: float    # tokens/sec (decode only, excludes TTFT)
    inter_token_latency: float  # average ms between tokens


async def benchmark_single(
    session: aiohttp.ClientSession,
    base_url: str,
    model: str,
    prompt: dict,
    max_tokens: int,
) -> RequestResult:
    """Send a single streaming request and measure timing."""

    payload = {
        "model": model,
        "messages": prompt["messages"],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": True,
    }

    t_start = time.perf_counter()
    t_first_token = None
    token_times = []
    tokens_generated = 0

    async with session.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
    ) as resp:
        resp.raise_for_status()
        async for line in resp.content:
            decoded = line.decode("utf-8").strip()
            if not decoded.startswith("data: "):
                continue
            data_str = decoded[6:]
            if data_str == "[DONE]":
                break
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            choices = data.get("choices", [])
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            content = delta.get("content", "") or delta.get("reasoning_content", "")
            if content:
                now = time.perf_counter()
                if t_first_token is None:
                    t_first_token = now
                token_times.append(now)
                tokens_generated += 1

    t_end = time.perf_counter()

    if t_first_token is None:
        t_first_token = t_end

    ttft = t_first_token - t_start
    total_time = t_end - t_start

    # Decode throughput: tokens after first / time after first
    decode_time = t_end - t_first_token if t_first_token else total_time
    throughput = (tokens_generated - 1) / decode_time if decode_time > 0 and tokens_generated > 1 else 0.0

    # Inter-token latency
    if len(token_times) > 1:
        intervals = [token_times[i+1] - token_times[i] for i in range(len(token_times)-1)]
        itl = sum(intervals) / len(intervals) * 1000  # ms
    else:
        itl = 0.0

    return RequestResult(
        prompt_name=prompt["name"],
        ttft=ttft,
        total_time=total_time,
        tokens_generated=tokens_generated,
        throughput=throughput,
        inter_token_latency=itl,
    )


async def run_concurrent(
    base_url: str,
    model: str,
    prompts: list,
    concurrency: int,
    num_requests: int,
    warmup: int,
) -> list[RequestResult]:
    """Run benchmark at a given concurrency level."""

    timeout = aiohttp.ClientTimeout(total=300)
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        # Warmup
        if warmup > 0:
            print(f"  Warming up ({warmup} requests)...")
            for i in range(warmup):
                prompt = prompts[i % len(prompts)]
                try:
                    await benchmark_single(session, base_url, model, prompt, prompt["max_tokens"])
                except Exception as e:
                    print(f"  Warmup error: {e}")

        # Benchmark
        print(f"  Running {num_requests} requests at concurrency {concurrency}...")
        t_wall_start = time.perf_counter()
        sem = asyncio.Semaphore(concurrency)
        results = []

        async def bounded_request(prompt):
            async with sem:
                return await benchmark_single(session, base_url, model, prompt, prompt["max_tokens"])

        tasks = []
        for i in range(num_requests):
            prompt = prompts[i % len(prompts)]
            tasks.append(bounded_request(prompt))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        wall_time = time.perf_counter() - t_wall_start

        # Separate successes and failures — both are reported
        good = []
        errors = []
        for r in results:
            if isinstance(r, Exception):
                errors.append(str(r))
            else:
                good.append(r)

        if errors:
            print(f"  {len(errors)}/{len(results)} requests FAILED")
            # Print first unique error
            unique = list(dict.fromkeys(errors))
            for e in unique[:3]:
                print(f"    > {e[:200]}")

        return good, errors, wall_time


def summarize(results: list[RequestResult], errors: list[str], concurrency: int, num_requests: int, wall_time: float) -> dict:
    """Compute summary statistics."""
    if not results:
        unique_errors = list(dict.fromkeys(errors))[:5]
        return {"concurrency": concurrency, "num_requests": num_requests,
                "successful": 0, "failed": len(errors), "wall_time_s": wall_time,
                "error": "no successful requests", "error_samples": unique_errors}

    ttfts = [r.ttft for r in results]
    throughputs = [r.throughput for r in results]
    total_times = [r.total_time for r in results]
    itls = [r.inter_token_latency for r in results if r.inter_token_latency > 0]
    tokens = [r.tokens_generated for r in results]

    def percentile(data, p):
        if not data:
            return 0.0
        sorted_data = sorted(data)
        idx = int(len(sorted_data) * p / 100)
        idx = min(idx, len(sorted_data) - 1)
        return sorted_data[idx]

    total_tokens = sum(tokens)
    total_wall = max(r.total_time for r in results)  # wall clock for concurrent batch

    return {
        "concurrency": concurrency,
        "num_requests": num_requests,
        "successful": len(results),
        "failed": len(errors),
        "total_tokens_generated": total_tokens,
        "ttft_avg_ms": sum(ttfts) / len(ttfts) * 1000,
        "ttft_p50_ms": percentile(ttfts, 50) * 1000,
        "ttft_p99_ms": percentile(ttfts, 99) * 1000,
        "throughput_avg_tps": sum(throughputs) / len(throughputs),
        "throughput_p50_tps": percentile(throughputs, 50),
        "itl_avg_ms": sum(itls) / len(itls) if itls else 0.0,
        "itl_p50_ms": percentile(itls, 50) if itls else 0.0,
        "latency_avg_s": sum(total_times) / len(total_times),
        "latency_p50_s": percentile(total_times, 50),
        "latency_p99_s": percentile(total_times, 99),
        "aggregate_throughput_tps": total_tokens / total_wall if total_wall > 0 else 0.0,
        "wall_time_s": wall_time,
        "error_samples": list(dict.fromkeys(errors))[:5] if errors else [],
    }


def get_model_name(base_url: str) -> str:
    """Query the server for the model name."""
    import urllib.request
    try:
        with urllib.request.urlopen(f"{base_url}/v1/models", timeout=10) as resp:
            data = json.loads(resp.read())
            models = data.get("data", [])
            if models:
                return models[0]["id"]
    except Exception:
        pass
    return "unknown"


def main():
    parser = argparse.ArgumentParser(description="AppleBench — LLM inference benchmark")
    parser.add_argument("--port", type=int, required=True, help="Server port")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--concurrency", default="16,8,1", help="Comma-separated concurrency levels")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests per concurrency level")
    parser.add_argument("--warmup", type=int, default=3, help="Warmup requests")
    parser.add_argument("--framework", required=True, help="Framework name (for labeling results)")
    parser.add_argument("--model", default=None, help="Model name to use in API calls (auto-detected if not set)")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--prompts", default=None, help="Path to prompts JSON file")
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    # Load prompts
    if args.prompts:
        prompts_path = Path(args.prompts)
    else:
        prompts_path = Path(__file__).parent.parent / "prompts" / "benchmark_prompts.json"
    with open(prompts_path) as f:
        prompts = json.load(f)

    # Get model name from server or use provided
    model = args.model if args.model else get_model_name(base_url)
    print(f"Framework: {args.framework}")
    print(f"Model: {model}")
    print(f"Endpoint: {base_url}")
    print()

    concurrency_levels = [int(c) for c in args.concurrency.split(",")]

    all_results = {
        "framework": args.framework,
        "model": model,
        "endpoint": base_url,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "concurrency_results": [],
    }

    t_total_start = time.perf_counter()

    for conc in concurrency_levels:
        print(f"--- Concurrency: {conc} ---")
        try:
            good, errors, wall_time = asyncio.run(run_concurrent(
                base_url, model, prompts, conc, args.requests, args.warmup
            ))
        except Exception as e:
            print(f"  SERVER CRASHED: {e}")
            all_results["concurrency_results"].append(
                {"concurrency": conc, "num_requests": args.requests,
                 "successful": 0, "failed": args.requests,
                 "wall_time_s": 0, "error": f"server crashed: {e}"}
            )
            print()
            continue
        summary = summarize(good, errors, conc, args.requests, wall_time)
        all_results["concurrency_results"].append(summary)

        # Print summary
        failed = summary.get('failed', 0)
        fail_str = f" | FAILED: {failed}" if failed else ""
        print(f"  TTFT avg: {summary.get('ttft_avg_ms', 0):.1f}ms | "
              f"Throughput avg: {summary.get('throughput_avg_tps', 0):.1f} tok/s | "
              f"Aggregate: {summary.get('aggregate_throughput_tps', 0):.1f} tok/s | "
              f"ITL avg: {summary.get('itl_avg_ms', 0):.1f}ms | "
              f"Wall: {wall_time:.1f}s{fail_str}")
        print()

    total_duration = time.perf_counter() - t_total_start
    all_results["total_duration_s"] = total_duration
    print(f"Total benchmark duration: {total_duration:.1f}s")

    # Save results
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(__file__).parent.parent / "results" / f"{args.framework}_{time.strftime('%Y%m%d_%H%M%S')}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Results saved to: {output_path}")

    return all_results


if __name__ == "__main__":
    main()
