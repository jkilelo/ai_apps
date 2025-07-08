# Platform Installation Guide

This guide provides platform-specific instructions for installing and running the AI Apps Suite on Windows, macOS, and Linux.

## Prerequisites

### All Platforms
- Python 3.8 or higher
- Node.js 18+ and npm (for frontend development)
- Git

## Windows Installation

### 1. Install Python
Download and install Python from [python.org](https://www.python.org/downloads/)
- **Important**: Check "Add Python to PATH" during installation

### 2. Install Node.js
Download and install Node.js from [nodejs.org](https://nodejs.org/)

### 3. Install Git
Download and install Git from [git-scm.com](https://git-scm.com/download/win)

### 4. Clone the Repository
```cmd
git clone https://github.com/jkilelo/ai_apps.git
cd ai_apps
```

### 5. Run the Windows Setup
```cmd
run_cross_platform.bat
```

Or manually:
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements_platform_agnostic.txt

# Install Playwright browsers
playwright install chromium

# Build frontend
npm install
npm run build

# Run the server
python run.py
```

### Windows-Specific Notes
- Uses single-worker mode (multi-worker support is limited on Windows)
- No uvloop support (uses default asyncio)
- May require Windows Defender/Firewall exceptions for localhost

## macOS Installation

### 1. Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python
```bash
brew install python@3.11
```

### 3. Install Node.js
```bash
brew install node
```

### 4. Clone and Setup
```bash
git clone https://github.com/jkilelo/ai_apps.git
cd ai_apps

# Run the setup script
chmod +x run_cross_platform.sh
./run_cross_platform.sh
```

### macOS-Specific Notes
- Supports multi-worker mode
- Can use uvloop for better performance
- May require privacy permissions for browser automation

## Linux Installation

### Ubuntu/Debian

```bash
# Update system
sudo apt update

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git nodejs npm

# Install additional dependencies for Playwright
sudo apt install libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2

# Clone and setup
git clone https://github.com/jkilelo/ai_apps.git
cd ai_apps
./run_cross_platform.sh
```

### Fedora/RHEL/CentOS

```bash
# Install Python and dependencies
sudo dnf install python3 python3-pip git nodejs npm

# Install Playwright dependencies
sudo dnf install nss nspr atk at-spi2-atk cups-libs libdrm \
    libxkbcommon libXcomposite libXdamage libXfixes libXrandr \
    mesa-libgbm alsa-lib

# Clone and setup
git clone https://github.com/jkilelo/ai_apps.git
cd ai_apps
./run_cross_platform.sh
```

### Linux-Specific Notes
- Best performance with uvloop
- Supports multi-worker mode
- May need `--no-sandbox` flag for Playwright in containers

## Docker Installation (All Platforms)

### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    nodejs \
    npm \
    && apt-get clean

# Install Playwright dependencies
RUN npx playwright install-deps

# Copy application
COPY . .

# Install Python dependencies
RUN pip install -r requirements_platform_agnostic.txt

# Install Playwright browsers
RUN playwright install chromium

# Build frontend
RUN npm install && npm run build

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "run.py"]
```

### 2. Build and Run
```bash
docker build -t ai-apps .
docker run -p 8080:8080 ai-apps
```

## Environment Variables

Create a `.env` file in the root directory:

```env
# Server Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8080
ENVIRONMENT=development

# MongoDB (optional)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=ai_apps

# OpenAI API (for multimodal analysis)
OPENAI_API_KEY=your_api_key_here
```

## Troubleshooting

### Windows Issues

1. **ImportError: No module named 'uvloop'**
   - This is expected on Windows. The app automatically falls back to asyncio

2. **Playwright browser not found**
   ```cmd
   playwright install chromium
   ```

3. **Permission denied errors**
   - Run Command Prompt as Administrator

### macOS Issues

1. **SSL Certificate errors**
   ```bash
   pip install --upgrade certifi
   ```

2. **Playwright permissions**
   - Go to System Preferences → Security & Privacy → Privacy
   - Allow Terminal/IDE to control computer

### Linux Issues

1. **Missing shared libraries for Playwright**
   ```bash
   sudo apt-get install libgbm1  # or equivalent for your distro
   ```

2. **Permission denied on port**
   - Use a port > 1024 or run with sudo (not recommended)

## Performance Optimization

### Windows
- Use Windows Terminal for better performance
- Disable Windows Defender real-time scanning for project directory
- Close unnecessary applications

### macOS
- Install uvloop: `pip install uvloop`
- Use Activity Monitor to check resource usage

### Linux
- Install uvloop: `pip install uvloop`
- Use systemd for production deployment
- Configure proper ulimits for file descriptors

## Next Steps

1. Access the application at `http://localhost:8080`
2. API documentation at `http://localhost:8080/api/docs`
3. Run tests: `pytest`
4. Check platform compatibility: `python utils/platform_utils.py`