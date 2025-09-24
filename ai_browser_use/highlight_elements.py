from browser_use import Agent, ChatGoogle, Browser, Controller
from dotenv import load_dotenv
import asyncio
import sys
import os
import io
from playwright.async_api import Page
from typing import List, Dict, Any

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


class ChatGoogleInjected(ChatGoogle):
    """
    Minimal injector that overrides ChatGoogle's get_client() method
    to use the get_client() from llm_gemini_client.py instead.
    """
    def get_client(self):
        """Override to use our centralized get_client() instead."""
        return get_client()


class InteractiveElementHighlighter:
    """
    A class to detect and highlight interactive elements on a webpage
    similar to browser_use's element detection feature.
    """

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        """Initialize browser and context."""
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def navigate_to_url(self, url: str):
        """Navigate to a specific URL."""
        await self.page.goto(url, wait_until='networkidle')
        await asyncio.sleep(2)  # Wait for dynamic content

    async def detect_interactive_elements(self) -> List[Dict[str, Any]]:
        """
        Detect all interactive elements on the current page.
        Returns a list of elements with their properties.
        """
        # JavaScript to detect interactive elements
        detect_script = """
        () => {
            const interactiveSelectors = [
                'a', 'button', 'input', 'textarea', 'select',
                '[role="button"]', '[role="link"]', '[role="textbox"]',
                '[onclick]', '[ng-click]', '[data-click]',
                '.btn', '.button', '.link'
            ];

            const elements = [];
            const seen = new Set();

            interactiveSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    if (!seen.has(el) && el.offsetWidth > 0 && el.offsetHeight > 0) {
                        seen.add(el);
                        const rect = el.getBoundingClientRect();
                        elements.push({
                            tagName: el.tagName.toLowerCase(),
                            text: el.innerText?.substring(0, 50) || el.value || el.placeholder || '',
                            type: el.type || '',
                            href: el.href || '',
                            id: el.id || '',
                            className: el.className || '',
                            rect: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height,
                                top: rect.top,
                                left: rect.left
                            },
                            isVisible: rect.width > 0 && rect.height > 0,
                            selector: el.id ? `#${el.id}` :
                                     el.className ? `.${el.className.split(' ')[0]}` :
                                     el.tagName.toLowerCase()
                        });
                    }
                });
            });

            return elements;
        }
        """

        elements = await self.page.evaluate(detect_script)
        return elements

    async def highlight_elements_with_numbers(self, elements: List[Dict[str, Any]]):
        """
        Add numbered labels to interactive elements on the page,
        similar to the browser_use highlighting style.
        """
        # CSS for the numbered labels
        label_css = """
        .browser-use-label {
            position: absolute;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 12px;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 3px;
            z-index: 10000;
            pointer-events: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            font-family: Arial, sans-serif;
            min-width: 20px;
            text-align: center;
        }
        """

        # Inject CSS
        await self.page.add_style_tag(content=label_css)

        # JavaScript to add numbered labels
        highlight_script = """
        (elements) => {
            // Remove existing labels
            document.querySelectorAll('.browser-use-label').forEach(el => el.remove());

            elements.forEach((element, index) => {
                if (element.isVisible) {
                    const label = document.createElement('div');
                    label.className = 'browser-use-label';
                    label.textContent = index + 1;
                    label.style.left = element.rect.left + 'px';
                    label.style.top = element.rect.top + 'px';

                    // Adjust position for better visibility
                    if (element.rect.top > 20) {
                        label.style.top = (element.rect.top - 18) + 'px';
                    }

                    document.body.appendChild(label);

                    // Also highlight the element itself with a border
                    const selector = element.selector;
                    try {
                        const el = document.querySelector(selector);
                        if (el) {
                            el.style.outline = '2px solid #667eea';
                            el.style.outlineOffset = '1px';
                        }
                    } catch (e) {
                        console.error('Error highlighting element:', e);
                    }
                }
            });

            return elements.length;
        }
        """

        count = await self.page.evaluate(highlight_script, elements)
        return count

    async def capture_screenshot(self, filename: str = "highlighted_page.png"):
        """Capture a screenshot of the page with highlighted elements."""
        await self.page.screenshot(path=filename, full_page=False)
        print(f"Screenshot saved as {filename}")

    async def extract_element_info(self, elements: List[Dict[str, Any]]) -> str:
        """
        Format element information for display or analysis.
        """
        info = []
        for i, element in enumerate(elements, 1):
            if element['isVisible']:
                info.append(f"{i}. {element['tagName']}")
                if element['text']:
                    info.append(f"   Text: {element['text']}")
                if element['type']:
                    info.append(f"   Type: {element['type']}")
                if element['href']:
                    info.append(f"   Link: {element['href']}")
                info.append("")

        return "\n".join(info)

    async def close(self):
        """Close browser and clean up."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()


async def main_with_highlighting():
    """
    Main function that demonstrates element detection and highlighting.
    """
    highlighter = InteractiveElementHighlighter(headless=False)

    try:
        # Initialize browser
        await highlighter.initialize()

        # Navigate to the target URL
        url = "https://uat01.citi.com"  # You can change this to any URL
        print(f"Navigating to {url}...")
        await highlighter.navigate_to_url(url)

        # Detect interactive elements
        print("Detecting interactive elements...")
        elements = await highlighter.detect_interactive_elements()
        print(f"Found {len(elements)} interactive elements")

        # Highlight elements with numbers
        print("Highlighting elements...")
        count = await highlighter.highlight_elements_with_numbers(elements)
        print(f"Highlighted {count} visible elements")

        # Extract and display element information
        element_info = await highlighter.extract_element_info(elements)
        print("\nInteractive Elements Found:")
        print("=" * 50)
        print(element_info)

        # Take a screenshot
        await highlighter.capture_screenshot("highlighted_elements.png")

        # Keep browser open for viewing
        print("\nPress Enter to close the browser...")
        await asyncio.sleep(10)  # Keep open for 10 seconds

    finally:
        await highlighter.close()


async def main_with_agent():
    """
    Alternative approach using browser_use Agent with custom task.
    """
    llm = ChatGoogleInjected(model="gemini-2.5-flash")

    # Create a task that identifies and marks interactive elements
    task = """
    Navigate to https://uat01.citi.com and:
    1. Identify all interactive elements (buttons, links, inputs, etc.)
    2. Create a numbered list of all interactive elements
    3. Take a screenshot showing the elements
    4. Return a summary of what interactive elements were found
    """

    browser = Browser(headless=False)
    agent = Agent(task=task, llm=llm, browser=browser)

    # Run the agent
    result = await agent.run()
    print("Agent Result:", result)


if __name__ == "__main__":
    # Choose which approach to use
    print("Select mode:")
    print("1. Custom highlighting (programmatic)")
    print("2. Agent-based detection (AI-powered)")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "2":
        asyncio.run(main_with_agent())
    else:
        asyncio.run(main_with_highlighting())