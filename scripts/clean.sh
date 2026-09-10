#!/usr/bin/env bash
# clean.sh — Remove all build artifacts
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Cleaning build artifacts..."
rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo "✓ Clean complete"
