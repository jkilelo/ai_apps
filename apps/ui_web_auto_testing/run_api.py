#!/usr/bin/env python3
"""
Script to run the UI Web Auto Testing API server (Platform-agnostic)
"""

import sys
import os
import platform

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup platform-appropriate event loop
from utils.platform_utils import setup_event_loop
setup_event_loop()

if __name__ == "__main__":
    import uvicorn
    from apps.ui_web_auto_testing.api.main_platform_agnostic import app
    
    # Platform-specific configuration
    config = {
        "app": app,
        "host": "0.0.0.0",
        "port": 8002,
        "reload": True,
        "log_level": "info"
    }
    
    # Adjust for Windows
    if platform.system() == "Windows":
        config["loop"] = "asyncio"
        config["workers"] = 1
    else:
        # Try to use uvloop on Unix systems
        try:
            import uvloop
            config["loop"] = "uvloop"
        except ImportError:
            config["loop"] = "asyncio"
    
    uvicorn.run(**config)