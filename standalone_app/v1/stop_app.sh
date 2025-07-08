#!/bin/bash

# Stop script for v1 standalone app

echo "Stopping AI Apps Standalone v1..."

# Kill the FastAPI process
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "FastAPI backend stopped."
    else
        echo "FastAPI process not found."
    fi
    rm -f app.pid
else
    # Try to find and kill by port
    PID=$(lsof -ti:8004)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo "Stopped process on port 8004."
    else
        echo "No process found on port 8004."
    fi
fi

# Clean up log files
if [ -f "app.log" ]; then
    rm -f app.log
fi

echo "AI Apps Standalone v1 stopped successfully!"