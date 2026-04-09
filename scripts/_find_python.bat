@echo off
REM UTF-8 BOM + ASCII. Sets PY_CMD in the caller when you use: CALL "%~dp0scripts\_find_python.bat"
REM Do not use SETLOCAL here or PY_CMD will not reach the parent batch file.
set "PY_CMD="
py -3 -c "import sys" >nul 2>&1 && set "PY_CMD=py -3" && goto :eof
python -c "import sys" >nul 2>&1 && set "PY_CMD=python" && goto :eof
python3 -c "import sys" >nul 2>&1 && set "PY_CMD=python3" && goto :eof
