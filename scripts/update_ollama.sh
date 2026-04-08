#!/bin/bash
# Update Ollama to latest
set -e
echo "=== Updating Ollama ==="
brew upgrade ollama || echo "Ollama already up to date"
echo "=== Ollama updated ==="
