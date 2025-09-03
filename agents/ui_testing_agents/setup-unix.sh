#!/bin/bash
# V2 LLM-Native System - Unix/Linux/Mac Setup Script
# ===================================================

echo "======================================================================"
echo "V2 LLM-NATIVE SYSTEM - UNIX/LINUX/MAC SETUP"
echo "======================================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.7+ first"
    exit 1
fi

echo "[OK] Python is installed: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    echo "[OK] Virtual environment created"
else
    echo "[INFO] Virtual environment already exists"
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "[INFO] Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "[INFO] Installing requirements..."
pip install -r requirements.txt

# Install Playwright browsers
echo "[INFO] Installing Playwright browsers..."
playwright install chromium

# Setup .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo "[INFO] Creating .env file from template..."
        cp .env.template .env
        echo ""
        echo "======================================================================"
        echo "IMPORTANT: Edit .env file and add your API keys"
        echo "You need at least ONE of:"
        echo "  - OpenAI API Key"
        echo "  - Anthropic API Key"
        echo "  - Google API Key"
        echo "======================================================================"
        echo ""
        
        # Try to open in default editor
        if [ -n "$EDITOR" ]; then
            $EDITOR .env
        elif command -v nano &> /dev/null; then
            nano .env
        elif command -v vi &> /dev/null; then
            vi .env
        else
            echo "Please manually edit .env file and add your API keys"
        fi
    fi
else
    echo "[INFO] .env file already exists"
fi

echo ""
echo "======================================================================"
echo "SETUP COMPLETE!"
echo "======================================================================"
echo ""
echo "To use the V2 system:"
echo "  1. Ensure .env has your API keys"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: python3 workplace_agents_v2/examples/quick_demo.py"
echo ""
echo "======================================================================"