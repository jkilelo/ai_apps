import io
import subprocess
import asyncio
import sys
import os

from dotenv import load_dotenv

# ensure browser_use is installed
try:
    from browser_use import Agent, ChatGoogle
except ImportError:
    print("browser_use package not found. Installing ... ")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "browser_use"])
    from browser_use import Agent, ChatGoogle

# Force UTF-8 encoding for stdout/stderr to handle emojis and non-ASCII
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Set UTF-8 as default encoding for the environment
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

# Add parent directory to path to import llm_gemini_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_service_layer.clients.google_client import get_client as gclient
from ai_service_layer.clients.google_client import get_base_params

load_dotenv(dotenv_path="./.env")


class ChatGoogleInjected(ChatGoogle):
    """
    Minimal injector that overrides ChatGoogle's get_client() method
    to use the get_client() from google_client.py instead.

    This allows us to use all of ChatGoogle's functionality while
    replacing only the client instantiation.
    """

    def get_client(self):
        """Override to use our centralized get_client() instead."""
        return gclient()


async def main():
    # Use the injected version with minimal code change
    # llm = ChatGoogleInjected(model="gemini-2.5-pro")
    llm = ChatGoogle(model="gemini-2.5-pro", **get_base_params())
    task = (
        """
### **Task for LLM Browser Automation**

Navigate to **uat.citi.com**.

Once on the page, perform the following actions:

* **Exhaustive Element Detection:** Systematically scroll through the entire page. Use a **20% overlap** between scroll positions to ensure all elements are captured.
* **Element Categorization:** Identify and categorize all interactive elements on the page, including but not limited to **navigation, buttons, media, forms, and content**.
* **Automated Testing and Analysis:**
    * **Element Prioritization:** Rank elements based on their importance or accessibility.
    * **Screenshot Capture:** Take visual snapshots of key elements.
    * **Interaction Testing:** Automatically test if elements are clickable or functional.
    * **Accessibility Scoring:** Rate each element's WCAG compliance.
    * **Heat Map Generation:** Create a visual density map of interactive elements.
* **Comprehensive Detection Strategies:** To ensure no elements are missed, employ the following advanced strategies:
    * **Multiple Detection Passes:** Run detection multiple times with different strategies.
    * **Dynamic Content Handling:** Wait for lazy-loading content and handle infinite scrolling.
    * **Shadow DOM Detection:** Scan for elements within the Shadow DOM.
    * **Event Listener Detection:** Identify elements with attached event listeners.
    * **Accessibility Tree Analysis:** Use the accessibility tree to locate interactive elements.
    * **DOM Mutation Observation:** Monitor for elements that appear after user interactions.
    * **Viewport and User Agent Variation:** Test different viewport sizes and user agents to reveal responsive or device-specific elements.
    * **Interaction Simulation:** Simulate hover, focus, and click events to reveal hidden elements.
    * **Frame/IFrame Detection:** Recursively scan all frames and iframes.
    * **CSS Analysis:** Parse CSS to find elements with pseudo-classes like `:hover` and `:focus`.
        """
    )
    agent = Agent(task=task, llm=llm)
    await agent.run()
    # clean up the agent
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
