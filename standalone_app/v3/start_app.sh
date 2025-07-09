#!/bin/bash

# AI Apps v2 Startup Script

echo "🚀 Starting AI Apps v2..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OPENAI_API_KEY"
fi

# Start the application
echo "Starting backend server..."
cd api
python main.py &
BACKEND_PID=$!

# Store PID for stop script
echo $BACKEND_PID > ../backend.pid

echo "✅ AI Apps v2 is running!"
echo "📍 Frontend: http://localhost:8004"
echo "📍 API Docs: http://localhost:8004/api/docs"
echo ""
echo "To stop the application, run: ./stop_app.sh"

# Keep script running
wait $BACKEND_PID