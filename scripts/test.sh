#!/usr/bin/env bash
# test.sh — Run the test suite
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

cd "$PROJECT_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MarkItDown Desktop — Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Generate fixtures if not already done
if [[ ! -f "tests/fixtures/sample.html" ]]; then
    echo "Generating test fixtures..."
    python tests/fixtures/generate_fixtures.py
fi

# Run pytest with verbose output
python -m pytest tests/ \
    -v \
    --tb=short \
    --no-header \
    -p no:cacheprovider \
    "$@"
