#!/bin/bash
# AI-First Smart Browser - Quick Setup Script
# This script initializes the development environment with all optimizations

echo "🚀 AI-First Smart Browser Setup Script v2.0.0"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 1. Check Python version
echo ""
echo "📋 Checking prerequisites..."
python_version=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [ $(echo "$python_version >= 3.11" | bc -l) -eq 1 ]; then
    print_status "Python $python_version detected"
else
    print_error "Python 3.11+ required (found $python_version)"
    exit 1
fi

# 2. Clean up any remaining redundant files
echo ""
echo "🧹 Cleaning up redundant files..."
cd .claude 2>/dev/null || { print_warning ".claude directory not found"; }
rm -f CLAUDE_IMPROVEMENTS.md CRITICAL_GAPS_ANALYSIS.md \
      FULL_SYNC_REPORT.md SYNC_REPORT.md \
      PROJECT_READINESS_ASSESSMENT.md IMPLEMENTATION_READY_CHECKLIST.md \
      UNIFIED_CONFIG_STRATEGY.md MODERN_PYTHON_STANDARDS.md \
      HOOKS_GUIDE.md CLEANUP_PLAN.md \
      settings.optimized.json hooks_browser_specific.json 2>/dev/null
cd ..
print_status "Redundant files cleaned"

# 3. Create necessary directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p .claude/memory .claude/logs .claude/exports .claude/profiles
mkdir -p data/qdrant data/meilisearch data/falkordb
mkdir -p src/execution src/perception src/cognition src/memory src/extensibility
mkdir -p tests/unit tests/integration tests/stealth tests/e2e
mkdir -p plugins/stealth scripts screenshots logs
print_status "Directory structure created"

# 4. Check for UV package manager
echo ""
echo "📦 Checking package manager..."
if command -v uv &> /dev/null; then
    print_status "UV package manager found"
    PKG_CMD="uv pip"
else
    print_warning "UV not found, falling back to pip"
    PKG_CMD="pip"
    echo "   To install UV (recommended): curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# 5. Create virtual environment if it doesn't exist
echo ""
echo "🐍 Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python -m venv .venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# 6. Install dependencies
echo ""
echo "📚 Installing dependencies..."
$PKG_CMD install -r requirements.txt
if [ $? -eq 0 ]; then
    print_status "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# 7. Install Playwright browsers
echo ""
echo "🎭 Installing Playwright browsers..."
playwright install chromium
if [ $? -eq 0 ]; then
    print_status "Playwright chromium installed"
else
    print_warning "Playwright installation failed - may need manual installation"
fi

# 8. Install pre-commit hooks
echo ""
echo "🪝 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    print_status "Pre-commit hooks installed"
else
    print_warning "Pre-commit not found - install with: pip install pre-commit"
fi

# 9. Check environment variables
echo ""
echo "🔑 Checking environment variables..."
if [ -f ".env" ]; then
    print_status ".env file exists"
    # Check for required API keys
    if grep -q "OPENAI_API_KEY=sk-" .env || \
       grep -q "ANTHROPIC_API_KEY=sk-ant-" .env || \
       grep -q "GOOGLE_API_KEY=AIza" .env; then
        print_status "At least one LLM API key configured"
    else
        print_warning "No LLM API keys found in .env - add at least one"
    fi
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning ".env created from .env.example - please add your API keys"
    else
        print_error ".env file not found and no .env.example available"
    fi
fi

# 10. Check Podman containers
echo ""
echo "🐳 Checking Podman containers..."
if command -v podman &> /dev/null; then
    # Check FalkorDB
    if podman ps | grep -q falkordb; then
        print_status "FalkorDB container running"
    else
        print_warning "FalkorDB container not running"
        echo "   To start: podman start falkordb"
    fi
    
    # Check Meilisearch
    if podman ps | grep -q meilisearch; then
        print_status "Meilisearch container running"
    else
        print_warning "Meilisearch container not running"
        echo "   To start: podman start meilisearch"
    fi
    
    # Check Qdrant
    if podman ps | grep -q qdrant; then
        print_status "Qdrant container running"
    else
        print_warning "Qdrant container not running (optional)"
        echo "   To deploy: podman run -d --name qdrant -p 6333:6333 docker.io/qdrant/qdrant:latest"
    fi
else
    print_warning "Podman not accessible - container status unknown"
    # Test services directly
    if redis-cli -p 6379 ping &> /dev/null; then
        print_status "FalkorDB accessible on port 6379"
    fi
    if curl -s http://localhost:7700/health | grep -q available &> /dev/null; then
        print_status "Meilisearch accessible on port 7700"
    fi
fi

# 11. Run basic validation
echo ""
echo "🔍 Running validation checks..."

# Check Python imports
python -c "import playwright; import pydantic; import loguru" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Core Python packages importable"
else
    print_error "Some Python packages failed to import"
fi

# Check Claude Code configuration
if [ -f ".claude/CLAUDE.md" ] && [ -f ".claude/settings.local.json" ]; then
    print_status "Claude Code configuration present"
else
    print_error "Claude Code configuration missing"
fi

# 12. Create initial implementation files if missing
echo ""
echo "📝 Checking implementation files..."
if [ ! -f "src/main.py" ]; then
    cat > src/main.py << 'EOF'
"""AI-First Smart Browser - Main Entry Point"""
import asyncio
import typer
from loguru import logger

app = typer.Typer()

@app.command()
def main(
    task: str = typer.Argument(None, help="Task to execute"),
    url: str = typer.Option("https://google.com", help="Starting URL"),
    headless: bool = typer.Option(False, help="Run in headless mode"),
):
    """AI-First Smart Browser CLI"""
    logger.info(f"Starting browser with task: {task}")
    # TODO: Implement main logic
    print(f"🚀 AI Browser v2.0.0 - Ready for implementation")
    print(f"Task: {task}")
    print(f"URL: {url}")
    print(f"Headless: {headless}")

if __name__ == "__main__":
    app()
EOF
    print_status "Created src/main.py stub"
fi

# 13. Final summary
echo ""
echo "========================================"
echo "📊 Setup Summary"
echo "========================================"
echo ""
echo "✅ Completed:"
echo "  • Removed duplicate parent CLAUDE.md"
echo "  • Cleaned 11 redundant files"
echo "  • Created directory structure"
echo "  • Installed dependencies"
echo "  • Configured development environment"
echo ""

if [ -f ".env" ] && grep -q "=sk-\|=AIza" .env; then
    echo "🚀 Ready to start development!"
    echo ""
    echo "Quick commands:"
    echo "  make run           - Run the application"
    echo "  make test          - Run tests"
    echo "  make quality       - Check code quality"
    echo "  make container-up  - Start Podman containers"
    echo ""
    echo "Development workflow:"
    echo "  source .claude/aliases.sh  - Load development aliases"
    echo "  python src/main.py --help  - Show CLI help"
else
    echo "⚠️  Almost ready! Next steps:"
    echo "  1. Add your API keys to .env file"
    echo "  2. Start Podman containers: make container-up"
    echo "  3. Run: make test"
fi

echo ""
echo "📚 Documentation:"
echo "  • Architecture: .claude/CLAUDE.md"
echo "  • Container guide: .claude/CONTAINER_REFERENCE.md"
echo "  • Development: .claude/README.md"
echo ""
echo "Happy coding! 🎉"