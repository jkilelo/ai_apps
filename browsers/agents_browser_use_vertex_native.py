"""
Browser Use with Vertex AI - Using Native Support
Browser_use has BUILT-IN support for Vertex AI through ChatGoogle!
This is the easiest way to use browser_use with your Vertex setup.
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import browser_use with native Google/Vertex support
from browser_use import Agent, Browser
from browser_use.llm.google.chat import ChatGoogle
from google.oauth2.credentials import Credentials
from google.genai.types import HttpOptions


# ==============================================================================
# OPTION 1: USE BROWSER_USE'S NATIVE VERTEX AI SUPPORT
# ==============================================================================

def create_vertex_llm():
    """
    Create a ChatGoogle instance configured for Vertex AI.
    This uses browser_use's NATIVE support for Vertex AI!
    """
    # Create ChatGoogle with Vertex AI configuration
    llm = ChatGoogle(
        model="gemini-2.0-flash",
        temperature=0.7,
        # Vertex AI specific parameters
        vertexai=True,  # Enable Vertex AI mode
        project=os.getenv("VERTEX_PROJECT_ID"),
        location=os.getenv("VERTEX_PROJECT_LOCATION", "us-central1"),
        http_options=HttpOptions(
            base_url=os.getenv("BASE_URL_VERTEX")
        ) if os.getenv("BASE_URL_VERTEX") else None,
        # You can also pass credentials directly if needed
        # credentials=Credentials("your-token")
    )
    
    return llm


# ==============================================================================
# READY-TO-USE EXAMPLES
# ==============================================================================

async def example_extract_news():
    """Extract news from a website using Vertex AI."""
    print("\n" + "=" * 70)
    print("EXTRACTING NEWS WITH BROWSER_USE + VERTEX AI (Native)")
    print("=" * 70)
    
    # Create agent with native Vertex AI support
    agent = Agent(
        task="Go to https://news.ycombinator.com and extract the titles of the top 3 stories",
        llm=create_vertex_llm(),
        browser=Browser(headless=True)
    )
    
    print("\n>> Starting browser agent with Vertex AI...")
    result = await agent.run()
    
    print("\n>> Extracted news:")
    print(result)
    
    return result


async def example_search_and_summarize():
    """Search Google and summarize results."""
    print("\n" + "=" * 70)
    print("SEARCH AND SUMMARIZE WITH BROWSER_USE + VERTEX AI")
    print("=" * 70)
    
    agent = Agent(
        task="Go to google.com, search for 'vertex ai gemini models', and summarize what you find about the latest models",
        llm=create_vertex_llm(),
        browser=Browser(headless=False)  # Show browser window
    )
    
    print("\n>> Searching and summarizing...")
    result = await agent.run()
    
    print("\n>> Summary:")
    print(result)
    
    return result


async def example_website_analysis():
    """Analyze a website's content and structure."""
    print("\n" + "=" * 70)
    print("WEBSITE ANALYSIS WITH BROWSER_USE + VERTEX AI")
    print("=" * 70)
    
    agent = Agent(
        task="""Go to https://www.python.org and provide:
        1. The main headline
        2. Latest Python version mentioned
        3. Any upcoming events or announcements""",
        llm=create_vertex_llm(),
        browser=Browser(headless=True)
    )
    
    print("\n>> Analyzing Python.org...")
    result = await agent.run()
    
    print("\n>> Analysis:")
    print(result)
    
    return result


async def example_interactive_task(url: str, task: str):
    """Run a custom browser task with Vertex AI."""
    print("\n" + "=" * 70)
    print("CUSTOM BROWSER TASK WITH VERTEX AI")
    print("=" * 70)
    
    agent = Agent(
        task=f"Go to {url} and {task}",
        llm=create_vertex_llm(),
        browser=Browser(headless=False)  # Show browser for interactive tasks
    )
    
    print(f"\n>> URL: {url}")
    print(f">> Task: {task}")
    print(">> Running browser agent...")
    
    result = await agent.run()
    
    print("\n>> Result:")
    print(result)
    
    return result


# ==============================================================================
# MAIN DEMO WITH MENU
# ==============================================================================

def main():
    """Main demo showing browser_use with native Vertex AI support."""
    
    print("=" * 80)
    print("BROWSER USE WITH VERTEX AI - NATIVE SUPPORT")
    print("=" * 80)
    print("\nBrowser_use has BUILT-IN support for Vertex AI!")
    print("Using ChatGoogle class with vertexai=True parameter.")
    
    # Check environment variables
    print("\n>> Checking Vertex AI configuration...")
    required_vars = ["VERTEX_PROJECT_ID", "VERTEX_PROJECT_LOCATION"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"\n[WARNING] Missing environment variables: {', '.join(missing)}")
        print("\nPlease set these in your .env file:")
        print("VERTEX_PROJECT_ID=your-project-id")
        print("VERTEX_PROJECT_LOCATION=us-central1")
        print("\nAnd run: gcloud auth application-default login")
        
        # Ask if user wants to continue anyway
        cont = input("\nContinue anyway? (y/n): ")
        if cont.lower() != 'y':
            return
    else:
        print("   [OK] Vertex AI configuration found")
        print(f"   Project: {os.getenv('VERTEX_PROJECT_ID')}")
        print(f"   Location: {os.getenv('VERTEX_PROJECT_LOCATION')}")
    
    # Menu
    print("\n" + "-" * 70)
    print("BROWSER AUTOMATION OPTIONS:")
    print("-" * 70)
    print("1. Extract top news from Hacker News")
    print("2. Search Google and summarize results")
    print("3. Analyze Python.org website")
    print("4. Custom task (you provide URL and instructions)")
    print("5. Run all examples")
    print("0. Exit")
    
    choice = input("\nSelect option (0-5): ")
    
    # Execute selected option
    try:
        if choice == "1":
            asyncio.run(example_extract_news())
        
        elif choice == "2":
            asyncio.run(example_search_and_summarize())
        
        elif choice == "3":
            asyncio.run(example_website_analysis())
        
        elif choice == "4":
            url = input("\nEnter URL: ")
            task = input("What should the browser do? ")
            asyncio.run(example_interactive_task(url, task))
        
        elif choice == "5":
            print("\n>> Running all examples...")
            asyncio.run(example_extract_news())
            print("\n" + "-" * 70)
            asyncio.run(example_website_analysis())
            print("\n" + "-" * 70)
            # Skip search example in batch mode to avoid too many browser windows
            print("\n[Skipping interactive search example in batch mode]")
        
        elif choice == "0":
            print("\nExiting...")
            return
        
        else:
            print("\nInvalid choice.")
    
    except Exception as e:
        print(f"\n[ERROR] Task failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify Vertex AI credentials: gcloud auth application-default login")
        print("3. Ensure browser_use is installed: pip install browser-use")
        print("4. Check if Playwright browsers are installed: playwright install chromium")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("Browser_use with native Vertex AI support works great!")
    print("=" * 80)


if __name__ == "__main__":
    main()