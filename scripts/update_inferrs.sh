#!/bin/bash
# Update inferrs to latest
set -e
echo "=== Updating inferrs ==="
brew upgrade inferrs || echo "inferrs already up to date"
echo "=== inferrs updated ==="
