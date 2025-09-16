"""
Browser Use Vertex AI Integration
This module provides a custom LLM wrapper to use browser_use with your Vertex AI client.
"""

import os
import sys
import asyncio
from typing import Any, TypeVar, overload
from dataclasses import dataclass
from pydantic import BaseModel

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your Vertex client
from agents.browser_use.instantiate_llm_client import initialize_client

# Import browser_use components
from browser_use import Agent, Browser
from browser_use.llm.base import BaseChatModel
from browser_use.llm.messages import BaseMessage, SystemMessage, UserMessage, AIMessage
from browser_use.llm.views import ChatInvokeCompletion, ChatInvokeUsage

T = TypeVar('T', bound=BaseModel)


@dataclass
class ChatVertexAI(BaseChatModel):
    """
    Custom Vertex AI chat model for browser_use.
    This wrapper allows browser_use to work with your existing Vertex AI client.
    """
    
    model: str = "gemini-2.0-flash"
    temperature: float = 0.7
    
    # Cache the client
    _client: Any = None
    
    @property
    def provider(self) -> str:
        return "vertex_ai"
    
    @property
    def name(self) -> str:
        return f"vertex-{self.model}"
    
    def get_client(self):
        """Get or initialize the Vertex AI client."""
        if self._client is None:
            self._client = initialize_client()
        return self._client
    
    def _messages_to_prompt(self, messages: list[BaseMessage]) -> str:
        """Convert browser_use messages to a single prompt for Vertex AI."""
        prompt_parts = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                prompt_parts.append(f"System: {msg.content}")
            elif isinstance(msg, UserMessage):
                prompt_parts.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                prompt_parts.append(f"Assistant: {msg.content}")
            else:
                # Handle any other message types
                prompt_parts.append(f"{msg.role}: {msg.content}")
        
        return "\n\n".join(prompt_parts)
    
    @overload
    async def ainvoke(
        self, messages: list[BaseMessage], output_format: None = None
    ) -> ChatInvokeCompletion[str]: ...
    
    @overload
    async def ainvoke(
        self, messages: list[BaseMessage], output_format: type[T]
    ) -> ChatInvokeCompletion[T]: ...
    
    async def ainvoke(
        self, 
        messages: list[BaseMessage], 
        output_format: type[T] | None = None
    ) -> ChatInvokeCompletion[T] | ChatInvokeCompletion[str]:
        """
        Invoke the Vertex AI model asynchronously.
        
        Args:
            messages: List of chat messages from browser_use
            output_format: Optional Pydantic model for structured output
        
        Returns:
            ChatInvokeCompletion with the response
        """
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)
        
        # If structured output is requested, add instructions
        if output_format:
            schema_str = output_format.model_json_schema()
            prompt += f"\n\nPlease respond with valid JSON matching this schema:\n{schema_str}"
        
        # Make the API call
        try:
            # Run synchronous call in executor
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(
                None,
                self._call_vertex_sync,
                prompt
            )
            
            # Parse structured output if needed
            if output_format:
                import json
                try:
                    # Try to extract JSON from the response
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        json_data = json.loads(json_str)
                        result = output_format(**json_data)
                    else:
                        # Fallback: try to parse the entire response
                        json_data = json.loads(response_text)
                        result = output_format(**json_data)
                except (json.JSONDecodeError, ValueError) as e:
                    # If parsing fails, return raw text
                    print(f"Warning: Could not parse structured output: {e}")
                    return ChatInvokeCompletion(
                        output=response_text,
                        raw_response=response_text,
                        usage=self._get_usage_estimate(prompt, response_text)
                    )
            else:
                result = response_text
            
            return ChatInvokeCompletion(
                output=result,
                raw_response=response_text,
                usage=self._get_usage_estimate(prompt, response_text)
            )
            
        except Exception as e:
            raise RuntimeError(f"Vertex AI call failed: {str(e)}")
    
    def _call_vertex_sync(self, prompt: str) -> str:
        """Synchronous call to Vertex AI."""
        client = self.get_client()
        
        # Call Vertex AI using your client format
        response = client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        
        return response.text
    
    def _get_usage_estimate(self, prompt: str, response: str) -> ChatInvokeUsage:
        """Estimate token usage (rough approximation)."""
        # Rough token estimation: ~4 characters per token
        prompt_tokens = len(prompt) // 4
        completion_tokens = len(response) // 4
        
        return ChatInvokeUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            prompt_cached_tokens=None,
            prompt_cache_creation_tokens=None,
            prompt_image_tokens=None
        )


# ==============================================================================
# BROWSER USE EXAMPLES WITH VERTEX AI
# ==============================================================================

async def example_web_search():
    """Example: Use browser_use to search the web with Vertex AI."""
    print("\n" + "=" * 60)
    print("BROWSER USE - WEB SEARCH EXAMPLE WITH VERTEX AI")
    print("=" * 60)
    
    # Create custom Vertex AI LLM
    llm = ChatVertexAI(
        model="gemini-2.0-flash",
        temperature=0.7
    )
    
    # Create browser_use agent with Vertex AI
    agent = Agent(
        task="Search for 'browser automation with AI' and summarize the top result",
        llm=llm,
        browser=Browser(headless=True)  # Run in headless mode
    )
    
    # Run the agent
    print("\n>> Starting browser automation task...")
    result = await agent.run()
    
    print("\n>> Task completed!")
    print(f"Result: {result}")
    
    return result


async def example_form_filling():
    """Example: Use browser_use to fill a form with Vertex AI."""
    print("\n" + "=" * 60)
    print("BROWSER USE - FORM FILLING EXAMPLE WITH VERTEX AI")
    print("=" * 60)
    
    # Create custom Vertex AI LLM
    llm = ChatVertexAI(
        model="gemini-2.0-flash",
        temperature=0.5
    )
    
    # Create browser_use agent
    agent = Agent(
        task="Go to https://www.example.com and describe what you see",
        llm=llm,
        browser=Browser(headless=False)  # Show browser window
    )
    
    # Run the agent
    print("\n>> Starting browser task...")
    result = await agent.run()
    
    print("\n>> Task completed!")
    print(f"Result: {result}")
    
    return result


async def example_data_extraction():
    """Example: Extract data from a website using Vertex AI."""
    print("\n" + "=" * 60)
    print("BROWSER USE - DATA EXTRACTION WITH VERTEX AI")
    print("=" * 60)
    
    # Create custom Vertex AI LLM
    llm = ChatVertexAI(
        model="gemini-2.0-flash",
        temperature=0.3  # Lower temperature for more precise extraction
    )
    
    # Create browser_use agent
    agent = Agent(
        task="Go to https://news.ycombinator.com and get the titles of the top 3 stories",
        llm=llm,
        browser=Browser(headless=True)
    )
    
    # Run the agent
    print("\n>> Extracting data from Hacker News...")
    result = await agent.run()
    
    print("\n>> Extraction completed!")
    print(f"Top stories: {result}")
    
    return result


def run_browser_use_demo():
    """Run all browser_use examples with Vertex AI."""
    print("\n" + "=" * 80)
    print("BROWSER USE WITH VERTEX AI - DEMO")
    print("=" * 80)
    
    print("\nThis demo shows how to use browser_use with your Vertex AI client.")
    print("Browser_use is an AI agent that can control web browsers to perform tasks.")
    
    # Check if Vertex client works
    print("\n>> Testing Vertex AI client...")
    try:
        client = initialize_client()
        test_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'Vertex AI ready for browser automation!'"
        )
        print(f"   Vertex AI says: {test_response.text}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   Please configure your Vertex AI credentials first.")
        return
    
    # Menu
    print("\n" + "-" * 60)
    print("Choose a browser_use example to run:")
    print("1. Web Search - Search and summarize results")
    print("2. Website Description - Navigate and describe a page")
    print("3. Data Extraction - Extract data from Hacker News")
    print("4. Run all examples")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-4): ")
    
    # Run selected example
    if choice == "1":
        asyncio.run(example_web_search())
    elif choice == "2":
        asyncio.run(example_form_filling())
    elif choice == "3":
        asyncio.run(example_data_extraction())
    elif choice == "4":
        print("\nRunning all examples...")
        asyncio.run(example_web_search())
        asyncio.run(example_form_filling())
        asyncio.run(example_data_extraction())
    elif choice == "0":
        print("Exiting...")
    else:
        print("Invalid choice. Please run again.")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    # Run the demo
    run_browser_use_demo()