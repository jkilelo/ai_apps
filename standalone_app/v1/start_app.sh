#!/bin/bash

# Start script for v1 standalone app

echo "Starting AI Apps Standalone v1..."

# Set environment variables
export PYTHONPATH=/var/www/ai_apps/standalone_app/v1:$PYTHONPATH
export NODE_ENV=production
export PORT=8004

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "MongoDB is not running. Please start MongoDB first."
    exit 1
fi

# Check if PySpark container is running (optional for data profiling)
if ! docker ps | grep -q "pyspark-notebook"; then
    echo "Warning: PySpark container is not running. Data profiling features may be limited."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
cd /var/www/ai_apps/standalone_app/v1
pip install -r requirements.txt > /dev/null 2>&1

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium > /dev/null 2>&1

# Build React frontend
echo "Building React frontend..."
cd /var/www/ai_apps/standalone_app/v1/frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
npm run build --silent

# Start the FastAPI backend
echo "Starting FastAPI backend on port 8004..."
cd /var/www/ai_apps/standalone_app/v1
nohup uvicorn api.main:app --host 0.0.0.0 --port 8004 --reload > app.log 2>&1 &
echo $! > app.pid

echo "AI Apps Standalone v1 started successfully!"
echo "Access the application at: http://localhost:8004"
echo ""
echo "To stop the application, run: ./stop_app.sh"