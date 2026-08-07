#!/bin/bash
# Local CI script to run formatting, linting, and tests

set -e

echo "======================================"
echo "    Running DICA Local CI Pipeline    "
echo "======================================"

echo ""
echo "[1/3] Running Code Formatter (ruff format)..."
uv run ruff format src/ tests/

echo ""
echo "[2/3] Running Code Linter (ruff check)..."
# We allow exit code 0 even if there are some rules violated during local dev,
# but ideally we want to enforce it strictly. For now we just display warnings.
uv run ruff check src/ tests/ || echo "⚠️ Linter found issues to fix."

echo ""
echo "[3/3] Running Test Suite (pytest with coverage)..."
uv run pytest -v --cov=src/dica --cov-report=term-missing

echo ""
echo "✅ Local CI Pipeline Completed."
