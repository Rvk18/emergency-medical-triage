#!/usr/bin/env bash
# Build triage Lambda deployment package.
# Output: infrastructure/triage_lambda_src/ (for Terraform archive source_dir)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ROOT}/infrastructure/triage_lambda_src"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# Install dependencies for Lambda (Linux x86_64) - avoid Mac-built binaries
pip install --target "$OUT_DIR" \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  pydantic \
  --quiet

# Copy triage package
cp -r "${ROOT}/src/triage" "$OUT_DIR/"

# Lambda entry point
cat > "$OUT_DIR/lambda_handler.py" << 'EOF'
"""Lambda entry point for POST /triage."""
from triage.api.handler import handler

__all__ = ["handler"]
EOF

echo "Built infrastructure/triage_lambda_src/"
