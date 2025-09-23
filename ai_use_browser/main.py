from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
import asyncio
import sys
import os

# Add parent directory to path to import llm_gemini_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_gemini_client import get_client

load_dotenv(dotenv_path="./.env")


class ChatGoogleInjected(ChatGoogle):
    """
    Minimal injector that overrides ChatGoogle's get_client() method
    to use the get_client() from llm_gemini_client.py instead.

    This allows us to use all of ChatGoogle's functionality while
    replacing only the client instantiation.
    """

    def get_client(self):
        """Override to use our centralized get_client() instead."""
        return get_client()


async def main():
    # Use the injected version with minimal code change
    llm = ChatGoogleInjected(model="gemini-2.5-flash")
    task = "navigate to uat01.citi.com and extract all interactive elements on the homepage"
    agent = Agent(task=task, llm=llm)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())