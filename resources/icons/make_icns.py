#!/usr/bin/env python3
"""
Convert AppIcon.jpg to a proper macOS .icns file.
Run this from the project root after resources/icons/AppIcon.jpg exists.

Requirements: Pillow (pip install Pillow)

Usage:
    python resources/icons/make_icns.py
"""
import subprocess
import sys
from pathlib import Path

ICONS_DIR = Path(__file__).parent
JPG_SOURCE = ICONS_DIR / "AppIcon.jpg"
ICONSET_DIR = ICONS_DIR / "AppIcon.iconset"
ICNS_OUT = ICONS_DIR / "AppIcon.icns"

SIZES = [16, 32, 64, 128, 256, 512, 1024]


def main():
    try:
        from PIL import Image
    except ImportError:
        print("Installing Pillow...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "--quiet"])
        from PIL import Image

    ICONSET_DIR.mkdir(exist_ok=True)
    img = Image.open(JPG_SOURCE).convert("RGBA")

    for size in SIZES:
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(ICONSET_DIR / f"icon_{size}x{size}.png")
        if size <= 512:
            resized2 = img.resize((size * 2, size * 2), Image.LANCZOS)
            resized2.save(ICONSET_DIR / f"icon_{size}x{size}@2x.png")
        print(f"  Generated {size}x{size}")

    # Use iconutil to create .icns
    result = subprocess.run(
        ["iconutil", "-c", "icns", str(ICONSET_DIR), "-o", str(ICNS_OUT)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"✓ Created: {ICNS_OUT}")
    else:
        print(f"iconutil failed: {result.stderr}")
        print("Trying sips fallback...")
        # Try sips as fallback
        subprocess.run(
            ["sips", "-s", "format", "icns", str(JPG_SOURCE), "--out", str(ICNS_OUT)],
        )
        print(f"✓ Created (via sips): {ICNS_OUT}")


if __name__ == "__main__":
    main()
