from browser_use import Agent, ChatGoogle, Browser, Controller
from browser_use.dom.views import DOMSnapshot
from dotenv import load_dotenv
import asyncio
import sys
import os
import io

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


class BrowserUseElementDetector:
    """
    Uses browser_use's built-in element detection and annotation features.
    """

    def __init__(self):
        self.llm = ChatGoogleInjected(model="gemini-2.5-flash")
        self.browser = None
        self.controller = None

    async def detect_and_annotate(self, url: str):
        """
        Use browser_use to detect and annotate interactive elements.
        """
        # Initialize browser with visual mode
        self.browser = Browser(
            headless=False,
            disable_security=True,  # For testing purposes
            extra_chromium_args=['--no-sandbox']
        )

        # Create controller for direct browser control
        self.controller = Controller()

        try:
            # Get browser context
            context = await self.browser._get_browser_context()
            page = await context.new_page()

            # Navigate to URL
            await page.goto(url, wait_until='networkidle')
            await asyncio.sleep(2)

            # Take a DOM snapshot
            dom_snapshot = await self._get_dom_snapshot(page)

            # Get interactive elements using browser_use's detection
            elements = await self._extract_interactive_elements(page)

            # Annotate the page with numbered badges
            await self._annotate_page_with_badges(page, elements)

            # Take screenshot with annotations
            screenshot_path = "annotated_elements.png"
            await page.screenshot(path=screenshot_path, full_page=False)
            print(f"Screenshot saved: {screenshot_path}")

            # Print element summary
            self._print_element_summary(elements)

            # Keep browser open for inspection
            print("\nBrowser will remain open for 15 seconds...")
            await asyncio.sleep(15)

        finally:
            if self.browser:
                await self.browser.close()

    async def _get_dom_snapshot(self, page):
        """
        Get a DOM snapshot using browser_use's method.
        """
        # Execute browser_use's DOM extraction script
        dom_script = """
        () => {
            const elements = [];
            const allElements = document.querySelectorAll('*');

            allElements.forEach((el, index) => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    elements.push({
                        index: index,
                        tagName: el.tagName.toLowerCase(),
                        attributes: Object.fromEntries([...el.attributes].map(a => [a.name, a.value])),
                        text: el.textContent?.trim().substring(0, 100),
                        bbox: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        }
                    });
                }
            });

            return elements;
        }
        """

        return await page.evaluate(dom_script)

    async def _extract_interactive_elements(self, page):
        """
        Extract interactive elements using browser_use's detection logic.
        """
        # This mimics browser_use's interactive element detection
        detection_script = """
        () => {
            const interactiveElements = [];
            let elementIndex = 0;

            // Define what makes an element interactive
            const interactiveSelectors = [
                'a[href]',
                'button',
                'input:not([type="hidden"])',
                'textarea',
                'select',
                '[role="button"]',
                '[role="link"]',
                '[role="tab"]',
                '[role="menuitem"]',
                '[onclick]',
                '[contenteditable="true"]',
                'summary'
            ];

            // Find all interactive elements
            const selector = interactiveSelectors.join(', ');
            const elements = document.querySelectorAll(selector);

            elements.forEach(el => {
                const rect = el.getBoundingClientRect();
                const isVisible = rect.width > 0 &&
                                 rect.height > 0 &&
                                 rect.top < window.innerHeight &&
                                 rect.bottom > 0 &&
                                 rect.left < window.innerWidth &&
                                 rect.right > 0;

                if (isVisible) {
                    elementIndex++;
                    interactiveElements.push({
                        index: elementIndex,
                        tagName: el.tagName.toLowerCase(),
                        type: el.type || '',
                        text: (el.textContent || el.value || el.placeholder || '').trim().substring(0, 50),
                        href: el.href || '',
                        role: el.getAttribute('role') || '',
                        ariaLabel: el.getAttribute('aria-label') || '',
                        bbox: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            top: rect.top,
                            left: rect.left
                        }
                    });
                }
            });

            return interactiveElements;
        }
        """

        return await page.evaluate(detection_script)

    async def _annotate_page_with_badges(self, page, elements):
        """
        Add browser_use-style numbered badges to elements.
        """
        annotation_script = """
        (elements) => {
            // Remove any existing annotations
            document.querySelectorAll('.browser-use-annotation').forEach(el => el.remove());

            // Create style for badges
            const style = document.createElement('style');
            style.textContent = `
                .browser-use-annotation {
                    position: fixed;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 3px 6px;
                    border-radius: 4px;
                    z-index: 999999;
                    pointer-events: none;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    min-width: 22px;
                    text-align: center;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    animation: fadeIn 0.3s ease-in;
                }

                @keyframes fadeIn {
                    from { opacity: 0; transform: scale(0.8); }
                    to { opacity: 1; transform: scale(1); }
                }

                .browser-use-highlight {
                    outline: 2px solid #6366f1 !important;
                    outline-offset: 2px !important;
                    background-color: rgba(99, 102, 241, 0.1) !important;
                    transition: all 0.3s ease !important;
                }
            `;
            document.head.appendChild(style);

            // Add badges for each element
            elements.forEach((element) => {
                const badge = document.createElement('div');
                badge.className = 'browser-use-annotation';
                badge.textContent = element.index;

                // Position badge at top-left corner of element
                badge.style.left = element.bbox.left + 'px';
                badge.style.top = Math.max(0, element.bbox.top - 25) + 'px';

                document.body.appendChild(badge);

                // Also highlight the element
                const xpath = `//body//*[${element.index}]`;
                const els = document.querySelectorAll(element.tagName);
                els.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (Math.abs(rect.left - element.bbox.left) < 2 &&
                        Math.abs(rect.top - element.bbox.top) < 2) {
                        el.classList.add('browser-use-highlight');
                    }
                });
            });

            return elements.length;
        }
        """

        return await page.evaluate(annotation_script, elements)

    def _print_element_summary(self, elements):
        """
        Print a summary of detected elements.
        """
        print("\n" + "=" * 60)
        print("INTERACTIVE ELEMENTS DETECTED")
        print("=" * 60)

        # Group elements by type
        by_type = {}
        for el in elements:
            tag = el['tagName']
            if tag not in by_type:
                by_type[tag] = []
            by_type[tag].append(el)

        # Print summary
        for tag, items in by_type.items():
            print(f"\n{tag.upper()} ({len(items)} found):")
            for item in items[:5]:  # Show first 5 of each type
                text = item['text'][:40] + "..." if len(item['text']) > 40 else item['text']
                print(f"  [{item['index']}] {text}")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")

        print("\n" + "=" * 60)
        print(f"TOTAL: {len(elements)} interactive elements")
        print("=" * 60)


async def main():
    """
    Main function to run the element detector.
    """
    detector = BrowserUseElementDetector()

    # URL to analyze
    url = input("Enter URL to analyze (default: https://www.example.com): ").strip()
    if not url:
        url = "https://uat.citi.com"

    print(f"\nAnalyzing: {url}")
    print("This will open a browser window and annotate interactive elements...")

    await detector.detect_and_annotate(url)


if __name__ == "__main__":
    asyncio.run(main())