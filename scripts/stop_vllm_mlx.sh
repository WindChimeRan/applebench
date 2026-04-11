#!/bin/bash
# Stop vllm-mlx server
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

PID_FILE="$PROJECT_DIR/.frameworks/vllm_mlx_server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        for i in $(seq 1 5); do
            kill -0 "$PID" 2>/dev/null || break
            sleep 1
        done
        kill -9 "$PID" 2>/dev/null || true
        echo "vllm-mlx server (PID $PID) stopped"
    else
        echo "vllm-mlx server (PID $PID) was not running"
    fi
    rm -f "$PID_FILE"
else
    echo "No PID file found for vllm-mlx server"
fi
