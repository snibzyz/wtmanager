@echo off
setlocal EnableExtensions
REM Keep this file ASCII-only + UTF-8 BOM so cmd.exe parses lines reliably on all locales.
chcp 65001 >nul 2>&1
cd /d "%~dp0"
call "%~dp0scripts\_find_python.bat"
if not defined PY_CMD (
    echo.
    echo ERROR: Python not found. Run install.bat after installing Python 3.10+.
    echo.
    pause
    exit /b 1
)
%PY_CMD% "%~dp0scripts\run.py"
if errorlevel 1 (
    echo.
    echo === ERROR: App crashed. Check output above. ===
    echo.
    pause
)
endlocal
