@echo off
echo ========================================
echo Setting up simple_apps_v2 Standalone
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo [1/4] Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install Python dependencies
    exit /b 1
)

echo [4/4] Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo Error: Failed to install Playwright browsers
    exit /b 1
)

echo.
echo ========================================
echo Backend setup complete!
echo ========================================
echo.

REM Setup frontend
cd frontend
echo Setting up frontend...
echo.

echo [1/2] Installing npm dependencies...
npm install
if errorlevel 1 (
    echo Error: Failed to install npm dependencies
    cd ..
    exit /b 1
)

echo [2/2] Building frontend assets...
npm run build
if errorlevel 1 (
    echo Warning: Build failed, but dev server should still work
)

cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application:
echo.
echo Backend:
echo   venv\Scripts\activate
echo   python run_standalone.py --service backend
echo.
echo Frontend (in new terminal):
echo   cd frontend
echo   npm run dev
echo.
echo Or use the provided run scripts:
echo   run_backend_standalone.bat
echo   run_frontend_standalone.bat
echo.
pause