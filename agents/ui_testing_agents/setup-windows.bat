@echo off
REM V2 LLM-Native System - Windows Setup Script
REM ============================================

echo ======================================================================
echo V2 LLM-NATIVE SYSTEM - WINDOWS SETUP
echo ======================================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python is installed

REM Create virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo [INFO] Installing requirements...
pip install -r requirements.txt

REM Install Playwright browsers
echo [INFO] Installing Playwright browsers...
playwright install chromium

REM Setup .env file
if not exist ".env" (
    if exist ".env.template" (
        echo [INFO] Creating .env file from template...
        copy .env.template .env
        echo.
        echo ======================================================================
        echo IMPORTANT: Edit .env file and add your API keys
        echo You need at least ONE of:
        echo   - OpenAI API Key
        echo   - Anthropic API Key
        echo   - Google API Key
        echo ======================================================================
        echo.
        echo Opening .env file in notepad...
        notepad .env
    )
) else (
    echo [INFO] .env file already exists
)

echo.
echo ======================================================================
echo SETUP COMPLETE!
echo ======================================================================
echo.
echo To use the Enterprise Test Automation Framework:
echo   1. Ensure .env has your API keys
echo   2. Run: venv\Scripts\activate
echo   3. Run: python test_automation_framework\sample_implementations\quick_start_demo.py
echo.
echo ======================================================================

pause