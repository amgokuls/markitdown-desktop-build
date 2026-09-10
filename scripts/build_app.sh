#!/usr/bin/env bash
# build_app.sh — Build the standalone macOS .app using PyInstaller
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"
DIST_DIR="$PROJECT_DIR/dist"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MarkItDown Desktop — Build .app"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

# Install build dependencies
echo "Installing build dependencies..."
pip install --quiet -r requirements/build.txt

# Clean previous build
rm -rf build/ dist/

echo "Running PyInstaller..."
pyinstaller packaging/markitdown_desktop.spec \
    --noconfirm \
    --clean

APP_PATH="$DIST_DIR/MarkItDown Desktop.app"

if [[ -d "$APP_PATH" ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✓ Build successful!"
    echo "  App: $APP_PATH"
    echo ""
    echo "To run the app:"
    echo "  open \"$APP_PATH\""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "❌ Build failed — app not found at expected path"
    exit 1
fi

# Optional code signing (if credentials are available)
if [[ -n "${APPLE_SIGNING_IDENTITY:-}" ]]; then
    echo "Code signing with identity: $APPLE_SIGNING_IDENTITY"
    codesign \
        --deep \
        --force \
        --options runtime \
        --sign "$APPLE_SIGNING_IDENTITY" \
        "$APP_PATH"
    echo "✓ Code signing complete"
else
    echo ""
    echo "⚠  Unsigned build — set APPLE_SIGNING_IDENTITY to sign"
    echo "   Users may see Gatekeeper warnings on first launch."
    echo "   Right-click → Open to bypass Gatekeeper for unsigned builds."
fi
