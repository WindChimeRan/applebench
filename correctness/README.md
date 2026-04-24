# Correctness Eval

Framework-correctness evaluation — separate from AppleBench's perf benchmark.

Goal: verify that each inference framework produces the same *answers* on a
labeled classification task. Perf (tok/s, TTFT) says nothing about whether a
framework's outputs are correct, so a fast-but-broken framework would go
undetected in the main AppleBench pipeline.

**Task.** GMRID_v3 supply-chain disruption news classification from
[inflaton/llms-at-edge](https://github.com/inflaton/llms-at-edge). 1147-row
test split, 8 classes, single-label. Uses the exact system prompt, few-shot
examples, and weighted-F1 scorer from their paper (IJCNN 2025).

**Not** AppleBench. Fully self-contained under `correctness/`. The AppleBench
perf pipeline (`scripts/`, `prompts/`, `results/`, `benchmark.py`,
`run_all.sh`, weekly skill) is untouched.

## Layout

```
correctness/
├── data/                        # gitignored — fetched from inflaton raw URLs
│   ├── GMRID_v3-test.csv
│   └── categories.json
├── prompts/                     # gitignored — built by build_prompts.py
│   ├── 0shot/{prompts,labels}.jsonl
│   └── 5shot/{prompts,labels}.jsonl
├── results/                     # scores.json committed, responses.jsonl not
│   └── <backend>_<model>_<N>shot/
│       ├── responses.jsonl      # gitignored
│       └── scores.json
├── scripts/
│   ├── fetch_data.sh            # curl GMRID + categories.json → data/
│   ├── build_prompts.py         # CSV + categories → prompts.jsonl + labels.jsonl
│   ├── run_eval.py              # OpenAI-compatible client → responses.jsonl
│   └── score_f1.py              # responses + labels → scores.json
├── run.sh                       # end-to-end wrapper
└── requirements.txt
```

## Setup

```bash
# From repo root
python3 -m venv .venvs/correctness
source .venvs/correctness/bin/activate  # bash; tcsh: source .venvs/correctness/bin/activate.csh
pip install -r correctness/requirements.txt

# Fetch the dataset (one-time)
bash correctness/scripts/fetch_data.sh

# Build prompts for 0-shot and 5-shot
python correctness/scripts/build_prompts.py --shots 0
python correctness/scripts/build_prompts.py --shots 5
```

## Running against a live endpoint

Works against any OpenAI-compatible `/v1/chat/completions` server. On NVIDIA:

```bash
# Terminal 1: serve Qwen3-0.6B with vLLM
vllm serve Qwen/Qwen3-0.6B --port 8000

# Terminal 2: run eval at both shot settings, score
bash correctness/run.sh \
  --backend vllm-nvidia \
  --model Qwen/Qwen3-0.6B \
  --base-url http://localhost:8000
```

Or individual steps:

```bash
python correctness/scripts/run_eval.py \
  --base-url http://localhost:8000 \
  --model Qwen/Qwen3-0.6B \
  --prompts correctness/prompts/5shot/prompts.jsonl \
  --output correctness/results/vllm-nvidia_Qwen3-0.6B_5shot/responses.jsonl

python correctness/scripts/score_f1.py \
  --responses correctness/results/vllm-nvidia_Qwen3-0.6B_5shot/responses.jsonl \
  --labels correctness/prompts/5shot/labels.jsonl \
  --output correctness/results/vllm-nvidia_Qwen3-0.6B_5shot/scores.json
```

## On Mac later

Each of the 9 AppleBench frameworks already serves OpenAI on ports 8001–8007.
Same procedure — start `serve_<fw>.sh`, point `run.sh` at it, stop, next. A
helper wrapper that loops over all 9 will land alongside.

## Decoding

- `temperature=0.0, top_p=1.0` (greedy). For vLLM, `top_k=-1` passed via
  `extra_body` when supported.
- Qwen3 thinking-off: `/no_think` appended to the system prompt for
  backend-portable behavior (works regardless of whether the framework honors
  `chat_template_kwargs={"enable_thinking": False}`).
- `max_tokens=256` — model should emit a short JSON object.

## Reference sanity check

Before trusting vLLM-NVIDIA's F1 as "the model's true capability," cross-check
against HF-transformers on the same NVIDIA box with identical settings. They
should agree within ~1 F1 point. If they don't, vLLM's chat template or
sampler is suspect and the reference isn't clean yet.

## Metric

Per inflaton: weighted-F1 over the 8-class `Summarized_label`. Also reported:
macro-F1, exact-match, per-class P/R/F1, and JSON-parse-failure rate.
