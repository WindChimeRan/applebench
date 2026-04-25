# AppleBench Results — Gemma-4-E4B-it (agent)

**Model:** Gemma-4-E4B-it
**Split:** agent
**Generated:** 2026-04-25 06:39:51

## Concurrency: 1

| Metric | mlx_lm | omlx | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 64 / 36 | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 3594.2 | 463.0 | 4602.9 |
| TTFT p50 (ms) | 2925.2 | 290.1 | 3368.9 |
| TTFT p99 (ms) | 15046.0 | 2169.2 | 17815.4 |
| Throughput avg (tok/s) | 18.1 | 133.6 | 30.2 |
| Output throughput (tok/s) | 5.3 | 68.1 | 12.6 |
| Input throughput (tok/s) | N/A | 4760.9 | 606.6 |
| Total token throughput (tok/s) | N/A | 4829.0 | 619.2 |
| ITL avg (ms) | 68.6 | 6.7 | 32.1 |
| ITL p50 (ms) | 48.0 | 6.6 | 32.1 |
| Latency avg (s) | 6.78 | 0.90 | 7.65 |
| Latency p99 (s) | 16.21 | 2.99 | 20.93 |
| Wall time (s) | 732.4 | 89.6 | 765.2 |

## Concurrency: 8

| Metric | mlx_lm | omlx | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 64 / 36 | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 53228.1 | 789.0 | 22236.0 |
| TTFT p50 (ms) | 54264.9 | 666.0 | 21181.8 |
| TTFT p99 (ms) | 78762.7 | 3589.7 | 50243.7 |
| Throughput avg (tok/s) | 18.1 | 12.6 | 11.1 |
| Output throughput (tok/s) | 5.3 | 80.6 | 20.7 |
| Input throughput (tok/s) | N/A | 5506.9 | 994.1 |
| Total token throughput (tok/s) | N/A | 5587.5 | 1014.8 |
| ITL avg (ms) | 68.5 | 89.4 | 163.2 |
| ITL p50 (ms) | 48.0 | 86.7 | 119.0 |
| Latency avg (s) | 56.41 | 6.04 | 36.66 |
| Latency p99 (s) | 81.36 | 25.95 | 105.15 |
| Wall time (s) | 732.5 | 77.5 | 467.0 |

## Concurrency: 16

| Metric | mlx_lm | omlx | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 64 / 36 | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 108013.2 | 6170.0 | 57931.2 |
| TTFT p50 (ms) | 113497.7 | 6274.6 | 57825.4 |
| TTFT p99 (ms) | 136101.5 | 9467.7 | 96527.8 |
| Throughput avg (tok/s) | 18.1 | 12.6 | 10.8 |
| Output throughput (tok/s) | 5.3 | 83.8 | 20.4 |
| Input throughput (tok/s) | N/A | 5776.8 | 988.2 |
| Total token throughput (tok/s) | N/A | 5860.7 | 1008.6 |
| ITL avg (ms) | 68.5 | 89.1 | 179.0 |
| ITL p50 (ms) | 48.0 | 84.5 | 123.0 |
| Latency avg (s) | 111.20 | 11.17 | 72.28 |
| Latency p99 (s) | 140.58 | 28.92 | 139.61 |
| Wall time (s) | 732.3 | 73.9 | 469.7 |

## Total Benchmark Duration

| Framework | mlx_lm | omlx | llamacpp |
|-----------|--------|--------|--------|
| Duration | 37.9m | 4.2m | 29.5m |
