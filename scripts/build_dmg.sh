#!/usr/bin/env bash
# build_dmg.sh — Create a professional .dmg installer from the built .app
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_DIR/dist"
APP_NAME="MarkItDown Desktop"
APP_PATH="$DIST_DIR/$APP_NAME.app"
DMG_PATH="$DIST_DIR/MarkItDown-Desktop.dmg"
DMG_STAGING="$DIST_DIR/dmg_staging"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MarkItDown Desktop — Build .dmg"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ ! -d "$APP_PATH" ]]; then
    echo "❌ App not found at: $APP_PATH"
    echo "   Run ./scripts/build_app.sh first."
    exit 1
fi

# Remove old DMG
rm -f "$DMG_PATH"
rm -rf "$DMG_STAGING"

# Check for create-dmg (preferred) or hdiutil
if command -v create-dmg &>/dev/null; then
    echo "Building DMG with create-dmg..."
    
    create-dmg \
        --volname "$APP_NAME" \
        --volicon "$PROJECT_DIR/resources/icons/AppIcon.icns" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "$APP_NAME.app" 150 185 \
        --hide-extension "$APP_NAME.app" \
        --app-drop-link 450 185 \
        --no-internet-enable \
        "$DMG_PATH" \
        "$APP_PATH" || true
        
    # create-dmg may exit non-zero on some configs but still produce the DMG
    if [[ -f "$DMG_PATH" ]]; then
        echo "✓ DMG created with create-dmg"
    else
        echo "create-dmg failed, falling back to hdiutil..."
        _build_with_hdiutil
    fi
else
    echo "create-dmg not found (install with: brew install create-dmg)"
    echo "Falling back to hdiutil..."
    _build_with_hdiutil() {
        mkdir -p "$DMG_STAGING"
        cp -R "$APP_PATH" "$DMG_STAGING/"
        ln -s /Applications "$DMG_STAGING/Applications"
        hdiutil create \
            -volname "$APP_NAME" \
            -srcfolder "$DMG_STAGING" \
            -ov \
            -format UDZO \
            "$DMG_PATH"
        rm -rf "$DMG_STAGING"
    }
    _build_with_hdiutil
fi

if [[ -f "$DMG_PATH" ]]; then
    SIZE=$(du -sh "$DMG_PATH" | cut -f1)
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✓ DMG created: $DMG_PATH ($SIZE)"
    echo ""
    echo "To mount and verify:"
    echo "  open \"$DMG_PATH\""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Optional notarization
    if [[ -n "${APPLE_ID:-}" && -n "${APPLE_APP_PASSWORD:-}" && -n "${APPLE_TEAM_ID:-}" ]]; then
        echo "Notarizing DMG..."
        xcrun notarytool submit "$DMG_PATH" \
            --apple-id "$APPLE_ID" \
            --password "$APPLE_APP_PASSWORD" \
            --team-id "$APPLE_TEAM_ID" \
            --wait
        echo "Stapling notarization ticket..."
        xcrun stapler staple "$DMG_PATH"
        echo "✓ Notarization complete"
    else
        echo "⚠  Skipping notarization — set APPLE_ID, APPLE_APP_PASSWORD, APPLE_TEAM_ID to notarize"
    fi
else
    echo "❌ DMG creation failed"
    exit 1
fi
