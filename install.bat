@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
echo === Installing dependencies ===
python install.py
echo.
pause
