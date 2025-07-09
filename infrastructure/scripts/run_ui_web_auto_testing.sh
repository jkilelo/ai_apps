#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default port if not set
export UI_WEB_AUTO_TESTING_PORT=${UI_WEB_AUTO_TESTING_PORT:-8002}

echo "Starting UI Web Auto Testing on port $UI_WEB_AUTO_TESTING_PORT..."
echo "Access the application at http://localhost:$UI_WEB_AUTO_TESTING_PORT"

# Run the FastAPI server
python -m apps.ui_web_auto_testing.api.main