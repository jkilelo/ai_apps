#!/bin/bash

echo "Form Chain Engine Demo Comparison"
echo "================================="
echo ""
echo "This script will help you run both implementations side by side"
echo ""

# Function to run a server in the background
run_server() {
    local script=$1
    local port=$2
    local name=$3
    
    echo "Starting $name on port $port..."
    python $script > /dev/null 2>&1 &
    local pid=$!
    echo "  PID: $pid"
    
    # Wait a moment for server to start
    sleep 2
    
    # Check if server is running
    if ps -p $pid > /dev/null; then
        echo "  ✓ $name is running"
        return $pid
    else
        echo "  ❌ Failed to start $name"
        return 0
    fi
}

echo "1. Starting Original Implementation (port 8037)..."
echo "   URL: http://localhost:8037"
run_server "html_v3_demo_server.py" 8037 "Original Implementation"
ORIGINAL_PID=$!

echo ""
echo "2. Starting Simplified Implementation (port 8038)..."
echo "   URL: http://localhost:8038"
run_server "html_v3_simplified_demo_server.py" 8038 "Simplified Implementation"
SIMPLIFIED_PID=$!

echo ""
echo "Both servers are running!"
echo ""
echo "You can now:"
echo "  - Visit http://localhost:8037 for the original implementation"
echo "  - Visit http://localhost:8038 for the simplified implementation"
echo "  - Run the test script: python test_simplified_implementation.py"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Wait for user to press Ctrl+C
trap 'echo ""; echo "Stopping servers..."; kill $ORIGINAL_PID $SIMPLIFIED_PID 2>/dev/null; exit' INT

# Keep script running
while true; do
    sleep 1
done