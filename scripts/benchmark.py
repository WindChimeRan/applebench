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
    tokens_generated: int  # SSE content chunks received (client-side count)
    throughput: float    # tokens/sec (decode only, excludes TTFT)
    inter_token_latency: float  # average ms between tokens
    prompt_tokens: int | None = None      # server-reported, from usage chunk
    completion_tokens: int | None = None  # server-reported, from usage chunk
    content: str = ""    # concatenated assistant content deltas
    reasoning: str = ""  # concatenated reasoning_content / reasoning deltas
    request_idx: int = -1  # submission index within the concurrency level


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
        "stream_options": {"include_usage": True},
    }

    t_start = time.perf_counter()
    t_first_token = None
    token_times = []
    tokens_generated = 0
    prompt_tokens = None
    completion_tokens = None
    content_chunks = []
    reasoning_chunks = []

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
            if usage := data.get("usage"):
                prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
                completion_tokens = usage.get("completion_tokens", completion_tokens)
            choices = data.get("choices", [])
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            content_delta = delta.get("content", "")
            reasoning_delta = delta.get("reasoning_content", "") or delta.get("reasoning", "")
            if content_delta or reasoning_delta:
                now = time.perf_counter()
                if t_first_token is None:
                    t_first_token = now
                token_times.append(now)
                tokens_generated += 1
                if content_delta:
                    content_chunks.append(content_delta)
                if reasoning_delta:
                    reasoning_chunks.append(reasoning_delta)

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

    # Detect silent failures: server returned 200 but generated 0-1 tokens
    if tokens_generated <= 1 and max_tokens > 1:
        raise RuntimeError(
            f"silent failure: server returned OK but generated only "
            f"{tokens_generated} token(s) for prompt '{prompt['name']}' "
            f"(requested max_tokens={max_tokens})"
        )

    return RequestResult(
        prompt_name=prompt["name"],
        ttft=ttft,
        total_time=total_time,
        tokens_generated=tokens_generated,
        throughput=throughput,
        inter_token_latency=itl,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        content="".join(content_chunks),
        reasoning="".join(reasoning_chunks),
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

        async def bounded_request(prompt, idx):
            async with sem:
                r = await benchmark_single(session, base_url, model, prompt, prompt["max_tokens"])
                r.request_idx = idx
                return r

        tasks = []
        for i in range(num_requests):
            prompt = prompts[i % len(prompts)]
            tasks.append(bounded_request(prompt, i))

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

    total_chunks = sum(tokens)

    # Server-reported token counts from the usage chunk (None if any request missing it)
    completion_list = [r.completion_tokens for r in results]
    prompt_list = [r.prompt_tokens for r in results]
    has_usage = all(t is not None for t in completion_list)
    has_input = all(t is not None for t in prompt_list)

    # Prefer server counts; fall back to chunk count (validate_results raises a warning)
    total_output_tokens = sum(completion_list) if has_usage else total_chunks
    total_input_tokens = sum(prompt_list) if has_input else None

    output_throughput = total_output_tokens / wall_time if wall_time > 0 else 0.0
    input_throughput = (total_input_tokens / wall_time) if (has_input and wall_time > 0) else None
    total_throughput = ((total_input_tokens + total_output_tokens) / wall_time) if (has_input and wall_time > 0) else None

    return {
        "concurrency": concurrency,
        "num_requests": num_requests,
        "successful": len(results),
        "failed": len(errors),
        "total_tokens_generated": total_chunks,
        "total_output_tokens": total_output_tokens,
        "total_input_tokens": total_input_tokens,
        "server_usage_available": has_usage,
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
        "output_throughput_tps": output_throughput,
        "input_throughput_tps": input_throughput,
        "total_token_throughput_tps": total_throughput,
        "wall_time_s": wall_time,
        "error_samples": list(dict.fromkeys(errors))[:5] if errors else [],
    }


def validate_results(results: list[RequestResult], summary: dict, prompts_used: list[dict]):
    """Warn about suspicious results that may indicate framework issues."""
    warnings = []

    successful = summary.get("successful", 0)
    if successful == 0:
        return warnings

    # Check 1: average tokens per request vs expected (prefer server-reported count)
    total_out = summary.get("total_output_tokens") or summary.get("total_tokens_generated", 0)
    avg_tokens = total_out / successful
    expected_max_tokens = sum(p["max_tokens"] for p in prompts_used[:successful]) / successful
    if avg_tokens < expected_max_tokens * 0.1:
        warnings.append(
            f"avg tokens/request ({avg_tokens:.0f}) is far below expected "
            f"(max_tokens avg={expected_max_tokens:.0f}). Possible silent failures."
        )

    # Check 2: throughput vs ITL consistency
    throughput_avg = summary.get("throughput_avg_tps", 0)
    itl_avg = summary.get("itl_avg_ms", 0)
    if throughput_avg > 0 and itl_avg > 0:
        implied_throughput = 1000.0 / itl_avg
        ratio = throughput_avg / implied_throughput if implied_throughput > 0 else 0
        if ratio < 0.25 or ratio > 4.0:
            warnings.append(
                f"throughput ({throughput_avg:.1f} tok/s) inconsistent with ITL "
                f"({itl_avg:.1f}ms, implies ~{implied_throughput:.1f} tok/s). "
                f"Ratio: {ratio:.2f}x."
            )

    # Check 3: many zero-throughput requests (p50 = 0 means >50% had 0 throughput)
    if summary.get("throughput_p50_tps", -1) == 0 and throughput_avg > 0:
        zero_count = sum(1 for r in results if r.throughput == 0)
        warnings.append(
            f"{zero_count}/{successful} requests had 0 throughput "
            f"(generated <=1 token each)."
        )

    # Check 4: server did not report token usage — fell back to SSE chunk count
    if not summary.get("server_usage_available", False):
        missing = sum(1 for r in results if r.completion_tokens is None)
        warnings.append(
            f"server did not report token usage for {missing}/{successful} requests "
            f"(missing `usage.completion_tokens`). Output counts fell back to SSE chunk "
            f"count, which may undercount if the framework bundles multiple tokens per "
            f"chunk. Framework should honor `stream_options.include_usage=true`."
        )

    # Check 5: server completion_tokens diverges from client-side chunk count
    if summary.get("server_usage_available", False):
        divergent = []
        for r in results:
            if r.completion_tokens is None or r.tokens_generated == 0:
                continue
            ratio = r.completion_tokens / r.tokens_generated
            if ratio < 0.95 or ratio > 1.05:
                divergent.append(ratio)
        if divergent:
            avg_ratio = sum(divergent) / len(divergent)
            warnings.append(
                f"{len(divergent)}/{successful} requests had server completion_tokens "
                f"diverging >5% from SSE chunk count (avg ratio {avg_ratio:.2f}x). "
                f"Framework may be bundling multiple tokens per chunk — per-request "
                f"throughput_avg_tps and itl_avg_ms are chunk-based and therefore suspect."
            )

    for w in warnings:
        print(f"  \u26a0 WARNING: {w}")

    return warnings


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
    parser.add_argument("--outputs", default=None,
                        help="Optional path for per-request outputs JSONL sidecar (content + reasoning per request)")
    parser.add_argument("--results-dir", default=None, help="Directory for result files (overrides default)")
    parser.add_argument("--prompts", default=None, help="Path to prompts JSON file")
    parser.add_argument("--split", default="chat", choices=["chat", "agent"],
                        help="Prompt split to use: 'chat' or 'agent' (default: chat)")
    parser.add_argument("--max-wall-time", type=int, default=3600,
                        help="Max wall time (seconds) per concurrency level before skipping remaining levels (default: 3600 = 60 min)")
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    # Load prompts
    if args.prompts:
        prompts_path = Path(args.prompts)
    else:
        split_file = f"{args.split}_benchmark_prompts.json"
        prompts_path = Path(__file__).parent.parent / "prompts" / split_file
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

    # Per-request outputs accumulator. Only populated if --outputs is set; one
    # record per successful request across all concurrency levels.
    all_outputs = []

    t_total_start = time.perf_counter()

    skip_remaining = False
    for conc in concurrency_levels:
        if skip_remaining:
            print(f"--- Concurrency: {conc} --- SKIPPED (previous level exceeded {args.max_wall_time}s)")
            all_results["concurrency_results"].append(
                {"concurrency": conc, "num_requests": args.requests,
                 "successful": 0, "failed": args.requests,
                 "wall_time_s": 0, "error": "skipped (previous level too slow)"}
            )
            print()
            continue

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

        # Sanity checks
        prompts_used = [prompts[i % len(prompts)] for i in range(args.requests)]
        sanity_warnings = validate_results(good, summary, prompts_used)
        if sanity_warnings:
            summary["sanity_warnings"] = sanity_warnings

        all_results["concurrency_results"].append(summary)

        if args.outputs:
            for r in good:
                all_outputs.append({
                    "concurrency": conc,
                    "request_idx": r.request_idx,
                    "prompt_name": r.prompt_name,
                    "content": r.content,
                    "reasoning": r.reasoning,
                    "tokens_generated": r.tokens_generated,
                })

        # Print summary
        failed = summary.get('failed', 0)
        fail_str = f" | FAILED: {failed}" if failed else ""
        print(f"  TTFT avg: {summary.get('ttft_avg_ms', 0):.1f}ms | "
              f"Throughput avg: {summary.get('throughput_avg_tps', 0):.1f} tok/s | "
              f"Output: {summary.get('output_throughput_tps', 0):.1f} tok/s | "
              f"ITL avg: {summary.get('itl_avg_ms', 0):.1f}ms | "
              f"Wall: {wall_time:.1f}s{fail_str}")
        if wall_time > args.max_wall_time:
            print(f"  ⚠ Wall time ({wall_time:.0f}s) exceeded limit ({args.max_wall_time}s). Skipping remaining levels.")
            skip_remaining = True
        print()

    total_duration = time.perf_counter() - t_total_start
    all_results["total_duration_s"] = total_duration
    print(f"Total benchmark duration: {total_duration:.1f}s")

    # Save results
    if args.output:
        output_path = Path(args.output)
    elif args.results_dir:
        output_path = Path(args.results_dir) / f"{args.framework}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    else:
        output_path = Path(__file__).parent.parent / "results" / f"{args.framework}_{time.strftime('%Y%m%d_%H%M%S')}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Results saved to: {output_path}")

    if args.outputs:
        outputs_path = Path(args.outputs)
        outputs_path.parent.mkdir(parents=True, exist_ok=True)
        with open(outputs_path, "w") as f:
            for record in all_outputs:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Outputs saved to: {outputs_path} ({len(all_outputs)} records)")

    return all_results


if __name__ == "__main__":
    main()
