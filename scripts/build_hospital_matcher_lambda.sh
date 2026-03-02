#!/usr/bin/env bash
# Build Hospital Matcher Lambda deployment package.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ROOT}/infrastructure/hospital_matcher_lambda_src"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

python3 -m pip install --target "$OUT_DIR" \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  pydantic \
  --quiet

cp -r "${ROOT}/src/hospital_matcher" "$OUT_DIR/"

cat > "$OUT_DIR/lambda_handler.py" << 'EOF'
"""Lambda entry point for POST /hospitals."""
from hospital_matcher.api.handler import handler

__all__ = ["handler"]
EOF

echo "Built infrastructure/hospital_matcher_lambda_src/"
