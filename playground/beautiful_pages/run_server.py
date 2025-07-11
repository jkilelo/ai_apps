#!/usr/bin/env python3
"""
Simple test server for the Real-time Console Streaming App
"""

import uvicorn
from realtime_console import app

if __name__ == "__main__":
    print("🚀 Starting Real-time Console Streaming Server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("🌐 Open your browser and navigate to the URL above")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
