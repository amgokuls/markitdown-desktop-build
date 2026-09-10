# Build script for MarkItDown Desktop (Windows)
$ErrorActionPreference = "Stop"

Write-Host "========================================"
Write-Host " Building MarkItDown Desktop for Windows"
Write-Host "========================================"

# Check if python is in PATH
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate venv and install requirements
Write-Host "Installing dependencies..."
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install pyinstaller pillow

# Clean old builds
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist\MarkItDown Desktop.exe") { Remove-Item -Force "dist\MarkItDown Desktop.exe" }

Write-Host "Running PyInstaller..."
# Build the standalone Windows executable (.exe)
.venv\Scripts\pyinstaller.exe `
    --noconfirm `
    --clean `
    --windowed `
    --name "MarkItDown Desktop" `
    --icon "resources\icons\AppIcon.ico" `
    --add-data "resources;resources" `
    --hidden-import "markitdown" `
    --hidden-import "PySide6.QtWebEngineCore" `
    app\main.py

Write-Host "========================================"
Write-Host "✓ Build successful!"
Write-Host "  Executable is located in: dist\MarkItDown Desktop\MarkItDown Desktop.exe"
Write-Host "========================================"
