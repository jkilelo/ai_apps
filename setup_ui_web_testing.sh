#!/bin/bash

# Setup script for UI Web Auto Testing

echo "Setting up UI Web Auto Testing environment..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install fastapi uvicorn slowapi pydantic playwright httpx psutil

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium
playwright install-deps

# Install Node.js dependencies (if not already installed)
echo "Installing Node.js dependencies..."
cd /var/www/ai_apps
npm install

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. Start the API server: cd apps/ui_web_auto_testing && python run_api.py"
echo "2. Start the frontend: npm run dev"
echo ""
echo "API will be available at: http://localhost:8002"
echo "Frontend will be available at: http://localhost:3000 or 3001"