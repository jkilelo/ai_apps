#!/usr/bin/env python3
"""
Simple HTTP Server for Baseline Testing
========================================
Serves the test HTML page on localhost:8888
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8888
HOST = "localhost"

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve from the test_baseline directory"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)
    
    def log_message(self, format, *args):
        """Custom logging with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")
    
    def do_POST(self):
        """Handle POST requests for form submission"""
        if self.path == "/submit":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print(f"[FORM SUBMISSION] Received POST data: {post_data.decode('utf-8')}")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success", "message": "Form received"}')
        else:
            self.send_error(404)

def start_server():
    """Start the HTTP server"""
    print("=" * 60)
    print("BASELINE TEST SERVER")
    print("=" * 60)
    print(f"Starting server at http://{HOST}:{PORT}")
    print(f"Serving directory: {SCRIPT_DIR}")
    print(f"Test page: http://{HOST}:{PORT}/index.html")
    print("-" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Server failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure index.html exists
    index_file = SCRIPT_DIR / "index.html"
    if not index_file.exists():
        print(f"[ERROR] index.html not found in {SCRIPT_DIR}")
        sys.exit(1)
    
    start_server()