#!/usr/bin/env python
"""
Standalone runner for simple_apps_v2
This script ensures all dependencies are properly configured for standalone operation
"""

import sys
import os
from pathlib import Path

# Add simple_apps_v2 root to Python path
SIMPLE_APPS_V2_ROOT = Path(__file__).parent
sys.path.insert(0, str(SIMPLE_APPS_V2_ROOT))

# Set environment variables if needed
os.environ.setdefault("PYTHONPATH", str(SIMPLE_APPS_V2_ROOT))

def run_backend():
    """Run the backend server"""
    import uvicorn
    from backend.web_automation.main import app
    
    print(f"Starting standalone backend server...")
    print(f"Project root: {SIMPLE_APPS_V2_ROOT}")
    print(f"Python path: {sys.path[0]}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5175,
        reload=False,
        log_level="info"
    )

def run_frontend():
    """Run the frontend development server"""
    import subprocess
    
    frontend_dir = SIMPLE_APPS_V2_ROOT / "frontend"
    print(f"Starting frontend from: {frontend_dir}")
    
    # Change to frontend directory and run npm
    os.chdir(frontend_dir)
    subprocess.run(["npm", "run", "dev"])

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run simple_apps_v2 standalone")
    parser.add_argument(
        "--service",
        choices=["backend", "frontend", "both"],
        default="backend",
        help="Which service to run"
    )
    
    args = parser.parse_args()
    
    if args.service == "backend":
        run_backend()
    elif args.service == "frontend":
        run_frontend()
    else:
        # Run both (would need threading or subprocess)
        print("To run both services, please open two terminals:")
        print(f"Terminal 1: python {__file__} --service backend")
        print(f"Terminal 2: python {__file__} --service frontend")

if __name__ == "__main__":
    main()