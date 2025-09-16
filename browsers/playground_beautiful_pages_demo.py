#!/usr/bin/env python3
"""
Demo script for the Real-time Console Streaming App
This script shows how to run the application and demonstrates its features.
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Please run: pip install -r requirements.txt")
        return False

def start_server():
    """Start the FastAPI server"""
    try:
        import realtime_console
        import uvicorn
        
        print("🚀 Starting Real-time Console Streaming Server...")
        print("📍 Server URL: http://localhost:8001")
        print("🔧 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the server
        uvicorn.run(
            realtime_console.app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def open_browser():
    """Open browser after a delay"""
    time.sleep(2)  # Wait for server to start
    try:
        webbrowser.open("http://localhost:8001")
        print("🌐 Opening browser...")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("📍 Please manually open: http://localhost:8001")

def main():
    """Main demo function"""
    print("🎯 Real-time Python Console Streaming Demo")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check if we're in the right directory
    required_files = ["realtime_console.py", "requirements.txt", "static", "templates"]
    missing_files = [f for f in required_files if not (current_dir / f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("💡 Please run this script from the beautiful_pages directory")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start the server (this will block)
    start_server()

if __name__ == "__main__":
    main()
