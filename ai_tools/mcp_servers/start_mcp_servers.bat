@echo off
echo ============================================================
echo Starting MCP Servers
echo ============================================================
echo.

REM Set Python path
set PYTHON_PATH=C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo Error: Python not found at %PYTHON_PATH%
    exit /b 1
)

echo Available MCP Servers:
echo 1. Chunk Server - Code chunking and analysis
echo 2. Index Server - Code indexing and search
echo 3. Vector Server - Vector storage and similarity search
echo 4. Edit Server - Code editing and refactoring
echo.

echo Select server to start (1-4) or 'a' for all:
set /p choice=

if "%choice%"=="1" goto chunk
if "%choice%"=="2" goto index
if "%choice%"=="3" goto vector
if "%choice%"=="4" goto edit
if "%choice%"=="a" goto all
if "%choice%"=="A" goto all

echo Invalid choice!
pause
exit /b 1

:chunk
echo Starting Chunk Server...
"%PYTHON_PATH%" chunk_server_fixed.py
goto end

:index
echo Starting Index Server...
"%PYTHON_PATH%" index_server_fixed.py
goto end

:vector
echo Starting Vector Server...
"%PYTHON_PATH%" vector_server_fixed.py
goto end

:edit
echo Starting Edit Server...
"%PYTHON_PATH%" edit_server_fixed.py
goto end

:all
echo Starting all servers in separate windows...
start "Chunk Server" cmd /k "%PYTHON_PATH%" chunk_server_fixed.py
start "Index Server" cmd /k "%PYTHON_PATH%" index_server_fixed.py
start "Vector Server" cmd /k "%PYTHON_PATH%" vector_server_fixed.py
start "Edit Server" cmd /k "%PYTHON_PATH%" edit_server_fixed.py
echo All servers started in separate windows!
goto end

:end
pause