#!/usr/bin/env python3
"""
Script to run the UI Web Auto Testing API server
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if __name__ == "__main__":
    import uvicorn
    from apps.ui_web_auto_testing.api.main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )