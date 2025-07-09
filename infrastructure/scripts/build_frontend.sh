#!/bin/bash
# Build the frontend application

echo "Building frontend..."
cd "$(dirname "$0")/../../ui" || exit 1

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Build the application
npm run build

echo "Frontend build complete!"