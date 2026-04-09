#!/bin/bash
# Stop llama.cpp server
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

PID_FILE="$PROJECT_DIR/.frameworks/llamacpp_server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        # Wait for graceful shutdown, then force kill
        for i in $(seq 1 5); do
            kill -0 "$PID" 2>/dev/null || break
            sleep 1
        done
        kill -9 "$PID" 2>/dev/null || true
        echo "llama.cpp server (PID $PID) stopped"
    else
        echo "llama.cpp server (PID $PID) was not running"
    fi
    rm -f "$PID_FILE"
else
    echo "No PID file found for llama.cpp server"
fi
