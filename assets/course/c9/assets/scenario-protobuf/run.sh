#!/usr/bin/env bash
# run.sh — porneste receiver in background, apoi sender
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

if [ ! -f sensors_pb2.py ]; then
    echo "[run] sensors_pb2.py nu exista. ruleaza ./setup.sh mai intai."
    exit 1
fi

echo "[run] pornesc receiver ..."
python3 receiver.py &
RECV_PID=$!

sleep 0.3

echo "[run] pornesc sender ..."
python3 sender.py

# asteapta sa se proceseze ultimul batch
sleep 0.5

echo "[run] opresc receiver ..."
kill "$RECV_PID" 2>/dev/null || true
wait "$RECV_PID" 2>/dev/null || true

echo "[run] done"
