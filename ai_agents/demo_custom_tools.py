"""
Demo script for custom browser-use tools
Shows how to use the custom tools framework
"""

import asyncio
import sys
import os
import io
from pathlib import Path

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from browser_use import ChatGoogle
from browser_use.agent.service import Agent
from custom_tools import CustomToolsManager, FileAnalyzerParams
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# Import the Google client if needed
from ai_service_layer.clients.google_client import get_client as gclient
from ai_service_layer.clients.google_client import get_base_params


class ScreenshotParams(BaseModel):
    """Parameters for screenshot tool"""
    filename: str = Field(default="screenshot.png", description="Filename for the screenshot")
    full_page: bool = Field(default=False, description="Capture full page or just viewport")


class FormFillerParams(BaseModel):
    """Parameters for form filling tool"""
    form_data: dict = Field(description="Dictionary of form field names/IDs to values")
    submit: bool = Field(default=False, description="Whether to submit the form after filling")


class PerformanceAnalyzerParams(BaseModel):
    """Parameters for performance analysis"""
    metrics: list[str] = Field(
        default=["loadTime", "domContentLoaded", "firstPaint"],
        description="Performance metrics to collect"
    )


async def demo_basic_tools():
    """Demonstrate basic custom tools"""
    print("\n" + "="*60)
    print("DEMO: Basic Custom Tools")
    print("="*60)

    # Create custom tools manager
    manager = CustomToolsManager(include_defaults=True)

    # Create LLM instance
    llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

    # Task 1: Count all available tools
    task1 = """
    Use the count_tools action to count all available tools.
    Get detailed information about both custom and default tools.
    Display the results in a nice format.
    """

    print("\n📊 Task 1: Counting all available tools...")
    agent = Agent(task=task1, llm=llm, tools=manager.get_tools_instance())
    await agent.run()
    await agent.close()

    # Task 2: Extract elements from a webpage
    task2 = """
    Navigate to example.com and use the extract_elements_advanced action
    to extract all links and buttons from the page.
    Include their attributes and display a summary.
    """

    print("\n🔍 Task 2: Extracting elements from example.com...")
    agent = Agent(task=task2, llm=llm, tools=manager.get_tools_instance())
    await agent.run()
    await agent.close()


async def demo_dynamic_tools():
    """Demonstrate dynamically adding new tools"""
    print("\n" + "="*60)
    print("DEMO: Dynamic Tool Addition")
    print("="*60)

    # Create custom tools manager
    manager = CustomToolsManager(include_defaults=True)

    # Add a screenshot tool dynamically
    @manager.tools.registry.action(
        'Take a screenshot of the current page',
        param_model=ScreenshotParams
    )
    async def take_screenshot(params: ScreenshotParams, browser_session):
        """Take a screenshot of the current page"""
        import base64
        from datetime import datetime

        # Get screenshot from browser
        screenshot = await browser_session.take_screenshot(full_page=params.full_page)

        # Save to file
        filename = f"screenshots/{params.filename}"
        os.makedirs("screenshots", exist_ok=True)

        with open(filename, "wb") as f:
            f.write(screenshot)

        # Create result
        result = {
            "filename": filename,
            "size": len(screenshot),
            "timestamp": datetime.now().isoformat(),
            "full_page": params.full_page
        }

        # Display confirmation in browser
        html = f"""
        <html>
        <head>
            <title>Screenshot Taken</title>
            <style>
                body {{ font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                .card {{ background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); text-align: center; }}
                h1 {{ color: #333; margin-bottom: 20px; }}
                .icon {{ font-size: 48px; margin-bottom: 20px; }}
                .info {{ color: #666; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="icon">📸</div>
                <h1>Screenshot Captured!</h1>
                <p class="info">Filename: {params.filename}</p>
                <p class="info">Size: {len(screenshot):,} bytes</p>
                <p class="info">Full Page: {params.full_page}</p>
                <p class="info">Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """

        await browser_session.evaluate(f"document.body.innerHTML = `{html}`;")
        return result

    # Add form filler tool
    @manager.tools.registry.action(
        'Automatically fill form fields with provided data',
        param_model=FormFillerParams
    )
    async def fill_form(params: FormFillerParams, browser_session):
        """Fill form fields automatically"""

        js_code = """
        (function(formData, shouldSubmit) {
            let filled = 0;
            let errors = [];

            for (const [key, value] of Object.entries(formData)) {
                // Try to find element by ID, name, or class
                let element = document.getElementById(key) ||
                             document.querySelector(`[name="${key}"]`) ||
                             document.querySelector(`.${key}`);

                if (element) {
                    if (element.type === 'checkbox') {
                        element.checked = value;
                    } else if (element.type === 'radio') {
                        element.checked = value;
                    } else {
                        element.value = value;
                    }
                    filled++;

                    // Trigger change event
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                } else {
                    errors.push(`Field not found: ${key}`);
                }
            }

            // Submit form if requested
            let submitted = false;
            if (shouldSubmit) {
                const form = document.querySelector('form');
                if (form) {
                    form.submit();
                    submitted = true;
                }
            }

            return {
                filled: filled,
                total: Object.keys(formData).length,
                errors: errors,
                submitted: submitted
            };
        })(""" + str(params.form_data) + """, """ + str(params.submit).lower() + """);
        """

        result = await browser_session.evaluate(js_code)
        return result

    # Add performance analyzer tool
    @manager.tools.registry.action(
        'Analyze page performance metrics',
        param_model=PerformanceAnalyzerParams
    )
    async def analyze_performance(params: PerformanceAnalyzerParams, browser_session):
        """Analyze page performance"""

        js_code = """
        (function() {
            const perf = window.performance;
            const timing = perf.timing;
            const navigation = perf.navigation;

            const metrics = {
                loadTime: timing.loadEventEnd - timing.navigationStart,
                domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                firstPaint: 0,
                firstContentfulPaint: 0,
                responseTime: timing.responseEnd - timing.requestStart,
                domInteractive: timing.domInteractive - timing.navigationStart,
                resourceCount: perf.getEntriesByType('resource').length
            };

            // Get paint timings
            const paintEntries = perf.getEntriesByType('paint');
            paintEntries.forEach(entry => {
                if (entry.name === 'first-paint') {
                    metrics.firstPaint = entry.startTime;
                } else if (entry.name === 'first-contentful-paint') {
                    metrics.firstContentfulPaint = entry.startTime;
                }
            });

            // Get largest contentful paint
            const lcpEntries = perf.getEntriesByType('largest-contentful-paint');
            if (lcpEntries.length > 0) {
                metrics.largestContentfulPaint = lcpEntries[lcpEntries.length - 1].startTime;
            }

            return {
                url: window.location.href,
                metrics: metrics,
                resources: perf.getEntriesByType('resource').map(r => ({
                    name: r.name,
                    duration: r.duration,
                    size: r.transferSize || 0,
                    type: r.initiatorType
                })).slice(0, 10), // Top 10 resources
                timestamp: new Date().toISOString()
            };
        })();
        """

        result = await browser_session.evaluate(js_code)

        # Create performance report
        metrics = result.get('metrics', {})
        report_html = f"""
        <html>
        <head>
            <title>Performance Analysis</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f7fa; }}
                h1 {{ color: #2c3e50; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
                .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
                .metric-label {{ color: #7f8c8d; margin-top: 5px; font-size: 14px; }}
                .good {{ color: #27ae60; }}
                .warning {{ color: #f39c12; }}
                .bad {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <h1>⚡ Performance Analysis Report</h1>
            <p>URL: {result.get('url', 'N/A')}</p>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value {('good' if metrics.get('loadTime', 0) < 3000 else 'warning' if metrics.get('loadTime', 0) < 5000 else 'bad')}">{metrics.get('loadTime', 0)}ms</div>
                    <div class="metric-label">Page Load Time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value {('good' if metrics.get('domContentLoaded', 0) < 2000 else 'warning' if metrics.get('domContentLoaded', 0) < 4000 else 'bad')}">{metrics.get('domContentLoaded', 0)}ms</div>
                    <div class="metric-label">DOM Content Loaded</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics.get('firstContentfulPaint', 0):.0f}ms</div>
                    <div class="metric-label">First Contentful Paint</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics.get('resourceCount', 0)}</div>
                    <div class="metric-label">Resources Loaded</div>
                </div>
            </div>
        </body>
        </html>
        """

        await browser_session.evaluate(f"document.body.innerHTML = `{report_html}`;")
        return result

    # Create LLM instance
    llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

    # Demonstrate the new tools
    task = """
    1. First, use count_tools to see how many tools we have now (including the new ones)
    2. Navigate to example.com
    3. Use analyze_performance to check the page performance
    4. Take a screenshot of the page
    """

    print("\n🚀 Running task with dynamically added tools...")
    agent = Agent(task=task, llm=llm, tools=manager.get_tools_instance())
    await agent.run()
    await agent.close()


async def demo_advanced_workflow():
    """Demonstrate an advanced workflow using multiple custom tools"""
    print("\n" + "="*60)
    print("DEMO: Advanced Multi-Tool Workflow")
    print("="*60)

    # Create custom tools manager
    manager = CustomToolsManager(include_defaults=True)

    # Create LLM instance
    llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

    # Complex task using multiple tools
    task = """
    Perform a comprehensive analysis of the Python.org website:
    1. Navigate to python.org
    2. Use extract_elements_advanced to find all buttons and links
    3. Monitor network activity for 5 seconds to see what requests are being made
    4. Count all available tools to show the power of our custom framework
    5. Provide a summary of your findings
    """

    print("\n🔬 Running comprehensive website analysis...")
    agent = Agent(task=task, llm=llm, tools=manager.get_tools_instance())
    await agent.run()
    await agent.close()


async def main():
    """Main demo function"""
    print("\n" + "="*80)
    print("BROWSER-USE CUSTOM TOOLS DEMONSTRATION")
    print("="*80)

    # Get user choice
    print("\nAvailable Demos:")
    print("1. Basic Custom Tools (tool counter, element extractor)")
    print("2. Dynamic Tool Addition (screenshot, form filler, performance)")
    print("3. Advanced Multi-Tool Workflow")
    print("4. Run All Demos")

    choice = input("\nSelect demo (1-4): ").strip()

    if choice == "1":
        await demo_basic_tools()
    elif choice == "2":
        await demo_dynamic_tools()
    elif choice == "3":
        await demo_advanced_workflow()
    elif choice == "4":
        await demo_basic_tools()
        await demo_dynamic_tools()
        await demo_advanced_workflow()
    else:
        print("Invalid choice. Running basic demo...")
        await demo_basic_tools()

    print("\n" + "="*80)
    print("DEMO COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())