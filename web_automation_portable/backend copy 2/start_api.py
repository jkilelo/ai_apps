#!/usr/bin/env python3
"""
Start script for Web Automation Portable Backend
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    # Ensure we're in the right directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    print("🚀 Starting Web Automation Portable Backend")
    print("=" * 60)
    print(f"Working directory: {backend_dir}")
    print("Available at: http://localhost:8001")
    print("API docs at: http://localhost:8001/docs")
    print("=" * 60)

    # Test imports first
    try:
        print("📦 Testing imports...")
        import data_types
        import browser
        import elements_extractor_no_llm
        import unified_web_automation_api
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)

    # Start the API server
    try:
        cmd = [sys.executable, "unified_web_automation_api.py"]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()