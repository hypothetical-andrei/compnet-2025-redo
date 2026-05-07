#!/usr/bin/env bash
# setup.sh — instaleaza dependentele si compileaza schema .proto
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

echo "[setup] instalare biblioteca protobuf ..."
pip3 install --quiet protobuf grpcio-tools

echo "[setup] compilare sensors.proto ..."
python3 -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    sensors.proto

echo "[setup] generat: sensors_pb2.py"
echo "[setup] gata. ruleaza ./run.sh"
