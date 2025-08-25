@echo off
REM ============================================================
REM Web Automation Pipeline - Service Restarter
REM Senior DevOps Engineer Pattern: Graceful Service Restart
REM ============================================================

echo.
echo ============================================================
echo     Web Automation Pipeline - Service Restarter
echo ============================================================
echo.

REM Call stop script
echo [INFO] Stopping existing services...
call "%~dp0stop_web_automation.bat"

REM Wait a moment for ports to be released
echo.
echo [INFO] Waiting for ports to be released...
timeout /t 3 /nobreak >nul

REM Call start script
echo.
echo [INFO] Starting services...
call "%~dp0start_web_automation.bat"

exit /b %errorlevel%