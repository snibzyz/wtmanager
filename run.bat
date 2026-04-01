@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
python run.py
if errorlevel 1 (
    echo.
    echo === ERROR: App crashed. Check output above. ===
    echo.
    pause
)
