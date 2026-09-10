#!/usr/bin/env bash
# setup.sh — Create virtual environment and install all dependencies
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MarkItDown Desktop — Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_DIR"

# Check Python version
# PySide6 requires Python <= 3.13; prefer 3.12
PYTHON=$(command -v python3.12 || command -v python3.11 || command -v python3.10)
if [[ -z "$PYTHON" ]]; then
    echo "❌ Python 3.10–3.12 required (PySide6 not yet available for Python 3.14)"
    echo "   Install with: brew install python@3.12"
    exit 1
fi
PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python: $PYTHON ($PY_VERSION)"

if [[ "$PY_VERSION" < "3.10" ]]; then
    echo "❌ Python 3.10+ required (found $PY_VERSION)"
    exit 1
fi

# Create virtual environment
if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment at .venv ..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
echo "Virtual environment: $VIRTUAL_ENV"

# Upgrade pip/setuptools
pip install --quiet --upgrade pip setuptools wheel

# Install runtime + dev dependencies
echo "Installing dependencies (this may take a few minutes) ..."
pip install --quiet -r requirements/dev.txt

# Generate test fixtures
echo "Generating test fixtures ..."
python tests/fixtures/generate_fixtures.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the app:"
echo "  ./scripts/dev.sh"
echo ""
echo "To run tests:"
echo "  ./scripts/test.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
