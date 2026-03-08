#!/usr/bin/env bash
# Build RMP Learning Lambda deployment package (no extra deps; uses Lambda boto3).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ROOT}/infrastructure/rmp_learning_lambda_src"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

cp -r "${ROOT}/src/rmp_learning" "$OUT_DIR/"

cat > "$OUT_DIR/lambda_handler.py" << 'EOF'
"""Lambda entry point for POST /rmp/learning."""
from rmp_learning.api.handler import handler

__all__ = ["handler"]
EOF

echo "Built infrastructure/rmp_learning_lambda_src/"
