@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv" (
    echo Venv not found. Run setup.bat first.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
streamlit run app.py --server.headless false --server.port 8501