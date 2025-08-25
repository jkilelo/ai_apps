@echo off
REM ============================================================
REM Web Automation Pipeline - Service Stopper
REM Senior DevOps Engineer Pattern: Graceful Service Shutdown
REM ============================================================

setlocal enabledelayedexpansion

REM Configuration
set BACKEND_PORT=5175
set FRONTEND_PORT=3000

REM Colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

echo.
echo ============================================================
echo     Web Automation Pipeline - Service Stopper
echo ============================================================
echo.

REM ============================================================
REM Stop Backend Service
REM ============================================================
echo %YELLOW%[CHECK]%RESET% Looking for backend process on port %BACKEND_PORT%...

REM Find PID using the port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    set PID=%%a
    goto :found_backend
)

echo %YELLOW%[INFO]%RESET% No backend process found on port %BACKEND_PORT%
goto :check_frontend

:found_backend
echo %YELLOW%[INFO]%RESET% Found backend process with PID: !PID!

REM Get process name
for /f "tokens=1" %%a in ('tasklist /fi "PID eq !PID!" ^| findstr "!PID!"') do (
    set PROCESS_NAME=%%a
)

if "!PROCESS_NAME!"=="python.exe" (
    echo %YELLOW%[STOP]%RESET% Stopping backend process...
    taskkill /PID !PID! /F >nul 2>&1
    if %errorlevel% equ 0 (
        echo %GREEN%[OK]%RESET% Backend stopped successfully
    ) else (
        echo %RED%[ERROR]%RESET% Failed to stop backend process
    )
) else (
    echo %YELLOW%[SKIP]%RESET% Process is not Python, skipping (might be another service)
)

:check_frontend
REM ============================================================
REM Stop Frontend Service
REM ============================================================
echo.
echo %YELLOW%[CHECK]%RESET% Looking for frontend process on port %FRONTEND_PORT%...

REM Find PID using the port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    set PID=%%a
    goto :found_frontend
)

echo %YELLOW%[INFO]%RESET% No frontend process found on port %FRONTEND_PORT%
goto :check_windows

:found_frontend
echo %YELLOW%[INFO]%RESET% Found frontend process with PID: !PID!

REM Get process name
for /f "tokens=1" %%a in ('tasklist /fi "PID eq !PID!" ^| findstr "!PID!"') do (
    set PROCESS_NAME=%%a
)

if "!PROCESS_NAME!"=="node.exe" (
    echo %YELLOW%[STOP]%RESET% Stopping frontend process...
    taskkill /PID !PID! /F >nul 2>&1
    if %errorlevel% equ 0 (
        echo %GREEN%[OK]%RESET% Frontend stopped successfully
    ) else (
        echo %RED%[ERROR]%RESET% Failed to stop frontend process
    )
) else (
    echo %YELLOW%[SKIP]%RESET% Process is not Node.js, skipping (might be another service)
)

:check_windows
REM ============================================================
REM Close console windows
REM ============================================================
echo.
echo %YELLOW%[CHECK]%RESET% Looking for console windows...

REM Try to close windows by title
taskkill /FI "WINDOWTITLE eq Web Automation Backend*" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[OK]%RESET% Closed backend console window
)

taskkill /FI "WINDOWTITLE eq Web Automation Frontend*" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[OK]%RESET% Closed frontend console window
)

REM ============================================================
REM Verify services are stopped
REM ============================================================
echo.
echo %YELLOW%[VERIFY]%RESET% Verifying services are stopped...

set ALL_STOPPED=1

REM Check backend
netstat -an | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo %YELLOW%[WARNING]%RESET% Port %BACKEND_PORT% is still in use
    set ALL_STOPPED=0
) else (
    echo %GREEN%[OK]%RESET% Backend port %BACKEND_PORT% is free
)

REM Check frontend
netstat -an | findstr ":%FRONTEND_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo %YELLOW%[WARNING]%RESET% Port %FRONTEND_PORT% is still in use
    set ALL_STOPPED=0
) else (
    echo %GREEN%[OK]%RESET% Frontend port %FRONTEND_PORT% is free
)

REM ============================================================
REM Summary
REM ============================================================
echo.
echo ============================================================
if %ALL_STOPPED% equ 1 (
    echo %GREEN%[SUCCESS]%RESET% All services stopped successfully
) else (
    echo %YELLOW%[WARNING]%RESET% Some ports are still in use
    echo         They might be used by other applications
)
echo ============================================================
echo.

echo Press any key to exit...
pause >nul
exit /b 0