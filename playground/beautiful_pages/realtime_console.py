#!/usr/bin/env python3
"""
Real-time Python Console Output Streaming App
A beautiful, responsive FastAPI + WebSocket application that streams Python console output to browsers
"""

import asyncio
import json
import subprocess
import sys
import threading
import time
from datetime import datetime
from typing import List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


class ConnectionManager:
    """Manages WebSocket connections for real-time streaming"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.processes = {}
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)
            
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


# FastAPI app initialization
app = FastAPI(title="Real-time Console Streaming", description="Stream Python console output in real-time")

# Mount static files and templates
app.mount("/static", StaticFiles(directory=r"/var/www/ai_apps/playground/beautiful_pages/static"), name="static")
templates = Jinja2Templates(directory=r"/var/www/ai_apps/playground/beautiful_pages/templates")

# Connection manager
manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("console_dashboard.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for commands from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "execute":
                await execute_python_code(message["code"], websocket)
            elif message["type"] == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def execute_python_code(code: str, websocket: WebSocket):
    """Execute Python code and stream output in real-time"""
    try:
        # Send execution start message
        await manager.send_personal_message(
            json.dumps({
                "type": "execution_start",
                "timestamp": datetime.now().isoformat(),
                "code": code
            }),
            websocket
        )
        
        # Create subprocess for Python execution
        process = subprocess.Popen(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output line by line
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "output",
                        "content": output.strip(),
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
                
        # Send completion message
        return_code = process.poll()
        await manager.send_personal_message(
            json.dumps({
                "type": "execution_complete",
                "return_code": return_code,
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
    except Exception as e:
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )


@app.get("/examples")
async def get_examples():
    """Get example Python code snippets"""
    examples = [
        {
            "name": "Hello World Loop",
            "code": """import time
for i in range(5):
    print(f"Hello World {i+1}!")
    time.sleep(1)
print("Done!")"""
        },
        {
            "name": "Real-time Data Generation",
            "code": """import time
import random
import datetime

print("Starting real-time data stream...")
for i in range(10):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    value = random.randint(1, 100)
    print(f"[{timestamp}] Data point {i+1}: {value}")
    time.sleep(0.5)
print("Stream completed!")"""
        },
        {
            "name": "Progress Bar Simulation",
            "code": """import time
import sys

def progress_bar(total, current):
    percent = int((current / total) * 100)
    bar = '█' * (percent // 2) + '░' * (50 - percent // 2)
    return f"[{bar}] {percent}%"

total_items = 20
print("Processing items...")
for i in range(total_items + 1):
    print(f"\\r{progress_bar(total_items, i)}", end='', flush=True)
    time.sleep(0.2)
print("\\nProcessing complete!")"""
        },
        {
            "name": "File Processing Demo",
            "code": """import time
import random

files = ["data.csv", "config.json", "report.pdf", "image.png", "script.py"]
print("Processing files...")

for i, filename in enumerate(files, 1):
    print(f"Processing file {i}/{len(files)}: {filename}")
    
    # Simulate processing time
    processing_time = random.uniform(0.5, 2.0)
    time.sleep(processing_time)
    
    # Simulate different outcomes
    if random.random() > 0.8:
        print(f"  ⚠️  Warning: Large file size for {filename}")
    else:
        print(f"  ✅ Successfully processed {filename}")

print("\\n🎉 All files processed successfully!")"""
        },
        {
            "name": "System Monitoring",
            "code": """import time
import random
import datetime

print("🖥️  System Monitor - Real-time Stats")
print("=" * 40)

for i in range(15):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    cpu_usage = random.randint(10, 90)
    memory_usage = random.randint(30, 80)
    disk_io = random.randint(0, 100)
    
    print(f"[{timestamp}] CPU: {cpu_usage}% | Memory: {memory_usage}% | Disk I/O: {disk_io} MB/s")
    time.sleep(0.8)

print("\\n📊 Monitoring session completed!")"""
        }
    ]
    return examples


if __name__ == "__main__":
    uvicorn.run(
        "realtime_console:app",
        host="0.0.0.0",
        port=8991,
        reload=True,
        log_level="info"
    )
