# AppleBench Results

Generated: 2026-04-06 16:12:56

## Concurrency: 1

| Metric | llamacpp | mistralrs | mlx_lm | vllm_metal |
|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 179.4 | 377.8 | 300.5 | 840.2 |
| TTFT p50 (ms) | 101.7 | 182.7 | 191.7 | 205.8 |
| TTFT p99 (ms) | 832.0 | 1400.1 | 979.0 | 4180.5 |
| Throughput avg (tok/s) | 166.1 | 48.2 | 187.2 | 73.4 |
| Aggregate throughput (tok/s) | 5884.3 | 2217.1 | 5801.0 | 1336.7 |
| ITL avg (ms) | 6.0 | 20.7 | 5.4 | 15.3 |
| ITL p50 (ms) | 5.9 | 20.7 | 5.2 | 12.8 |
| Latency avg (s) | 1.10 | 3.53 | 1.12 | 3.22 |
| Latency p99 (s) | 2.61 | 6.88 | 2.64 | 11.53 |
| Wall time (s) | 110.3 | 352.8 | 112.1 | 322.4 |

## Concurrency: 8

| Metric | llamacpp | mistralrs | mlx_lm | vllm_metal |
|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 55 / 45 | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 1863.0 | 5810.4 | 1785.7 | 1409.2 |
| TTFT p50 (ms) | 1794.4 | 3769.4 | 1163.0 | 333.4 |
| TTFT p99 (ms) | 3119.2 | 31140.4 | 8151.5 | 7875.3 |
| Throughput avg (tok/s) | 104.0 | 2.4 | 31.5 | 14.1 |
| Aggregate throughput (tok/s) | 2491.1 | 26.4 | 836.0 | 509.9 |
| ITL avg (ms) | 10.3 | 592.9 | 35.4 | 84.0 |
| ITL p50 (ms) | 9.4 | 429.7 | 34.6 | 86.3 |
| Latency avg (s) | 3.40 | 85.54 | 7.35 | 13.87 |
| Latency p99 (s) | 6.12 | 298.91 | 18.41 | 30.49 |
| Wall time (s) | 43.8 | 1996.1 | 93.8 | 176.9 |

## Concurrency: 16

| Metric | llamacpp | mistralrs | mlx_lm | vllm_metal |
|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | CRASHED | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 5019.5 | 0.0 | 3371.2 | 1983.4 |
| TTFT p50 (ms) | 5318.9 | 0.0 | 2388.1 | 1093.4 |
| TTFT p99 (ms) | 7643.0 | 0.0 | 9470.9 | 10799.8 |
| Throughput avg (tok/s) | 101.7 | 0.0 | 19.8 | 8.5 |
| Aggregate throughput (tok/s) | 1468.8 | 0.0 | 542.2 | 329.9 |
| ITL avg (ms) | 10.4 | 0.0 | 63.6 | 138.0 |
| ITL p50 (ms) | 9.6 | 0.0 | 70.6 | 140.1 |
| Latency avg (s) | 6.58 | 0.00 | 13.77 | 22.39 |
| Latency p99 (s) | 10.38 | 0.00 | 28.31 | 46.40 |
| Wall time (s) | 44.1 | 0.0 | 88.8 | 145.2 |

## Total Benchmark Duration

| Framework | llamacpp | mistralrs | mlx_lm | vllm_metal |
|-----------|--------|--------|--------|--------|
| Duration | 3.4m | 39.3m | 5.0m | 11.1m |
