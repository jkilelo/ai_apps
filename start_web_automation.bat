@echo off
REM ============================================================
REM Web Automation Pipeline - Service Launcher
REM Senior DevOps Engineer Pattern: Idempotent Service Management
REM ============================================================

setlocal enabledelayedexpansion

REM Configuration
set BACKEND_PORT=5175
set FRONTEND_PORT=3000
set BACKEND_DIR=%~dp0simple_apps_v2\backend\web_automation
set FRONTEND_DIR=%~dp0simple_apps_original\frontend
set PYTHON_VENV=%~dp0.venv\Scripts\python.exe
set LOG_DIR=%~dp0logs
set BACKEND_LOG=%LOG_DIR%\backend.log
set FRONTEND_LOG=%LOG_DIR%\frontend.log

REM Colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

echo.
echo ============================================================
echo     Web Automation Pipeline - Service Manager
echo     Port 5175 (Backend) - Port 3000 (Frontend)
echo ============================================================
echo.

REM Create log directory if it doesn't exist
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
    echo %YELLOW%[INFO]%RESET% Created log directory: %LOG_DIR%
)

REM ============================================================
REM Check if Backend is running
REM ============================================================
echo %YELLOW%[CHECK]%RESET% Checking backend status on port %BACKEND_PORT%...

REM Check if port 5175 is in use
netstat -an | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    REM Port is in use, verify it's our backend
    curl -s -o nul -w "%%{http_code}" http://localhost:%BACKEND_PORT%/api/ui/health >temp_status.txt 2>nul
    set /p HTTP_STATUS=<temp_status.txt
    del temp_status.txt >nul 2>&1
    
    if "!HTTP_STATUS!"=="200" (
        echo %GREEN%[OK]%RESET% Backend is already running on port %BACKEND_PORT%
        set BACKEND_RUNNING=1
    ) else (
        echo %RED%[ERROR]%RESET% Port %BACKEND_PORT% is in use but backend is not responding
        echo         Please stop the conflicting service or change the port
        set BACKEND_RUNNING=0
        goto :check_frontend
    )
) else (
    echo %YELLOW%[INFO]%RESET% Backend is not running
    set BACKEND_RUNNING=0
)

:check_frontend
REM ============================================================
REM Check if Frontend is running
REM ============================================================
echo %YELLOW%[CHECK]%RESET% Checking frontend status on port %FRONTEND_PORT%...

REM Check if port 3000 is in use
netstat -an | findstr ":%FRONTEND_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    REM Port is in use, verify it's our frontend
    curl -s -o nul -w "%%{http_code}" http://localhost:%FRONTEND_PORT% >temp_status.txt 2>nul
    set /p HTTP_STATUS=<temp_status.txt
    del temp_status.txt >nul 2>&1
    
    if "!HTTP_STATUS!"=="200" (
        echo %GREEN%[OK]%RESET% Frontend is already running on port %FRONTEND_PORT%
        set FRONTEND_RUNNING=1
    ) else (
        echo %RED%[ERROR]%RESET% Port %FRONTEND_PORT% is in use but frontend is not responding
        echo         Please stop the conflicting service or change the port
        set FRONTEND_RUNNING=0
    )
) else (
    echo %YELLOW%[INFO]%RESET% Frontend is not running
    set FRONTEND_RUNNING=0
)

REM ============================================================
REM Start Backend if not running
REM ============================================================
if %BACKEND_RUNNING% equ 0 (
    echo.
    echo %YELLOW%[START]%RESET% Starting backend server...
    
    REM Check if Python venv exists
    if not exist "%PYTHON_VENV%" (
        echo %RED%[ERROR]%RESET% Python virtual environment not found at %PYTHON_VENV%
        echo         Please create it first: python -m venv .venv
        goto :error_exit
    )
    
    REM Check if startup.py exists
    if not exist "%BACKEND_DIR%\startup.py" (
        echo %RED%[ERROR]%RESET% Backend startup.py not found at %BACKEND_DIR%
        goto :error_exit
    )
    
    REM Start backend in a new window
    echo %YELLOW%[INFO]%RESET% Launching backend in new window...
    start "Web Automation Backend" /D "%BACKEND_DIR%" cmd /k "%PYTHON_VENV% startup.py 2>&1 | tee %BACKEND_LOG%"
    
    REM Wait for backend to be ready
    echo %YELLOW%[WAIT]%RESET% Waiting for backend to start...
    set RETRIES=30
    :wait_backend
    timeout /t 2 /nobreak >nul
    curl -s http://localhost:%BACKEND_PORT%/api/ui/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo %GREEN%[OK]%RESET% Backend started successfully
    ) else (
        set /a RETRIES-=1
        if !RETRIES! gtr 0 (
            echo %YELLOW%[WAIT]%RESET% Still waiting... (!RETRIES! attempts left)
            goto :wait_backend
        ) else (
            echo %RED%[ERROR]%RESET% Backend failed to start after 60 seconds
            echo         Check the log at: %BACKEND_LOG%
            goto :error_exit
        )
    )
)

REM ============================================================
REM Start Frontend if not running
REM ============================================================
if %FRONTEND_RUNNING% equ 0 (
    echo.
    echo %YELLOW%[START]%RESET% Starting frontend server...
    
    REM Check if frontend directory exists
    if not exist "%FRONTEND_DIR%" (
        echo %RED%[ERROR]%RESET% Frontend directory not found at %FRONTEND_DIR%
        goto :error_exit
    )
    
    REM Check if node_modules exists
    if not exist "%FRONTEND_DIR%\node_modules" (
        echo %YELLOW%[INFO]%RESET% Installing frontend dependencies...
        cd /d "%FRONTEND_DIR%"
        call npm install
        if %errorlevel% neq 0 (
            echo %RED%[ERROR]%RESET% Failed to install frontend dependencies
            goto :error_exit
        )
    )
    
    REM Start frontend in a new window
    echo %YELLOW%[INFO]%RESET% Launching frontend in new window...
    start "Web Automation Frontend" /D "%FRONTEND_DIR%" cmd /k "npm run dev 2>&1 | tee %FRONTEND_LOG%"
    
    REM Wait for frontend to be ready
    echo %YELLOW%[WAIT]%RESET% Waiting for frontend to start...
    set RETRIES=30
    :wait_frontend
    timeout /t 2 /nobreak >nul
    curl -s http://localhost:%FRONTEND_PORT% >nul 2>&1
    if %errorlevel% equ 0 (
        echo %GREEN%[OK]%RESET% Frontend started successfully
    ) else (
        set /a RETRIES-=1
        if !RETRIES! gtr 0 (
            echo %YELLOW%[WAIT]%RESET% Still waiting... (!RETRIES! attempts left)
            goto :wait_frontend
        ) else (
            echo %RED%[ERROR]%RESET% Frontend failed to start after 60 seconds
            echo         Check the log at: %FRONTEND_LOG%
            goto :error_exit
        )
    )
)

REM ============================================================
REM Success - Services are running
REM ============================================================
echo.
echo ============================================================
echo %GREEN%[SUCCESS]%RESET% Web Automation Pipeline is ready!
echo ============================================================
echo.
echo   Backend:  http://localhost:%BACKEND_PORT%/api/ui/health
echo   Frontend: http://localhost:%FRONTEND_PORT%
echo   API Docs: http://localhost:%BACKEND_PORT%/docs
echo.
echo   Logs:
echo     Backend:  %BACKEND_LOG%
echo     Frontend: %FRONTEND_LOG%
echo.
echo %YELLOW%[TIP]%RESET% To stop services, close the console windows or use:
echo       stop_web_automation.bat
echo.

REM Open browser if both services are running
if %BACKEND_RUNNING% equ 1 if %FRONTEND_RUNNING% equ 1 (
    echo %YELLOW%[INFO]%RESET% Both services already running, skipping browser launch
) else (
    echo %YELLOW%[INFO]%RESET% Opening browser in 5 seconds...
    timeout /t 5 /nobreak >nul
    start http://localhost:%FRONTEND_PORT%/flows/web-automation
)

goto :end

:error_exit
echo.
echo %RED%[ERROR]%RESET% Failed to start services
echo         Please check the error messages above
exit /b 1

:end
echo Press any key to exit...
pause >nul
exit /b 0