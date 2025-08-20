@echo off
echo Starting simple_apps_v2 Backend (Standalone)...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Run setup_standalone.bat first.
    echo Attempting to run with system Python...
)

REM Run the backend
python run_standalone.py --service backend

pause