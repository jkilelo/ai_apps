@echo off
REM Set UTF-8 encoding for Windows console and Python

REM Set console code page to UTF-8
chcp 65001 >nul 2>&1

REM Set Python UTF-8 environment variables
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PYTHONLEGACYWINDOWSFSENCODING=0
set PYTHONLEGACYWINDOWSSTDIO=0

REM Set locale environment variables
set LC_ALL=en_US.UTF-8
set LANG=en_US.UTF-8
set LANGUAGE=en_US.UTF-8

REM Set Windows-specific UTF-8 settings
set PYTHONUNBUFFERED=1

echo ===============================================
echo UTF-8 Environment Configuration
echo ===============================================
echo PYTHONIOENCODING=%PYTHONIOENCODING%
echo PYTHONUTF8=%PYTHONUTF8%
echo Console Code Page: 65001 (UTF-8)
echo ===============================================
echo.

REM Run the UTF-8 runner which will run the test
python run_with_utf8.py

pause