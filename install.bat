@echo off
setlocal EnableExtensions
REM Keep this file ASCII-only + UTF-8 BOM so cmd.exe parses lines reliably on all locales.
chcp 65001 >nul 2>&1
cd /d "%~dp0"
echo === Installing dependencies ===
call "%~dp0scripts\_find_python.bat"
if not defined PY_CMD (
    echo.
    echo ERROR: Python not found.
    echo   Install Python 310 or newer from https://www.python.org/downloads/
    echo   Check "Add python.exe to PATH" or install the "py" launcher.
    echo.
    pause
    exit /b 1
)
echo Using: %PY_CMD%
%PY_CMD% "%~dp0scripts\install.py"
echo.
if errorlevel 1 (
    echo === Install failed ===
    pause
    exit /b 1
)
pause
endlocal
