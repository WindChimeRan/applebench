# AppleBench Results — Gemma-4-E4B-it (chat)

**Model:** Gemma-4-E4B-it
**Split:** chat
**Generated:** 2026-04-25 12:58:37

## Concurrency: 1

| Metric | mlx_lm | omlx | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 100 / 0 | 98 / 2 |
| TTFT avg (ms) | 1041.7 | 217.7 | 1075.3 |
| TTFT p50 (ms) | 806.0 | 189.5 | 593.0 |
| TTFT p99 (ms) | 2762.0 | 804.4 | 5132.5 |
| Throughput avg (tok/s) | 20.9 | 156.5 | 29.8 |
| Output throughput (tok/s) | 14.5 | 96.5 | 22.1 |
| Input throughput (tok/s) | N/A | 2075.9 | 281.2 |
| Total token throughput (tok/s) | N/A | 2172.3 | 303.4 |
| ITL avg (ms) | 48.6 | 5.2 | 31.8 |
| ITL p50 (ms) | 48.0 | 5.0 | 31.7 |
| Latency avg (s) | 3.49 | 0.48 | 3.53 |
| Latency p99 (s) | 10.33 | 1.96 | 9.55 |
| Wall time (s) | 343.4 | 48.0 | 347.8 |

## Concurrency: 8

| Metric | mlx_lm | omlx | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 100 / 0 | 98 / 2 |
| TTFT avg (ms) | 23544.0 | 475.4 | 3087.9 |
| TTFT p50 (ms) | 23546.1 | 395.7 | 2936.9 |
| TTFT p99 (ms) | 39129.7 | 1806.5 | 6204.6 |
| Throughput avg (tok/s) | 20.9 | 17.0 | 23.2 |
| Output throughput (tok/s) | 14.5 | 114.9 | 90.3 |
| Input throughput (tok/s) | N/A | 2543.4 | 1148.5 |
| Total token throughput (tok/s) | N/A | 2658.3 | 1238.8 |
| ITL avg (ms) | 48.6 | 59.7 | 41.3 |
| ITL p50 (ms) | 48.0 | 59.4 | 40.1 |
| Latency avg (s) | 25.99 | 3.09 | 6.27 |
| Latency p99 (s) | 44.15 | 14.46 | 16.93 |
| Wall time (s) | 343.4 | 39.2 | 85.2 |

## Concurrency: 16

| Metric | mlx_lm | omlx | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 100 / 0 | 98 / 2 |
| TTFT avg (ms) | 46946.3 | 3240.7 | 8411.5 |
| TTFT p50 (ms) | 49597.2 | 3368.0 | 8606.3 |
| TTFT p99 (ms) | 68445.8 | 4984.7 | 14111.8 |
| Throughput avg (tok/s) | 20.9 | 17.9 | 23.4 |
| Output throughput (tok/s) | 14.5 | 118.3 | 92.4 |
| Input throughput (tok/s) | N/A | 2583.0 | 1174.8 |
| Total token throughput (tok/s) | N/A | 2701.3 | 1267.1 |
| ITL avg (ms) | 48.6 | 61.1 | 40.7 |
| ITL p50 (ms) | 47.9 | 57.3 | 39.8 |
| Latency avg (s) | 49.39 | 5.85 | 11.56 |
| Latency p99 (s) | 70.17 | 17.96 | 24.69 |
| Wall time (s) | 343.3 | 38.6 | 83.3 |

## Total Benchmark Duration

| Framework | mlx_lm | omlx | llamacpp |
|-----------|--------|--------|--------|
| Duration | 17.6m | 2.2m | 8.9m |
