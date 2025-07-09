#!/bin/bash
# Cross-platform runner script for AI Apps Suite

echo "🚀 Starting AI Apps Suite..."

# Detect the operating system
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS_NAME="Linux";;
    Darwin*)    OS_NAME="macOS";;
    MINGW*)     OS_NAME="Windows";;
    CYGWIN*)    OS_NAME="Windows";;
    *)          OS_NAME="Unknown";;
esac

echo "📍 Detected OS: ${OS_NAME}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Python version: ${PYTHON_VERSION}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ "${OS_NAME}" = "Windows" ]; then
    # Windows
    source venv/Scripts/activate 2>/dev/null || venv\\Scripts\\activate
else
    # Unix-like systems
    source venv/bin/activate
fi

# Install/upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
if [ "${OS_NAME}" = "Windows" ]; then
    # Use platform-agnostic requirements for Windows
    pip install -r requirements_platform_agnostic.txt
else
    # Use regular requirements for Unix systems
    pip install -r requirements.txt
fi

# Install Playwright browsers if not already installed
echo "🎭 Setting up Playwright..."
playwright install chromium 2>/dev/null || echo "ℹ️  Playwright browsers already installed"

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ENVIRONMENT="${ENVIRONMENT:-development}"

# Build frontend if needed
if [ -d "src" ] && [ -f "package.json" ]; then
    if [ ! -d "dist" ] || [ "${ENVIRONMENT}" = "development" ]; then
        echo "🔨 Building frontend..."
        if command -v npm &> /dev/null; then
            npm install
            npm run build
        else
            echo "⚠️  npm not found. Skipping frontend build."
            echo "   Install Node.js to build the frontend."
        fi
    fi
fi

# Run the server
echo "🚀 Starting server..."
python run.py