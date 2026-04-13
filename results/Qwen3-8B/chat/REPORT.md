# AppleBench Results — Qwen3-8B (chat)

**Model:** Qwen3-8B
**Split:** chat
**Generated:** 2026-04-13 18:11:16

## Concurrency: 1

| Metric | vllm_metal | ollama | omlx | mistralrs | inferrs | mlx_lm |
|--------|--------|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 2 / 98 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 3683.6 | 76812.7 | 191.5 | 2524.2 | 4096.7 | 1959.9 |
| TTFT p50 (ms) | 1324.0 | 89454.8 | 189.7 | 1303.8 | 1637.4 | 1197.0 |
| TTFT p99 (ms) | 15960.2 | 89454.8 | 288.1 | 8766.1 | 16611.1 | 7235.2 |
| Throughput avg (tok/s) | 17.3 | 0.0 | 181.9 | 7.7 | 2.0 | 21.7 |
| Output throughput (tok/s) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Input throughput (tok/s) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Total token throughput (tok/s) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ITL avg (ms) | 58.5 | 19008.0 | 5.5 | 129.3 | 552.2 | 46.1 |
| ITL p50 (ms) | 55.1 | 23514.9 | 5.4 | 129.4 | 441.3 | 45.3 |
| Latency avg (s) | 12.97 | 121.03 | 1.03 | 22.86 | 64.62 | 9.16 |
| Latency p99 (s) | 34.98 | 143.36 | 1.95 | 42.24 | 293.90 | 19.50 |
| Wall time (s) | 1296.5 | 27865.9 | 103.1 | 2286.5 | 6462.0 | 915.7 |

## Concurrency: 8

| Metric | vllm_metal | ollama | omlx | mistralrs | inferrs | mlx_lm |
|--------|--------|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | SKIPPED (PREVIOUS LEVEL TOO SLOW) | 100 / 0 | 16 / 84 | SKIPPED (PREVIOUS LEVEL TOO SLOW) | 100 / 0 |
| TTFT avg (ms) | 7293.1 | 0.0 | 518.4 | 23787.6 | 0.0 | 6725.5 |
| TTFT p50 (ms) | 3290.9 | 0.0 | 405.5 | 23403.5 | 0.0 | 4674.3 |
| TTFT p99 (ms) | 34660.5 | 0.0 | 1800.7 | 49752.0 | 0.0 | 22622.1 |
| Throughput avg (tok/s) | 3.7 | 0.0 | 32.3 | 0.7 | 0.0 | 5.1 |
| Output throughput (tok/s) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Input throughput (tok/s) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Total token throughput (tok/s) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ITL avg (ms) | 308.9 | 0.0 | 32.0 | 1621.4 | 0.0 | 216.7 |
| ITL p50 (ms) | 302.4 | 0.0 | 32.5 | 1491.8 | 0.0 | 216.9 |
| Latency avg (s) | 55.54 | 0.00 | 5.26 | 124.11 | 0.00 | 40.26 |
| Latency p99 (s) | 116.97 | 0.00 | 10.06 | 203.03 | 0.00 | 81.07 |
| Wall time (s) | 708.4 | 0.0 | 67.4 | 944.6 | 0.0 | 514.1 |

## Concurrency: 16

| Metric | vllm_metal | ollama | omlx | mistralrs | inferrs | mlx_lm |
|--------|--------|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | SKIPPED (PREVIOUS LEVEL TOO SLOW) | 100 / 0 | CRASHED | SKIPPED (PREVIOUS LEVEL TOO SLOW) | 55 / 45 |
| TTFT avg (ms) | 12487.8 | 0.0 | 5220.5 | 0.0 | 0.0 | 22695.9 |
| TTFT p50 (ms) | 12004.9 | 0.0 | 5584.7 | 0.0 | 0.0 | 22099.3 |
| TTFT p99 (ms) | 48929.7 | 0.0 | 7139.1 | 0.0 | 0.0 | 51432.5 |
| Throughput avg (tok/s) | 2.5 | 0.0 | 32.9 | 0.0 | 0.0 | 3.6 |
| Output throughput (tok/s) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Input throughput (tok/s) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Total token throughput (tok/s) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ITL avg (ms) | 476.5 | 0.0 | 31.3 | 0.0 | 0.0 | 327.2 |
| ITL p50 (ms) | 465.1 | 0.0 | 31.9 | 0.0 | 0.0 | 276.4 |
| Latency avg (s) | 86.18 | 0.00 | 9.94 | 0.00 | 0.00 | 67.38 |
| Latency p99 (s) | 185.58 | 0.00 | 16.08 | 0.00 | 0.00 | 143.13 |
| Wall time (s) | 564.4 | 0.0 | 66.6 | 0.0 | 0.0 | 232.5 |

## Total Benchmark Duration

| Framework | vllm_metal | ollama | omlx | mistralrs | inferrs | mlx_lm |
|-----------|--------|--------|--------|--------|--------|--------|
| Duration | 44.3m | 466.1m | 4.0m | 55.0m | 111.7m | 28.6m |
