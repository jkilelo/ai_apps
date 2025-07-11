#!/bin/bash

# Real-time Console Streaming App Startup Script

echo "🚀 Starting Real-time Python Console Streamer..."
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully!"
else
    echo "⚠️  requirements.txt not found. Installing FastAPI and uvicorn..."
    pip install fastapi uvicorn
fi

echo ""
echo "🎯 Starting the application..."
echo "📍 Server will be available at: http://localhost:8001"
echo "🔧 Press Ctrl+C to stop the server"
echo ""

# Start the application
python3 realtime_console.py
