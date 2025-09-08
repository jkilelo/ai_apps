# Installation Guide

This guide will help you install and set up the AI-First Smart Browser on your system.

## System Requirements

### Minimum Requirements
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for dependencies and browser engines
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)

### Recommended Requirements
- **Python**: 3.12+ for optimal performance
- **RAM**: 16GB for production workloads
- **CPU**: Multi-core processor for concurrent task execution
- **Storage**: SSD for faster browser initialization

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/ai-first-smart-browser.git
cd ai-first-smart-browser

# Run the setup script
./setup.sh  # On Linux/macOS
# OR
setup.bat   # On Windows
```

The setup script will:
- Create a virtual environment
- Install Python dependencies
- Download browser engines
- Set up container services (optional)
- Initialize the configuration

### Method 2: Manual Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/ai-first-smart-browser.git
cd ai-first-smart-browser
```

#### Step 2: Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv venv

# Activate environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Using conda (alternative)
conda create -n ai-browser python=3.11
conda activate ai-browser
```

#### Step 3: Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install browser engines
playwright install

# For development (optional)
pip install -r requirements-dev.txt
```

#### Step 4: Install Browser Engines
```bash
# Install all supported browsers
playwright install

# Or install specific browsers
playwright install chromium
playwright install firefox
playwright install webkit
```

## Container Services Setup

The AI-First Smart Browser uses containerized services for advanced memory capabilities. These are optional but recommended for production use.

### Using Podman (Recommended)

#### Install Podman
=== "Linux (Ubuntu/Debian)"
    ```bash
    sudo apt update
    sudo apt install -y podman
    ```

=== "macOS"
    ```bash
    brew install podman
    podman machine init
    podman machine start
    ```

=== "Windows"
    ```powershell
    # Install via Chocolatey
    choco install podman-desktop
    
    # Or download from GitHub releases
    # https://github.com/containers/podman/releases
    ```

#### Deploy Services
```bash
# Start all services
podman-compose up -d

# Or start individual services
podman run -d --name falkordb -p 6379:6379 falkordb/falkordb:latest
podman run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest
podman run -d --name meilisearch -p 7700:7700 getmeili/meilisearch:latest
```

### Using Docker (Alternative)

```bash
# Start all services
docker-compose up -d

# Or start individual services
docker run -d --name falkordb -p 6379:6379 falkordb/falkordb:latest
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest
docker run -d --name meilisearch -p 7700:7700 getmeili/meilisearch:latest
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# LLM API Keys (at least one required)
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Container Services (optional)
QDRANT_HOST=localhost
QDRANT_PORT=6333
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
MEILISEARCH_HOST=localhost
MEILISEARCH_PORT=7700

# Browser Configuration
DEFAULT_BROWSER=chromium
HEADLESS=true
STEALTH_MODE=true

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs

# Performance
MAX_CONCURRENT_TASKS=3
MEMORY_LIMIT_MB=2048
```

### Configuration File

The main configuration is in `configs/default.json`:

```json
{
  "browser": {
    "type": "chromium",
    "headless": true,
    "viewport": {"width": 1920, "height": 1080},
    "stealth": {
      "enabled": true,
      "plugins": ["webdriver_removal", "canvas_noise", "user_agent_spoof"]
    }
  },
  "llm": {
    "default_provider": "openai",
    "model": "gpt-4",
    "max_tokens": 4096,
    "temperature": 0.1
  },
  "memory": {
    "session_db_path": ".claude/memory/session.db",
    "cleanup_interval_hours": 24,
    "max_history_items": 1000
  }
}
```

## Verification

### Test Installation

```bash
# Run the installation test
python -c "
from src.execution.browser_manager import BrowserManager
from src.cognition.llm_manager import LLMManager
print('✅ All core modules imported successfully')
"
```

### Health Check

```bash
# Run comprehensive health check
python src/main.py --health-check

# Expected output:
# ✅ System Health: OK
# ✅ Browser Engine: OK  
# ✅ LLM Providers: OK
# ✅ Memory Layers: OK
# ✅ Container Services: OK (optional)
```

### Basic Functionality Test

```bash
# Run a simple task
python src/main.py --task "Navigate to google.com and take a screenshot" --test-mode
```

## Troubleshooting

### Common Issues

#### 1. Browser Installation Fails
```bash
# Error: Playwright browsers not installed
playwright install

# Error: Permission denied
sudo playwright install  # Linux/macOS
# Run as administrator on Windows
```

#### 2. Container Connection Issues
```bash
# Check container status
podman ps -a
# OR
docker ps -a

# Restart containers
podman restart falkordb qdrant meilisearch
```

#### 3. Python Version Conflicts
```bash
# Check Python version
python --version

# Use specific Python version
python3.11 -m venv venv
```

#### 4. Import Errors
```bash
# Missing dependencies
pip install -r requirements.txt

# Path issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Getting Help

If you encounter issues:

1. **Check the logs**: `tail -f logs/app.log`
2. **Run diagnostics**: `python src/diagnostics.py`
3. **Search issues**: [GitHub Issues](https://github.com/your-org/ai-first-smart-browser/issues)
4. **Ask for help**: [GitHub Discussions](https://github.com/your-org/ai-first-smart-browser/discussions)

## Next Steps

Once installation is complete:

1. **[Quick Start Guide](quickstart.md)** - Run your first automated task
2. **[Configuration Guide](configuration.md)** - Customize for your needs  
3. **[Architecture Overview](../architecture/overview.md)** - Understand the system design
4. **[User Guide](../user-guide/basic-usage.md)** - Learn advanced features

---

**Installation complete!** 🎉 You're ready to start automating web tasks with AI.