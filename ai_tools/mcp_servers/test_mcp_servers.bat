@echo off
echo Testing MCP Servers Integration
echo ================================
echo.

set PYTHON="C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe"
set MCP_DIR=C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_tools\mcp_servers

echo [1] Testing Chunk Server...
%PYTHON% -c "import sys; sys.path.insert(0, r'%MCP_DIR%'); from chunk_server_fixed import ChunkServer; print('  ✓ Chunk Server imports successfully')"
if %errorlevel% neq 0 (
    echo   X Chunk Server failed to import
    exit /b 1
)

echo.
echo [2] Testing Index Server...
%PYTHON% -c "import sys; sys.path.insert(0, r'%MCP_DIR%'); from index_server_fixed import IndexServer; print('  ✓ Index Server imports successfully')"
if %errorlevel% neq 0 (
    echo   X Index Server failed to import
    exit /b 1
)

echo.
echo [3] Testing Vector Server...
%PYTHON% -c "import sys; sys.path.insert(0, r'%MCP_DIR%'); from vector_server_fixed import VectorServer; print('  ✓ Vector Server imports successfully')"
if %errorlevel% neq 0 (
    echo   X Vector Server failed to import
    exit /b 1
)

echo.
echo [4] Testing Edit Server...
%PYTHON% -c "import sys; sys.path.insert(0, r'%MCP_DIR%'); from edit_server_fixed import EditServer; print('  ✓ Edit Server imports successfully')"
if %errorlevel% neq 0 (
    echo   X Edit Server failed to import
    exit /b 1
)

echo.
echo ================================
echo All servers imported successfully!
echo.
echo MCP servers are configured in:
echo %APPDATA%\Claude\claude_desktop_config.json
echo.
echo To use the servers:
echo 1. Restart Claude Desktop
echo 2. The servers will be available as tools
echo.
pause