# AppleBench Results — Qwen3.5-0.8B (agent)

**Model:** Qwen3.5-0.8B
**Split:** agent
**Generated:** 2026-04-25 18:00:32

## Concurrency: 1

| Metric | llamacpp | omlx | vllm_metal | mlx_lm |
|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 100 / 0 | 100 / 0 | 99 / 1 |
| TTFT avg (ms) | 786.3 | 692.0 | 3541.3 | 986.1 |
| TTFT p50 (ms) | 649.4 | 577.1 | 2372.0 | 744.5 |
| TTFT p99 (ms) | 2732.7 | 2217.7 | 10265.3 | 2238.2 |
| Throughput avg (tok/s) | 109.3 | 85.3 | 42.9 | 94.0 |
| Output throughput (tok/s) | 49.0 | 48.7 | 11.9 | 37.9 |
| Input throughput (tok/s) | 3372.1 | 3515.1 | 944.4 | N/A |
| Total token throughput (tok/s) | 3421.2 | 3563.8 | 956.2 | N/A |
| ITL avg (ms) | 8.8 | 10.8 | 23.9 | 12.4 |
| ITL p50 (ms) | 8.8 | 11.1 | 22.0 | 10.0 |
| Latency avg (s) | 1.37 | 1.31 | 4.89 | 1.77 |
| Latency p99 (s) | 3.88 | 3.78 | 12.90 | 3.58 |
| Wall time (s) | 136.9 | 131.4 | 489.0 | 175.9 |

## Concurrency: 8

| Metric | llamacpp | omlx | vllm_metal | mlx_lm |
|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 100 / 0 | 100 / 0 | 99 / 1 |
| TTFT avg (ms) | 3725.4 | 596.2 | 6016.8 | 12798.0 |
| TTFT p50 (ms) | 3795.8 | 399.5 | 4791.4 | 12607.9 |
| TTFT p99 (ms) | 6906.1 | 2470.4 | 30356.0 | 18061.1 |
| Throughput avg (tok/s) | 36.2 | 17.8 | 3.6 | 95.6 |
| Output throughput (tok/s) | 84.8 | 125.4 | 14.6 | 38.2 |
| Input throughput (tok/s) | 5848.6 | 9998.7 | 1176.8 | N/A |
| Total token throughput (tok/s) | 5933.4 | 10124.1 | 1191.5 | N/A |
| ITL avg (ms) | 38.9 | 59.5 | 507.7 | 12.2 |
| ITL p50 (ms) | 25.2 | 58.9 | 407.0 | 9.8 |
| Latency avg (s) | 6.21 | 3.52 | 31.09 | 13.57 |
| Latency p99 (s) | 19.22 | 17.69 | 168.17 | 19.49 |
| Wall time (s) | 78.9 | 46.2 | 392.4 | 174.5 |

## Concurrency: 16

| Metric | llamacpp | omlx | vllm_metal | mlx_lm |
|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 100 / 0 | 100 / 0 | 99 / 1 |
| TTFT avg (ms) | 8941.6 | 3709.4 | 14010.9 | 25350.4 |
| TTFT p50 (ms) | 9762.5 | 3695.4 | 9730.1 | 25695.8 |
| TTFT p99 (ms) | 14208.3 | 5762.4 | 71406.4 | 34788.8 |
| Throughput avg (tok/s) | 38.0 | 16.8 | 1.8 | 95.6 |
| Output throughput (tok/s) | 90.5 | 125.1 | 14.6 | 38.1 |
| Input throughput (tok/s) | 6214.5 | 10088.3 | 1209.9 | N/A |
| Total token throughput (tok/s) | 6305.0 | 10213.3 | 1224.5 | N/A |
| ITL avg (ms) | 37.1 | 63.9 | 944.0 | 12.2 |
| ITL p50 (ms) | 23.7 | 61.2 | 862.7 | 9.9 |
| Latency avg (s) | 11.34 | 6.71 | 60.03 | 26.12 |
| Latency p99 (s) | 22.58 | 20.44 | 271.37 | 35.39 |
| Wall time (s) | 74.3 | 45.8 | 381.7 | 174.7 |

## Total Benchmark Duration

| Framework | llamacpp | omlx | vllm_metal | mlx_lm |
|-----------|--------|--------|--------|--------|
| Duration | 5.1m | 3.9m | 21.9m | 9.0m |
