# AppleBench Results — Gemma-4-E4B-it (agent)

**Model:** Gemma-4-E4B-it
**Split:** agent
**Generated:** 2026-04-25 13:04:04

## Concurrency: 1

| Metric | omlx | mlx_lm | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 64 / 36 | 100 / 0 |
| TTFT avg (ms) | 545.0 | 3594.2 | 4602.9 |
| TTFT p50 (ms) | 346.1 | 2925.2 | 3368.9 |
| TTFT p99 (ms) | 2386.7 | 15046.0 | 17815.4 |
| Throughput avg (tok/s) | 133.4 | 18.1 | 30.2 |
| Output throughput (tok/s) | 62.6 | 5.3 | 12.6 |
| Input throughput (tok/s) | 4379.4 | N/A | 606.6 |
| Total token throughput (tok/s) | 4442.0 | N/A | 619.2 |
| ITL avg (ms) | 6.7 | 68.6 | 32.1 |
| ITL p50 (ms) | 6.5 | 48.0 | 32.1 |
| Latency avg (s) | 0.97 | 6.78 | 7.65 |
| Latency p99 (s) | 2.94 | 16.21 | 20.93 |
| Wall time (s) | 97.4 | 732.4 | 765.2 |

## Concurrency: 8

| Metric | omlx | mlx_lm | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 64 / 36 | 100 / 0 |
| TTFT avg (ms) | 808.9 | 53228.1 | 22236.0 |
| TTFT p50 (ms) | 661.8 | 54264.9 | 21181.8 |
| TTFT p99 (ms) | 3321.1 | 78762.7 | 50243.7 |
| Throughput avg (tok/s) | 11.7 | 18.1 | 11.1 |
| Output throughput (tok/s) | 77.6 | 5.3 | 20.7 |
| Input throughput (tok/s) | 5686.8 | N/A | 994.1 |
| Total token throughput (tok/s) | 5764.4 | N/A | 1014.8 |
| ITL avg (ms) | 92.5 | 68.5 | 163.2 |
| ITL p50 (ms) | 92.7 | 48.0 | 119.0 |
| Latency avg (s) | 5.83 | 56.41 | 36.66 |
| Latency p99 (s) | 25.45 | 81.36 | 105.15 |
| Wall time (s) | 75.0 | 732.5 | 467.0 |

## Concurrency: 16

| Metric | omlx | mlx_lm | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 64 / 36 | 100 / 0 |
| TTFT avg (ms) | 6056.2 | 108013.2 | 57931.2 |
| TTFT p50 (ms) | 6141.2 | 113497.7 | 57825.4 |
| TTFT p99 (ms) | 9508.2 | 136101.5 | 96527.8 |
| Throughput avg (tok/s) | 12.4 | 18.1 | 10.8 |
| Output throughput (tok/s) | 83.1 | 5.3 | 20.4 |
| Input throughput (tok/s) | 5984.8 | N/A | 988.2 |
| Total token throughput (tok/s) | 6067.8 | N/A | 1008.6 |
| ITL avg (ms) | 90.8 | 68.5 | 179.0 |
| ITL p50 (ms) | 86.1 | 48.0 | 123.0 |
| Latency avg (s) | 10.91 | 111.20 | 72.28 |
| Latency p99 (s) | 28.20 | 140.58 | 139.61 |
| Wall time (s) | 71.3 | 732.3 | 469.7 |

## Total Benchmark Duration

| Framework | omlx | mlx_lm | llamacpp |
|-----------|--------|--------|--------|
| Duration | 4.2m | 37.9m | 29.5m |
