#!/usr/bin/env bash
# Build RMP Learning Lambda deployment package (psycopg2 for Aurora; Lambda boto3).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ROOT}/infrastructure/rmp_learning_lambda_src"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# Install psycopg2 for Aurora (Linux x86_64 for Lambda)
python3 -m pip install --target "$OUT_DIR" \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  psycopg2-binary \
  --quiet

cp -r "${ROOT}/src/rmp_learning" "$OUT_DIR/"

cat > "$OUT_DIR/lambda_handler.py" << 'EOF'
"""Lambda entry point for RMP Learning (POST /rmp/learning, GET /rmp/learning/me, GET /rmp/learning/leaderboard)."""
from rmp_learning.api.handler import handler

__all__ = ["handler"]
EOF

echo "Built infrastructure/rmp_learning_lambda_src/"
