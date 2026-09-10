#!/usr/bin/env bash
# dev.sh — Run the application from source
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
echo "Starting MarkItDown Desktop (development mode)..."
python -m app.main
