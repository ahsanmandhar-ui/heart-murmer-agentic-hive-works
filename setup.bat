@echo off
setlocal
cd /d "%~dp0"
echo === Heart Murmur PC Setup ===

where python >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

python download_model.py
if errorlevel 1 (
    echo Model check failed.
    pause
    exit /b 1
)

echo.
echo Setup complete. Run run.bat to start the app.
pause