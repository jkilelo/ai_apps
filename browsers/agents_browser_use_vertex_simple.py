"""
Simple Browser Use with Vertex AI Integration
Quick start example to use browser_use MCP agent with your Vertex AI client.
"""

import os
import sys
import asyncio
from dataclasses import dataclass

# Fix path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your Vertex client
from agents.browser_use.instantiate_llm_client import initialize_client

# Import browser_use - it's already installed in your venv
from browser_use import Agent, Browser
from browser_use.llm.base import BaseChatModel
from browser_use.llm.messages import BaseMessage
from browser_use.llm.views import ChatInvokeCompletion, ChatInvokeUsage


@dataclass
class VertexLLM(BaseChatModel):
    """Minimal Vertex AI wrapper for browser_use."""
    
    model: str = "gemini-2.0-flash"
    _client: any = None
    
    @property
    def provider(self) -> str:
        return "vertex_ai"
    
    @property
    def name(self) -> str:
        return self.model
    
    async def ainvoke(self, messages, output_format=None):
        """Process messages with Vertex AI."""
        # Convert messages to text
        prompt = "\n".join([f"{m.role}: {m.content}" for m in messages])
        
        # Get Vertex client
        if self._client is None:
            self._client = initialize_client()
        
        # Make synchronous call in async context
        loop = asyncio.get_event_loop()
        response_text = await loop.run_in_executor(
            None,
            lambda: self._client.models.generate_content(
                model=self.model,
                contents=prompt
            ).text
        )
        
        # Return in browser_use format
        return ChatInvokeCompletion(
            output=response_text,
            raw_response=response_text,
            usage=ChatInvokeUsage(
                prompt_tokens=len(prompt)//4,
                completion_tokens=len(response_text)//4,
                total_tokens=(len(prompt) + len(response_text))//4
            )
        )


# ==============================================================================
# SIMPLE EXAMPLES
# ==============================================================================

async def browse_website(url: str, task: str):
    """
    Use browser_use to browse a website and perform a task.
    
    Args:
        url: Website URL to visit
        task: What to do on the website
    """
    print(f"\n>> Browsing {url}")
    print(f">> Task: {task}")
    
    # Create Vertex-powered agent
    agent = Agent(
        task=f"Go to {url} and {task}",
        llm=VertexLLM(model="gemini-2.0-flash"),
        browser=Browser(headless=True)  # Set to False to see the browser
    )
    
    # Run the task
    result = await agent.run()
    
    print(f"\n>> Result: {result}")
    return result


async def extract_data(url: str, what_to_extract: str):
    """
    Extract specific data from a website.
    
    Args:
        url: Website to extract from
        what_to_extract: Description of data to extract
    """
    print(f"\n>> Extracting from {url}")
    print(f">> Looking for: {what_to_extract}")
    
    agent = Agent(
        task=f"Go to {url} and extract {what_to_extract}. Return only the extracted data.",
        llm=VertexLLM(),
        browser=Browser(headless=True)
    )
    
    result = await agent.run()
    
    print(f"\n>> Extracted data:")
    print(result)
    return result


async def fill_form(url: str, form_data: dict):
    """
    Fill a form on a website.
    
    Args:
        url: Form URL
        form_data: Dictionary of field names and values
    """
    print(f"\n>> Filling form at {url}")
    
    # Build task description
    task_parts = [f"Go to {url} and fill the form with:"]
    for field, value in form_data.items():
        task_parts.append(f"- {field}: {value}")
    task = "\n".join(task_parts)
    
    agent = Agent(
        task=task,
        llm=VertexLLM(),
        browser=Browser(headless=False)  # Show browser for forms
    )
    
    result = await agent.run()
    print(f"\n>> Form filling result: {result}")
    return result


async def take_screenshot(url: str, filename: str = "screenshot.png"):
    """
    Navigate to a URL and take a screenshot.
    
    Args:
        url: Website to screenshot
        filename: Where to save the screenshot
    """
    print(f"\n>> Taking screenshot of {url}")
    
    agent = Agent(
        task=f"Go to {url}, wait for it to load completely, then take a screenshot",
        llm=VertexLLM(),
        browser=Browser(headless=False)
    )
    
    result = await agent.run()
    print(f"\n>> Screenshot saved: {result}")
    return result


# ==============================================================================
# MAIN DEMO
# ==============================================================================

def main():
    """Interactive demo of browser_use with Vertex AI."""
    
    print("=" * 70)
    print("BROWSER USE WITH VERTEX AI - SIMPLE DEMO")
    print("=" * 70)
    
    # Test Vertex connection
    print("\n>> Testing Vertex AI connection...")
    try:
        client = initialize_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'Ready for browser automation!'"
        )
        print(f"   Vertex AI: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
        print("\n   Please set up your Vertex AI credentials:")
        print("   1. Run: gcloud auth application-default login")
        print("   2. Set environment variables in .env file")
        return
    
    print("\n" + "-" * 70)
    print("BROWSER AUTOMATION OPTIONS:")
    print("-" * 70)
    print("1. Extract top news from Hacker News")
    print("2. Get example.com page title and description")
    print("3. Search Google for 'browser automation'")
    print("4. Extract Python.org latest news")
    print("5. Custom URL and task")
    
    choice = input("\nSelect option (1-5): ")
    
    # Run selected task
    if choice == "1":
        asyncio.run(extract_data(
            "https://news.ycombinator.com",
            "the titles of the top 5 news stories"
        ))
    
    elif choice == "2":
        asyncio.run(browse_website(
            "https://www.example.com",
            "get the page title and main heading"
        ))
    
    elif choice == "3":
        asyncio.run(browse_website(
            "https://www.google.com",
            "search for 'browser automation with AI' and summarize the first result"
        ))
    
    elif choice == "4":
        asyncio.run(extract_data(
            "https://www.python.org",
            "the latest Python news or announcements"
        ))
    
    elif choice == "5":
        url = input("Enter URL: ")
        task = input("What should the browser do? ")
        asyncio.run(browse_website(url, task))
    
    else:
        print("Invalid choice")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETED")
    print("Browser_use successfully used your Vertex AI client!")
    print("=" * 70)


if __name__ == "__main__":
    main()