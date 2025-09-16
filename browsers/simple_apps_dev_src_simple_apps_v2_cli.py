"""
Command-line interface for Simple Apps v2.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from simple_apps_v2 import __version__
from simple_apps_v2.api.app import create_app
from simple_apps_v2.core.config import get_settings
from simple_apps_v2.core.logging import setup_logging
from simple_apps_v2.services.extractor import ElementExtractor

# Fix for Windows async subprocess
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = typer.Typer(
    name="simple-apps-v2",
    help="Modern web automation testing application",
    add_completion=False,
)

console = Console()


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"Simple Apps v2 version {__version__}")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(5175, help="Port to bind to"),
    reload: bool = typer.Option(True, help="Enable auto-reload"),
    workers: int = typer.Option(1, help="Number of worker processes"),
    log_level: str = typer.Option("info", help="Log level"),
) -> None:
    """Start the API server."""
    
    # Setup logging
    setup_logging(level=log_level.upper())
    
    console.print(f"🚀 Starting Simple Apps v2 API server on {host}:{port}")
    
    # Create FastAPI app
    fastapi_app = create_app()
    
    # Run with uvicorn
    config = uvicorn.Config(
        app=fastapi_app,
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,  # reload doesn't work with multiple workers
        log_level=log_level,
        access_log=True,
    )
    
    server = uvicorn.Server(config)
    server.run()


@app.command()
def extract(
    url: str = typer.Argument(..., help="URL to extract elements from"),
    headless: bool = typer.Option(True, help="Run browser in headless mode"),
    analyze: bool = typer.Option(True, help="Use LLM for element analysis"),
    output: Optional[Path] = typer.Option(None, help="Output file path (JSON)"),
    verbose: bool = typer.Option(False, help="Verbose output"),
) -> None:
    """Extract elements from a web page."""
    
    setup_logging(level="DEBUG" if verbose else "INFO")
    
    async def _extract() -> None:
        try:
            console.print(f"🔍 Extracting elements from: {url}")
            
            # Create extractor
            extractor = ElementExtractor()
            
            # Extract elements
            result = await extractor.extract_elements_from_url(
                url=url,
                analyze_with_llm=analyze
            )
            
            if result.get("success", False):
                total_elements = result.get("total_elements", 0)
                console.print(f"✅ Successfully extracted {total_elements} elements")
                
                # Display summary table
                elements_by_category = result.get("elements_by_category", {})
                if elements_by_category:
                    table = Table(title="Elements by Category")
                    table.add_column("Category", style="cyan")
                    table.add_column("Count", style="green")
                    
                    for category, elements in elements_by_category.items():
                        table.add_row(category, str(len(elements)))
                    
                    console.print(table)
                
                # Save to file if specified
                if output:
                    import json
                    output.parent.mkdir(parents=True, exist_ok=True)
                    with open(output, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, default=str)
                    console.print(f"💾 Results saved to: {output}")
                
                # Show LLM analysis if available
                llm_analysis = result.get("llm_analysis")
                if llm_analysis and verbose:
                    console.print("\n🧠 LLM Analysis:")
                    console.print(llm_analysis.get("summary", "No summary available"))
                
            else:
                error = result.get("error", "Unknown error")
                console.print(f"❌ Extraction failed: {error}", style="red")
                raise typer.Exit(1)
        
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")
            raise typer.Exit(1)
    
    # Run async function
    asyncio.run(_extract())


@app.command()
def config() -> None:
    """Show current configuration."""
    settings = get_settings()
    
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    config_items = [
        ("App Name", settings.app_name),
        ("Version", settings.version),
        ("Debug Mode", str(settings.debug)),
        ("API Host", settings.api_host),
        ("API Port", str(settings.api_port)),
        ("Default LLM Provider", settings.default_llm_provider),
        ("Default LLM Model", settings.default_llm_model),
        ("Browser Headless", str(settings.browser_headless)),
        ("Log Level", settings.log_level),
        ("OpenAI API Key", "Set" if settings.openai_api_key else "Not set"),
        ("Google API Key", "Set" if settings.google_api_key else "Not set"),
        ("Anthropic API Key", "Set" if settings.anthropic_api_key else "Not set"),
    ]
    
    for setting, value in config_items:
        table.add_row(setting, str(value))
    
    console.print(table)


@app.command()
def health() -> None:
    """Check system health and dependencies."""
    console.print("🏥 System Health Check\n")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    status = "✅" if sys.version_info >= (3, 10) else "❌"
    console.print(f"{status} Python {python_version} (required: 3.10+)")
    
    # Check dependencies
    dependencies = [
        ("FastAPI", "fastapi"),
        ("Playwright", "playwright"),
        ("OpenAI", "openai"),
        ("Pydantic", "pydantic"),
        ("Rich", "rich"),
        ("Typer", "typer"),
    ]
    
    for dep_name, module_name in dependencies:
        try:
            __import__(module_name)
            console.print(f"✅ {dep_name} - Available")
        except ImportError:
            console.print(f"❌ {dep_name} - Missing")
    
    # Check configuration
    settings = get_settings()
    
    console.print("\n🔧 Configuration Status:")
    
    # API Keys
    if settings.openai_api_key:
        console.print("✅ OpenAI API Key - Configured")
    else:
        console.print("⚠️ OpenAI API Key - Not configured")
    
    if settings.google_api_key:
        console.print("✅ Google API Key - Configured")
    else:
        console.print("⚠️ Google API Key - Not configured")
    
    if settings.anthropic_api_key:
        console.print("✅ Anthropic API Key - Configured")
    else:
        console.print("⚠️ Anthropic API Key - Not configured")
    
    # Check Playwright browsers
    console.print("\n🌐 Browser Status:")
    try:
        from playwright._impl._driver import compute_driver_executable
        driver_path = compute_driver_executable()
        if driver_path.exists():
            console.print("✅ Playwright - Browsers installed")
        else:
            console.print("❌ Playwright - Browsers not installed (run: playwright install)")
    except Exception:
        console.print("⚠️ Playwright - Cannot check browser status")


@app.command()
def init(
    directory: Path = typer.Argument(Path.cwd(), help="Directory to initialize"),
    force: bool = typer.Option(False, help="Overwrite existing files"),
) -> None:
    """Initialize a new project directory with templates."""
    
    console.print(f"📁 Initializing project in: {directory}")
    
    # Create directory structure
    directories = [
        "tests",
        "pages", 
        "config",
        "reports",
        "screenshots",
    ]
    
    for dir_name in directories:
        dir_path = directory / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"✅ Created directory: {dir_name}")
    
    # Create template files
    templates = {
        ".env": """# Environment variables for Simple Apps v2
# Copy this file to .env and fill in your API keys

# LLM API Keys (optional - will use defaults if not set)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=5175
DEBUG=true

# Browser Configuration
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30000

# Logging
LOG_LEVEL=INFO
""",
        
        "pytest.ini": """[tool:pytest]
minversion = 8.0
addopts = -ra --strict-markers --strict-config -v
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    browser: marks tests that require browser automation
""",
        
        "README.md": f"""# Simple Apps v2 Project

Generated with Simple Apps v2 version {__version__}

## Getting Started

1. Install dependencies:
   ```bash
   pip install simple-apps-v2
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

4. Start the API server:
   ```bash
   simple-apps serve
   ```

5. Extract elements from a website:
   ```bash
   simple-apps extract https://example.com
   ```

## Project Structure

- `tests/` - Generated test files
- `pages/` - Page object models
- `config/` - Configuration files
- `reports/` - Test reports
- `screenshots/` - Screenshots from test runs

## Documentation

Visit the API documentation at http://localhost:5175/docs when the server is running.
""",
    }
    
    for filename, content in templates.items():
        file_path = directory / filename
        
        if file_path.exists() and not force:
            console.print(f"⚠️ Skipped existing file: {filename}")
            continue
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        console.print(f"✅ Created file: {filename}")
    
    console.print(f"\n🎉 Project initialized successfully!")
    console.print(f"📝 Edit {directory}/.env to configure your API keys")
    console.print(f"🚀 Run 'simple-apps serve' to start the API server")


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()