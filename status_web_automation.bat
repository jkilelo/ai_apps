@echo off
REM ============================================================
REM Web Automation Pipeline - Service Status Checker
REM Senior DevOps Engineer Pattern: Service Health Monitoring
REM ============================================================

setlocal enabledelayedexpansion

REM Configuration
set BACKEND_PORT=5175
set FRONTEND_PORT=3000
set BACKEND_URL=http://localhost:%BACKEND_PORT%/api/ui/health
set FRONTEND_URL=http://localhost:%FRONTEND_PORT%

REM Colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

echo.
echo ============================================================
echo     Web Automation Pipeline - Service Status
echo     %date% %time%
echo ============================================================
echo.

REM ============================================================
REM Check Backend Status
REM ============================================================
echo %CYAN%[BACKEND SERVICE]%RESET%
echo -----------------

REM Check if port is listening
netstat -an | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Port:       %GREEN%LISTENING%RESET% on %BACKEND_PORT%
    
    REM Find PID
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
        set PID=%%a
        goto :got_backend_pid
    )
    :got_backend_pid
    echo   Process ID: !PID!
    
    REM Get process details
    for /f "tokens=1,2" %%a in ('tasklist /fi "PID eq !PID!" ^| findstr "!PID!"') do (
        echo   Process:    %%a
    )
    
    REM Check API health
    echo   Health Check:
    curl -s %BACKEND_URL% >temp_health.json 2>nul
    if %errorlevel% equ 0 (
        echo   API Status: %GREEN%HEALTHY%RESET%
        
        REM Parse JSON response (basic parsing)
        for /f "delims=" %%a in (temp_health.json) do (
            set HEALTH_RESPONSE=%%a
            echo   Response:   !HEALTH_RESPONSE:~0,60!...
        )
        del temp_health.json >nul 2>&1
    ) else (
        echo   API Status: %RED%NOT RESPONDING%RESET%
    )
    
    REM Check endpoints
    echo.
    echo   Endpoints:
    curl -s -o nul -w "    /element_extraction: %%{http_code}\n" http://localhost:%BACKEND_PORT%/api/ui/element_extraction 2>nul
    curl -s -o nul -w "    /test_generation:    %%{http_code}\n" http://localhost:%BACKEND_PORT%/api/ui/test_generation 2>nul
    curl -s -o nul -w "    /code_generation:    %%{http_code}\n" http://localhost:%BACKEND_PORT%/api/ui/code_generation 2>nul
    curl -s -o nul -w "    /code_execution:     %%{http_code}\n" http://localhost:%BACKEND_PORT%/api/ui/code_execution 2>nul
    
) else (
    echo   Port:       %RED%NOT LISTENING%RESET%
    echo   Status:     %RED%OFFLINE%RESET%
)

echo.
REM ============================================================
REM Check Frontend Status
REM ============================================================
echo %CYAN%[FRONTEND SERVICE]%RESET%
echo ------------------

REM Check if port is listening
netstat -an | findstr ":%FRONTEND_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Port:       %GREEN%LISTENING%RESET% on %FRONTEND_PORT%
    
    REM Find PID
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
        set PID=%%a
        goto :got_frontend_pid
    )
    :got_frontend_pid
    echo   Process ID: !PID!
    
    REM Get process details
    for /f "tokens=1,2" %%a in ('tasklist /fi "PID eq !PID!" ^| findstr "!PID!"') do (
        echo   Process:    %%a
    )
    
    REM Check HTTP response
    curl -s -o nul -w "" %FRONTEND_URL% 2>nul
    if %errorlevel% equ 0 (
        echo   Web Status: %GREEN%ACCESSIBLE%RESET%
        
        REM Get response code
        curl -s -o nul -w "  HTTP Code:  %%{http_code}\n" %FRONTEND_URL% 2>nul
    ) else (
        echo   Web Status: %RED%NOT RESPONDING%RESET%
    )
    
    echo   URL:        %FRONTEND_URL%
    
) else (
    echo   Port:       %RED%NOT LISTENING%RESET%
    echo   Status:     %RED%OFFLINE%RESET%
)

echo.
REM ============================================================
REM Check System Resources
REM ============================================================
echo %CYAN%[SYSTEM RESOURCES]%RESET%
echo ------------------

REM Get memory usage
for /f "skip=1" %%a in ('wmic os get TotalVisibleMemorySize') do (
    set /a TOTAL_MEM=%%a/1024 2>nul
    if !TOTAL_MEM! gtr 0 goto :got_total_mem
)
:got_total_mem

for /f "skip=1" %%a in ('wmic os get FreePhysicalMemory') do (
    set /a FREE_MEM=%%a/1024 2>nul
    if !FREE_MEM! gtr 0 goto :got_free_mem
)
:got_free_mem

if defined TOTAL_MEM if defined FREE_MEM (
    set /a USED_MEM=TOTAL_MEM-FREE_MEM
    set /a MEM_PERCENT=USED_MEM*100/TOTAL_MEM
    echo   Memory:     !USED_MEM! MB / !TOTAL_MEM! MB (!MEM_PERCENT!%% used^)
)

REM Count Node.js processes
set NODE_COUNT=0
for /f %%a in ('tasklist ^| findstr /i "node.exe" ^| find /c "node.exe"') do set NODE_COUNT=%%a
echo   Node.js:    !NODE_COUNT! process(es^)

REM Count Python processes
set PYTHON_COUNT=0
for /f %%a in ('tasklist ^| findstr /i "python.exe" ^| find /c "python.exe"') do set PYTHON_COUNT=%%a
echo   Python:     !PYTHON_COUNT! process(es^)

echo.
REM ============================================================
REM Overall Status
REM ============================================================
echo %CYAN%[OVERALL STATUS]%RESET%
echo ----------------

set BACKEND_OK=0
set FRONTEND_OK=0

REM Check backend health
curl -s http://localhost:%BACKEND_PORT%/api/ui/health >nul 2>&1
if %errorlevel% equ 0 set BACKEND_OK=1

REM Check frontend health
curl -s http://localhost:%FRONTEND_PORT% >nul 2>&1
if %errorlevel% equ 0 set FRONTEND_OK=1

if %BACKEND_OK% equ 1 if %FRONTEND_OK% equ 1 (
    echo   System:     %GREEN%FULLY OPERATIONAL%RESET%
    echo.
    echo   %GREEN%Ready to use at:%RESET%
    echo     http://localhost:%FRONTEND_PORT%/flows/web-automation
) else if %BACKEND_OK% equ 1 (
    echo   System:     %YELLOW%PARTIALLY OPERATIONAL%RESET%
    echo   Backend:    %GREEN%ONLINE%RESET%
    echo   Frontend:   %RED%OFFLINE%RESET%
    echo.
    echo   %YELLOW%Start frontend with: start_web_automation.bat%RESET%
) else if %FRONTEND_OK% equ 1 (
    echo   System:     %YELLOW%PARTIALLY OPERATIONAL%RESET%
    echo   Backend:    %RED%OFFLINE%RESET%
    echo   Frontend:   %GREEN%ONLINE%RESET%
    echo.
    echo   %YELLOW%Start backend with: start_web_automation.bat%RESET%
) else (
    echo   System:     %RED%OFFLINE%RESET%
    echo.
    echo   %YELLOW%Start services with: start_web_automation.bat%RESET%
)

echo.
echo ============================================================
echo.

REM Auto-refresh option
choice /c YN /t 5 /d N /m "Auto-refresh status in 5 seconds"
if %errorlevel% equ 1 (
    cls
    goto :start
)

:start
exit /b 0