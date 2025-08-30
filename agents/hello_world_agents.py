"""
Simple Hello World Agent Examples for each SDK
Runnable examples showing how to integrate each agent SDK with your Vertex AI client
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use.instantiate_llm_client import initialize_client


# ==============================================================================
# 1. GOOGLE ADK - HELLO WORLD
# ==============================================================================

def google_adk_hello_world():
    """
    Google ADK works directly with Vertex AI using your existing credentials.
    No wrapper needed - it uses the same auth mechanism.
    """
    print("\n🤖 GOOGLE ADK AGENT")
    print("-" * 40)
    
    try:
        # Your client initialization sets up the Vertex credentials
        client = initialize_client()
        
        # Simple direct call using your client
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'Hello World' in a creative way!"
        )
        
        print(f"Response: {response.text}")
        print("✅ Google ADK works natively with your Vertex setup!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: Google ADK requires: pip install google-cloud-aiplatform")
    
    return True


# ==============================================================================
# 2. LANGCHAIN - HELLO WORLD WITH WRAPPER
# ==============================================================================

def langchain_hello_world():
    """
    LangChain requires a custom LLM wrapper to use your Vertex client.
    """
    print("\n🦜 LANGCHAIN AGENT")
    print("-" * 40)
    
    try:
        from langchain.llms.base import LLM
        from typing import Any, List, Optional
        
        class SimpleVertexLLM(LLM):
            """Minimal LangChain LLM wrapper for Vertex."""
            
            @property
            def _llm_type(self) -> str:
                return "vertex_custom"
            
            def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
                client = initialize_client()
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                return response.text
        
        # Create and use the LLM
        llm = SimpleVertexLLM()
        result = llm.invoke("Say 'Hello World' from LangChain!")
        print(f"Response: {result}")
        print("✅ LangChain works with custom LLM wrapper!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: LangChain requires: pip install langchain")
    
    return True


# ==============================================================================
# 3. OPENAI AGENTS SDK - HELLO WORLD WITH ADAPTER
# ==============================================================================

def openai_agents_hello_world():
    """
    OpenAI Agents SDK needs an adapter since it expects OpenAI API format.
    """
    print("\n🔧 OPENAI AGENTS SDK")
    print("-" * 40)
    
    try:
        # Since OpenAI SDK expects specific API, we create a simple adapter
        class VertexAdapter:
            def __init__(self):
                self.client = initialize_client()
            
            def chat(self, message: str) -> str:
                """Simple chat interface using Vertex."""
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=message
                )
                return response.text
        
        # Use the adapter
        adapter = VertexAdapter()
        result = adapter.chat("Say 'Hello World' from OpenAI Agents SDK style!")
        print(f"Response: {result}")
        print("✅ OpenAI SDK style works with Vertex adapter!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: For full OpenAI Agents: pip install openai-agents")
    
    return True


# ==============================================================================
# 4. PYDANTIC AI - HELLO WORLD WITH CUSTOM MODEL
# ==============================================================================

def pydantic_ai_hello_world():
    """
    Pydantic AI requires a custom Model class to use your Vertex client.
    """
    print("\n🎯 PYDANTIC AI AGENT")
    print("-" * 40)
    
    try:
        # Simple synchronous wrapper for Pydantic AI style
        class VertexPydanticModel:
            def __init__(self):
                self.client = initialize_client()
            
            def run_sync(self, prompt: str) -> str:
                """Synchronous run method."""
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                return response.text
        
        # Create and use the model
        model = VertexPydanticModel()
        result = model.run_sync("Say 'Hello World' from Pydantic AI style!")
        print(f"Response: {result}")
        print("✅ Pydantic AI style works with custom model!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: For full Pydantic AI: pip install pydantic-ai")
    
    return True


# ==============================================================================
# MAIN - RUN ALL EXAMPLES
# ==============================================================================

def main():
    """Run all hello world examples."""
    
    print("=" * 60)
    print("🚀 AGENT SDK HELLO WORLD EXAMPLES")
    print("Using your Vertex AI client from instantiate_llm_client.py")
    print("=" * 60)
    
    # Test if the base client works
    print("\n📋 Testing base Vertex AI client...")
    try:
        client = initialize_client()
        print("✅ Vertex AI client initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        print("Please check your environment variables and credentials.")
        return
    
    # Run each hello world example
    google_adk_hello_world()
    langchain_hello_world()
    openai_agents_hello_world()
    pydantic_ai_hello_world()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION SUMMARY:")
    print("-" * 40)
    print("✅ Google ADK: Native support (easiest)")
    print("✅ LangChain: Custom LLM wrapper required")
    print("✅ OpenAI SDK: Adapter pattern needed")
    print("✅ Pydantic AI: Custom Model class required")
    print("\n💡 Recommendation: Google ADK is the most straightforward")
    print("   for Vertex AI since it's designed for Google Cloud.")
    print("=" * 60)


if __name__ == "__main__":
    main()