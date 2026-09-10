@echo off
setlocal

echo ========================================
echo  Building MarkItDown Desktop for Windows
echo ========================================

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    exit /b 1
)

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Installing dependencies...
call .venv\Scripts\python.exe -m pip install -r requirements.txt
call .venv\Scripts\python.exe -m pip install pyinstaller pillow

if exist "build" rmdir /s /q "build"

echo Running PyInstaller...
call .venv\Scripts\pyinstaller.exe ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "MarkItDown Desktop" ^
    --icon "resources\icons\AppIcon.ico" ^
    --add-data "resources;resources" ^
    --hidden-import "markitdown" ^
    --hidden-import "PySide6.QtWebEngineCore" ^
    app\main.py

echo ========================================
echo ✓ Build successful!
echo   Executable is located in: dist\MarkItDown Desktop\MarkItDown Desktop.exe
echo ========================================
