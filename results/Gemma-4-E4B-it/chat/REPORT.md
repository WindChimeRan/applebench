# AppleBench Results — Gemma-4-E4B-it (chat)

**Model:** Gemma-4-E4B-it
**Split:** chat
**Generated:** 2026-04-25 05:24:32

## Concurrency: 1

| Metric | omlx | mlx_lm | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 98 / 2 | 98 / 2 |
| TTFT avg (ms) | 215.8 | 1041.7 | 1075.3 |
| TTFT p50 (ms) | 189.0 | 806.0 | 593.0 |
| TTFT p99 (ms) | 806.2 | 2762.0 | 5132.5 |
| Throughput avg (tok/s) | 156.4 | 20.9 | 29.8 |
| Output throughput (tok/s) | 96.9 | 14.5 | 22.1 |
| Input throughput (tok/s) | 2076.2 | N/A | 281.2 |
| Total token throughput (tok/s) | 2173.1 | N/A | 303.4 |
| ITL avg (ms) | 5.1 | 48.6 | 31.8 |
| ITL p50 (ms) | 5.0 | 48.0 | 31.7 |
| Latency avg (s) | 0.48 | 3.49 | 3.53 |
| Latency p99 (s) | 1.75 | 10.33 | 9.55 |
| Wall time (s) | 48.0 | 343.4 | 347.8 |

## Concurrency: 8

| Metric | omlx | mlx_lm | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 98 / 2 | 98 / 2 |
| TTFT avg (ms) | 486.0 | 23544.0 | 3087.9 |
| TTFT p50 (ms) | 402.6 | 23546.1 | 2936.9 |
| TTFT p99 (ms) | 1780.4 | 39129.7 | 6204.6 |
| Throughput avg (tok/s) | 17.2 | 20.9 | 23.2 |
| Output throughput (tok/s) | 114.7 | 14.5 | 90.3 |
| Input throughput (tok/s) | 2520.0 | N/A | 1148.5 |
| Total token throughput (tok/s) | 2634.6 | N/A | 1238.8 |
| ITL avg (ms) | 59.1 | 48.6 | 41.3 |
| ITL p50 (ms) | 59.7 | 48.0 | 40.1 |
| Latency avg (s) | 3.12 | 25.99 | 6.27 |
| Latency p99 (s) | 14.47 | 44.15 | 16.93 |
| Wall time (s) | 39.6 | 343.4 | 85.2 |

## Concurrency: 16

| Metric | omlx | mlx_lm | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 98 / 2 | 98 / 2 |
| TTFT avg (ms) | 3248.7 | 46946.3 | 8411.5 |
| TTFT p50 (ms) | 3390.1 | 49597.2 | 8606.3 |
| TTFT p99 (ms) | 4950.2 | 68445.8 | 14111.8 |
| Throughput avg (tok/s) | 18.7 | 20.9 | 23.4 |
| Output throughput (tok/s) | 119.4 | 14.5 | 92.4 |
| Input throughput (tok/s) | 2568.9 | N/A | 1174.8 |
| Total token throughput (tok/s) | 2688.2 | N/A | 1267.1 |
| ITL avg (ms) | 57.9 | 48.6 | 40.7 |
| ITL p50 (ms) | 55.4 | 47.9 | 39.8 |
| Latency avg (s) | 5.87 | 49.39 | 11.56 |
| Latency p99 (s) | 18.62 | 70.17 | 24.69 |
| Wall time (s) | 38.8 | 343.3 | 83.3 |

## Total Benchmark Duration

| Framework | omlx | mlx_lm | llamacpp |
|-----------|--------|--------|--------|
| Duration | 2.2m | 17.6m | 8.9m |
