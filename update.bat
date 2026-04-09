@echo off
setlocal EnableExtensions
REM Keep this file ASCII-only + UTF-8 BOM so cmd.exe parses lines reliably on all locales.
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo === git pull ===
git pull --ff-only
if errorlevel 1 (
    echo.
    echo git pull failed. Fix conflicts, or: git fetch origin ^&^& git reset --hard origin/main
    echo   (use origin/master if your default branch is master)
    echo.
    pause
    exit /b 1
)

echo.
echo === pip install (requirements.txt) ===
call "%~dp0scripts\_find_python.bat"
if not defined PY_CMD (
    echo ERROR: Python not found. Skipping pip.
    pause
    exit /b 1
)
%PY_CMD% "%~dp0scripts\install.py"
if errorlevel 1 (
    echo scripts\install.py failed
    pause
    exit /b 1
)

echo.
echo === Done. Run run.bat ===
pause
endlocal
