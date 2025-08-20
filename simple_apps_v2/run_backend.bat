@echo off
REM Run the backend with proper event loop configuration for Python 3.13+

echo Starting Web Automation Backend...
echo ================================

REM Check if virtual environment exists
if exist "..\.venv\Scripts\python.exe" (
    echo Using virtual environment Python
    "..\.venv\Scripts\python.exe" run_backend.py %*
) else if exist "..\..\.venv\Scripts\python.exe" (
    echo Using virtual environment Python
    "..\..\.venv\Scripts\python.exe" run_backend.py %*
) else (
    echo Using system Python
    python run_backend.py %*
)

pause