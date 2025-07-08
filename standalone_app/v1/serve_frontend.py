#!/usr/bin/env python3
import http.server
import socketserver
import os
import urllib.request
import json

PORT = 8005
BACKEND_URL = "http://localhost:8004"

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend/build", **kwargs)
    
    def do_GET(self):
        if self.path.startswith('/api'):
            self.proxy_request()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api'):
            self.proxy_request()
        else:
            self.send_error(404)
    
    def proxy_request(self):
        # Read request body if POST
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        # Create backend request
        url = BACKEND_URL + self.path
        req = urllib.request.Request(url, data=body, method=self.command)
        
        # Copy headers
        for header, value in self.headers.items():
            if header.lower() not in ['host', 'connection']:
                req.add_header(header, value)
        
        try:
            # Make request to backend
            with urllib.request.urlopen(req) as response:
                # Send response status
                self.send_response(response.getcode())
                
                # Copy response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Copy response body
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            self.send_error(e.code, e.reason)
        except Exception as e:
            self.send_error(500, str(e))

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    os.chdir('/var/www/ai_apps/standalone_app/v1')
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        httpd.serve_forever()