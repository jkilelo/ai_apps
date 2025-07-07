#!/usr/bin/env python3
"""
Platform-agnostic server runner for AI Apps Suite
Works on Windows, macOS, and Linux
"""

import os
import sys
import platform
import asyncio
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import FastAPI app
from apps.ui_web_auto_testing.api.main import app


def get_server_config():
    """Get platform-appropriate server configuration"""
    config = {
        "host": os.getenv("FASTAPI_HOST", "0.0.0.0"),
        "port": int(os.getenv("FASTAPI_PORT", "8080")),
        "reload": os.getenv("ENVIRONMENT", "development") == "development",
        "log_level": "info"
    }
    
    # Platform-specific optimizations
    system = platform.system().lower()
    
    if system == "windows":
        # Windows-specific settings
        config["workers"] = 1  # Multi-worker not well supported on Windows
        print("🪟 Running on Windows - using single worker mode")
    else:
        # Unix-like systems (Linux, macOS)
        config["workers"] = os.cpu_count() or 1
        print(f"🐧 Running on {system.title()} - using {config['workers']} workers")
    
    return config


def main():
    """Main entry point"""
    import uvicorn
    
    config = get_server_config()
    
    print(f"""
╔═══════════════════════════════════════════╗
║        AI Apps Suite Server               ║
╠═══════════════════════════════════════════╣
║ Platform: {platform.system()} {platform.machine()}
║ Python:   {sys.version.split()[0]}
║ Host:     {config['host']}
║ Port:     {config['port']}
║ Mode:     {'Development' if config['reload'] else 'Production'}
╚═══════════════════════════════════════════╝
    """)
    
    try:
        # Check if we can use uvloop (Unix only)
        if platform.system() != "Windows":
            try:
                import uvloop
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                print("✅ Using uvloop for better performance")
            except ImportError:
                print("ℹ️  uvloop not available, using default event loop")
        else:
            print("ℹ️  Using Windows-compatible asyncio event loop")
        
        # Run the server
        uvicorn.run(
            "apps.ui_web_auto_testing.api.main:app",
            **config
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()