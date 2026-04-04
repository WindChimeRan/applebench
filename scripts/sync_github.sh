#!/bin/bash
# Sync benchmark results to GitHub
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

cd "$PROJECT_DIR"

# Stage results
git add results/
git add -u

# Commit with timestamp
DATE=$(date +"%Y-%m-%d %H:%M")
git commit -m "Benchmark results: $DATE" || echo "Nothing to commit"
git push || echo "Push failed — check remote configuration"
