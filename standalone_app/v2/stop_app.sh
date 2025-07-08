#!/bin/bash

# AI Apps v2 Stop Script

echo "🛑 Stopping AI Apps v2..."

# Stop backend
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm backend.pid
    else
        echo "Backend server not running"
        rm backend.pid
    fi
else
    echo "No backend PID file found"
fi

# Kill any remaining processes on ports
echo "Cleaning up ports..."
lsof -ti:8004 | xargs -r kill -9 2>/dev/null || true

echo "✅ AI Apps v2 stopped"