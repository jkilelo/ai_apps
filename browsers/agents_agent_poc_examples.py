"""
POC Agent Examples using different SDKs with Google Vertex AI client
This file demonstrates how to create agents using different SDKs with your existing LLM client
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use.instantiate_llm_client import initialize_client
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json


# ==============================================================================
# 1. GOOGLE AGENT SDK (ADK) - WRAPPER
# ==============================================================================

class GoogleADKWrapper:
    """
    Wrapper to use Google ADK with your custom Vertex AI client.
    Note: Google ADK expects specific client format, so we need to adapt.
    """
    
    def __init__(self):
        self.client = initialize_client()
        
    def create_hello_world_agent(self):
        """
        Create a simple hello world agent using Google ADK approach.
        Since ADK is tightly integrated with Vertex AI, we can use your client directly.
        """
        from google.adk.agents import Agent
        
        # Define a simple tool function
        def say_hello(name: str) -> dict:
            """Returns a greeting message."""
            return {"status": "success", "message": f"Hello {name}! Welcome to the agent world!"}
        
        # Create agent - ADK will use your Vertex credentials automatically
        agent = Agent(
            name="hello_world_agent",
            model="gemini-2.0-flash",  # This will use your Vertex project
            description="Simple hello world agent",
            instruction="Greet users warmly and help them get started.",
            tools=[say_hello]
        )
        
        # Since your client is already configured for Vertex, the agent will use it
        return agent
    
    def run_agent(self, agent, query: str):
        """Run the agent with a query using your client."""
        # ADK handles the client internally when configured with Vertex
        response = agent.run(query)
        return response


# ==============================================================================
# 2. LANGCHAIN - CUSTOM LLM WRAPPER
# ==============================================================================

from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, List, Optional

class VertexLangChainLLM(LLM):
    """Custom LangChain LLM wrapper for your Vertex AI client."""
    
    client: Any = None
    model_name: str = "gemini-2.0-flash"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = initialize_client()
    
    @property
    def _llm_type(self) -> str:
        return "vertex_custom"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Vertex AI model through your custom client."""
        try:
            # Use your client to generate response
            response = self.client.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error calling Vertex AI: {str(e)}"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {"model_name": self.model_name}


def create_langchain_agent():
    """Create a LangChain agent using the custom Vertex LLM."""
    from langchain.agents import tool
    from langgraph.prebuilt import create_react_agent
    
    # Initialize custom LLM
    llm = VertexLangChainLLM()
    
    # Define a simple tool
    @tool
    def greet_user(name: str) -> str:
        """Greet a user by name."""
        return f"Hello {name}! This is LangChain agent using Vertex AI."
    
    # Create agent
    agent = create_react_agent(
        model=llm,
        tools=[greet_user]
    )
    
    return agent


# ==============================================================================
# 3. OPENAI AGENTS SDK - WRAPPER
# ==============================================================================

class OpenAIAgentWrapper:
    """
    Wrapper to use OpenAI Agents SDK with Vertex AI.
    This requires more adaptation since OpenAI SDK expects specific API format.
    """
    
    def __init__(self):
        self.vertex_client = initialize_client()
    
    def create_agent_with_vertex(self):
        """
        Create an agent that internally uses Vertex AI instead of OpenAI.
        We'll need to override the Runner's execution.
        """
        from agents import Agent
        
        # Create a standard agent structure
        agent = Agent(
            name="VertexAgent",
            instructions="You are a helpful assistant powered by Vertex AI."
        )
        
        # We'll need a custom runner since OpenAI SDK expects OpenAI API
        return agent
    
    def run_with_vertex(self, agent, query: str):
        """
        Custom run method that uses Vertex AI instead of OpenAI.
        """
        # Construct the prompt with agent instructions
        full_prompt = f"{agent.instructions}\n\nUser: {query}\nAssistant:"
        
        # Use Vertex client to generate response
        try:
            response = self.vertex_client.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"


# ==============================================================================
# 4. PYDANTIC AI - CUSTOM MODEL WRAPPER
# ==============================================================================

from pydantic_ai import Agent, ModelProvider
from pydantic_ai.models import Model, ModelCall, ModelResponse
from pydantic import BaseModel
import asyncio

class VertexAIModel(Model):
    """Custom Pydantic AI model that uses your Vertex AI client."""
    
    def __init__(self):
        self.client = initialize_client()
        self.model_name = "gemini-2.0-flash"
    
    async def run(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> ModelResponse:
        """Run the model with messages."""
        # Convert messages to Vertex AI format
        prompt = self._messages_to_prompt(messages)
        
        # Call Vertex AI synchronously (we'll wrap in async)
        response_text = await self._call_vertex_async(prompt)
        
        return ModelResponse(
            content=response_text,
            role="assistant"
        )
    
    async def _call_vertex_async(self, prompt: str) -> str:
        """Async wrapper for Vertex AI call."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._call_vertex_sync,
            prompt
        )
    
    def _call_vertex_sync(self, prompt: str) -> str:
        """Synchronous Vertex AI call."""
        try:
            response = self.client.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert message list to a single prompt string."""
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role}: {content}")
        return "\n".join(prompt_parts)


def create_pydantic_agent():
    """Create a Pydantic AI agent using custom Vertex AI model."""
    # Use the custom Vertex AI model
    vertex_model = VertexAIModel()
    
    # Create agent with custom model
    agent = Agent(
        model=vertex_model,
        instructions="You are a helpful assistant using Vertex AI through Pydantic AI."
    )
    
    return agent


# ==============================================================================
# MAIN DEMO - How to use each SDK with your Vertex AI client
# ==============================================================================

def main():
    """Demonstrate all agent SDKs with Vertex AI."""
    
    print("=" * 60)
    print("AGENT SDK POC WITH VERTEX AI")
    print("=" * 60)
    
    # 1. Google ADK Example
    print("\n1. GOOGLE ADK AGENT:")
    print("-" * 40)
    try:
        google_wrapper = GoogleADKWrapper()
        agent = google_wrapper.create_hello_world_agent()
        print("✓ Google ADK agent created successfully")
        print("  Note: ADK natively supports Vertex AI with your credentials")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Install: pip install google-cloud-aiplatform google-adk")
    
    # 2. LangChain Example
    print("\n2. LANGCHAIN AGENT:")
    print("-" * 40)
    try:
        agent = create_langchain_agent()
        print("✓ LangChain agent created with custom Vertex LLM wrapper")
        print("  The VertexLangChainLLM class wraps your client for LangChain")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Install: pip install langchain langgraph")
    
    # 3. OpenAI Agents SDK Example
    print("\n3. OPENAI AGENTS SDK:")
    print("-" * 40)
    try:
        wrapper = OpenAIAgentWrapper()
        agent = wrapper.create_agent_with_vertex()
        print("✓ OpenAI-style agent created with Vertex AI backend")
        print("  Note: Requires custom runner since SDK expects OpenAI API")
        # Example usage:
        result = wrapper.run_with_vertex(agent, "Say hello!")
        print(f"  Response: {result[:100]}...")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Install: pip install openai-agents")
    
    # 4. Pydantic AI Example
    print("\n4. PYDANTIC AI AGENT:")
    print("-" * 40)
    try:
        agent = create_pydantic_agent()
        print("✓ Pydantic AI agent created with custom Vertex AI model")
        print("  The VertexAIModel class implements Pydantic AI's Model interface")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Install: pip install pydantic-ai")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("-" * 40)
    print("1. Google ADK: Works natively with Vertex AI (easiest)")
    print("2. LangChain: Use custom LLM wrapper (VertexLangChainLLM)")
    print("3. OpenAI SDK: Requires custom runner to redirect to Vertex")
    print("4. Pydantic AI: Use custom Model class (VertexAIModel)")
    print("=" * 60)


if __name__ == "__main__":
    main()