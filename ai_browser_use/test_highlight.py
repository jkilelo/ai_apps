from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
import asyncio
import sys
import os
import io
from playwright.async_api import async_playwright

# Force UTF-8 encoding for stdout/stderr to handle emojis and non-ASCII
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Set UTF-8 as default encoding for the environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Add parent directory to path to import llm_gemini_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_gemini_client import get_client

load_dotenv(dotenv_path="./.env")


async def highlight_interactive_elements():
    """
    Simple script to highlight interactive elements on a webpage.
    """
    print("Starting browser to highlight interactive elements...")

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    # Navigate to example.com for testing
    url = "https://www.example.com"
    print(f"Navigating to {url}...")
    await page.goto(url, wait_until='networkidle')

    # JavaScript to detect and highlight interactive elements
    highlight_script = """
    () => {
        // Add styles for badges
        const style = document.createElement('style');
        style.textContent = `
            .element-badge {
                position: absolute;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 3px 7px;
                border-radius: 4px;
                z-index: 10000;
                pointer-events: none;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                font-family: Arial, sans-serif;
                min-width: 24px;
                text-align: center;
            }
            .highlighted-element {
                outline: 2px solid #667eea !important;
                outline-offset: 2px !important;
            }
        `;
        document.head.appendChild(style);

        // Find interactive elements
        const interactiveSelectors = 'a, button, input, textarea, select, [role="button"], [onclick]';
        const elements = document.querySelectorAll(interactiveSelectors);

        let count = 0;
        elements.forEach((el, index) => {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                count++;

                // Add highlight
                el.classList.add('highlighted-element');

                // Add badge
                const badge = document.createElement('div');
                badge.className = 'element-badge';
                badge.textContent = count;
                badge.style.left = rect.left + 'px';
                badge.style.top = Math.max(0, rect.top - 25) + 'px';
                badge.style.position = 'fixed';
                document.body.appendChild(badge);
            }
        });

        return count;
    }
    """

    # Apply highlighting
    count = await page.evaluate(highlight_script)
    print(f"✓ Highlighted {count} interactive elements")

    # Take screenshot
    screenshot_path = "highlighted_example.png"
    await page.screenshot(path=screenshot_path)
    print(f"✓ Screenshot saved: {screenshot_path}")

    # Keep browser open for 10 seconds to see the result
    print("\nBrowser will remain open for 10 seconds...")
    await asyncio.sleep(10)

    # Cleanup
    await browser.close()
    await playwright.stop()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(highlight_interactive_elements())