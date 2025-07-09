@echo off
REM Cross-platform runner script for AI Apps Suite (Windows)

echo Starting AI Apps Suite...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Display Python version
echo Python version:
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements_platform_agnostic.txt

REM Install Playwright browsers if needed
echo Setting up Playwright...
playwright install chromium 2>nul || echo Playwright browsers already installed

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%cd%
if not defined ENVIRONMENT set ENVIRONMENT=development

REM Build frontend if needed
if exist "src" if exist "package.json" (
    if not exist "dist" (
        echo Building frontend...
        where npm >nul 2>&1
        if %errorlevel% equ 0 (
            call npm install
            call npm run build
        ) else (
            echo WARNING: npm not found. Skipping frontend build.
            echo Install Node.js to build the frontend.
        )
    )
)

REM Run the server
echo Starting server...
python run.py

pause