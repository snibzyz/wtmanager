@echo off
setlocal EnableExtensions
REM Keep this file ASCII-only + UTF-8 BOM so cmd.exe parses lines reliably on all locales.
REM Builds a standalone dist\WTManager.exe with PyInstaller.
chcp 65001 >nul 2>&1
cd /d "%~dp0"
call "%~dp0scripts\_find_python.bat"
if not defined PY_CMD (
    echo.
    echo ERROR: Python not found. Install Python 3.10+ first.
    echo.
    pause
    exit /b 1
)
%PY_CMD% "%~dp0scripts\build_exe.py"
echo.
pause
endlocal
