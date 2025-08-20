#!/usr/bin/env python
"""
Backend Runner with Proper Event Loop Configuration
====================================================
This script ensures the correct event loop policy is set BEFORE
uvicorn starts, which is critical for Python 3.13+ on Windows.
"""

import sys
import asyncio
import platform
from pathlib import Path

# CRITICAL: Set event loop policy BEFORE any async operations
if sys.platform == 'win32':
    # Windows requires ProactorEventLoop for subprocess operations
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print(f"Set Windows ProactorEventLoop policy for Python {sys.version_info.major}.{sys.version_info.minor}")

# Add simple_apps_v2 to path
simple_apps_v2_root = Path(__file__).parent
sys.path.insert(0, str(simple_apps_v2_root))

# Now import uvicorn AFTER setting the event loop policy
import uvicorn

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the backend with proper event loop configuration")
    parser.add_argument("--port", type=int, default=5175, help="Port to run the server on")
    parser.add_argument("--host", default="localhost", help="Host to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()
    
    # Run the backend
    uvicorn.run(
        "backend.web_automation.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )