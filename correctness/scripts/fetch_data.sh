#!/bin/bash
# Fetch GMRID_v3 supply-chain classification dataset + category schema
# from inflaton/llms-at-edge raw URLs.
#
# Dataset source: https://github.com/inflaton/llms-at-edge
# Paper: "LLMs at the Edge: Performance and Efficiency Evaluation with
# Ollama on Diverse Hardware" (IJCNN 2025).
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
mkdir -p "$DATA_DIR"

RAW_BASE="https://raw.githubusercontent.com/inflaton/llms-at-edge/main"

echo "Fetching GMRID_v3-test.csv..."
curl -fL -o "$DATA_DIR/GMRID_v3-test.csv" "$RAW_BASE/dataset/GMRID_v3-test.csv"

echo "Fetching categories.json..."
curl -fL -o "$DATA_DIR/categories.json" "$RAW_BASE/dataset/categories.json"

echo ""
echo "Fetched:"
ls -lh "$DATA_DIR"/GMRID_v3-test.csv "$DATA_DIR"/categories.json
