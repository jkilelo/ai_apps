@echo off
echo Setting up Simple Apps v2...
echo.

echo Installing Python dependencies...
cd ..\backend
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install Python dependencies
    exit /b 1
)

echo.
echo Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo Failed to install Playwright browsers
    exit /b 1
)

echo.
echo Installing Frontend dependencies...
cd ..\frontend
npm install
if errorlevel 1 (
    echo Failed to install Frontend dependencies
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo.
echo To run the application:
echo   1. Backend: cd backend && python -m uvicorn web_automation.main:app --reload
echo   2. Frontend: cd frontend && npm run dev
echo ========================================
cd ..