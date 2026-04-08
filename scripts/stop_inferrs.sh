#!/bin/bash
# Stop inferrs server
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

PID_FILE="$PROJECT_DIR/.frameworks/inferrs_server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "inferrs server (PID $PID) stopped"
    else
        echo "inferrs server (PID $PID) was not running"
    fi
    rm -f "$PID_FILE"
else
    echo "No PID file found for inferrs server"
fi
