@echo off
REM Set Python to use UTF-8 encoding globally on Windows

REM Force Python to use UTF-8 for stdout/stderr
set PYTHONIOENCODING=utf-8

REM Enable UTF-8 mode in Python (Python 3.7+)
set PYTHONUTF8=1

REM Set Windows console to UTF-8
chcp 65001 > nul

echo UTF-8 encoding has been set for this session.
echo.
echo To make these settings permanent, add these environment variables to your system:
echo   PYTHONIOENCODING=utf-8
echo   PYTHONUTF8=1
echo.
echo Running Python with UTF-8 encoding...

REM Run the main.py script with UTF-8 encoding
python main.py %*