"""
Quick Fix and Test for Pydantic AI Integration
This script will test different approaches and show you what works
"""

import os
import sys


def test_pydantic_ai_installation():
    """Test if Pydantic AI is installed correctly"""
    print("🔍 Testing Pydantic AI installation...")

    try:
        import pydantic_ai

        print(f"✅ Pydantic AI installed (version: {pydantic_ai.__version__})")
        return True
    except ImportError:
        print("❌ Pydantic AI not installed")
        print("Install with: pip install pydantic-ai[google]")
        return False


def test_google_credentials():
    """Test Google AI credentials setup"""
    print("\n🔍 Testing Google AI credentials...")

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("✅ GOOGLE_API_KEY environment variable found")
        return True
    else:
        print("❌ GOOGLE_API_KEY not set")
        print("Set with: export GOOGLE_API_KEY=your_key")
        print("Get key from: https://aistudio.google.com/apikey")
        return False


def test_simple_agent():
    """Test creating a simple agent"""
    print("\n🔍 Testing simple agent creation...")

    try:
        from pydantic_ai import Agent
        from pydantic import BaseModel, Field

        class TestResponse(BaseModel):
            answer: str = Field(description="The answer")
            confidence: float = Field(description="Confidence 0-1", ge=0, le=1)

        # Try simple string model first
        agent = Agent(
            "google:gemini-1.5-flash",
            output_type=TestResponse,
            system_prompt="You are a helpful assistant.",
        )

        print("✅ Simple agent created successfully")
        return agent

    except Exception as e:
        print(f"❌ Failed to create simple agent: {e}")
        return None


def test_agent_run():
    """Test running an agent"""
    print("\n🔍 Testing agent execution...")

    agent = test_simple_agent()
    if not agent:
        return False

    try:
        result = agent.run_sync("What is 2 + 2? Be confident in your answer.")

        print("✅ Agent executed successfully")
        print(f"Answer: {result.data.answer}")
        print(f"Confidence: {result.data.confidence}")
        return True

    except Exception as e:
        print(f"❌ Agent execution failed: {e}")
        if "API_KEY" in str(e):
            print(
                "This looks like a credentials issue. Make sure GOOGLE_API_KEY is set."
            )
        return False


def test_vertex_ai_approach():
    """Test Vertex AI specific approach"""
    print("\n🔍 Testing Vertex AI approach...")

    try:
        from pydantic_ai import Agent
        from pydantic_ai.models.google import GoogleModel
        from pydantic_ai.providers.google import GoogleProvider

        # Test with Vertex AI provider
        provider = GoogleProvider(vertexai=True)
        model = GoogleModel("gemini-1.5-flash", provider=provider)

        agent = Agent(model, system_prompt="You are a helpful assistant.")

        print("✅ Vertex AI agent created successfully")

        # Try a simple run
        result = agent.run_sync("Hello, can you confirm you're working?")
        print(f"✅ Vertex AI agent response: {result.data}")
        return True

    except Exception as e:
        print(f"❌ Vertex AI approach failed: {e}")
        print("This might require additional Vertex AI setup")
        return False


def fix_abstract_class_error():
    """Provide solution for abstract class error"""
    print("\n🔧 Solution for Abstract Class Error:")
    print("=" * 50)

    print(
        "The error occurs because the custom VertexAIWrapper class needs to implement"
    )
    print("all abstract methods required by Pydantic AI's Model base class.")
    print()
    print("RECOMMENDED SOLUTION: Use the simplified approach instead!")
    print()
    print(
        "Instead of creating a custom wrapper, use Pydantic AI's built-in Google support:"
    )
    print()
    print("# Simple approach (recommended)")
    print("from pydantic_ai import Agent")
    print("from pydantic_ai.models.google import GoogleModel")
    print("from pydantic_ai.providers.google import GoogleProvider")
    print()
    print("# For Vertex AI")
    print("provider = GoogleProvider(vertexai=True)")
    print("model = GoogleModel('gemini-1.5-flash', provider=provider)")
    print("agent = Agent(model)")
    print()
    print("# Or even simpler")
    print("agent = Agent('google:gemini-1.5-flash')")
    print()


def show_working_examples():
    """Show working code examples"""
    print("\n📝 Working Examples:")
    print("=" * 50)

    example1 = """
# Example 1: Simple agent with structured output
from pydantic_ai import Agent
from pydantic import BaseModel, Field

class Response(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)

agent = Agent(
    "google:gemini-1.5-flash",
    output_type=Response,
    system_prompt="You are helpful and confident."
)

result = agent.run_sync("What is the capital of Kenya?")
print(f"Answer: {result.data.answer}")
print(f"Confidence: {result.data.confidence}")
"""

    example2 = """
# Example 2: Agent with Vertex AI
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

provider = GoogleProvider(
    vertexai=True,
    # credentials=your_credentials,  # Optional
    # project="your-project",        # Optional
    # location="us-central1"         # Optional
)

model = GoogleModel("gemini-1.5-flash", provider=provider)
agent = Agent(model, system_prompt="You are a helpful assistant.")

result = agent.run_sync("Hello!")
print(result.data)
"""

    print("EXAMPLE 1 - Simple Agent:")
    print(example1)
    print("\nEXAMPLE 2 - Vertex AI Agent:")
    print(example2)


def main():
    """Main test and fix function"""
    print("🔧 Pydantic AI Integration - Quick Fix & Test")
    print("=" * 60)

    # Run tests
    pydantic_ok = test_pydantic_ai_installation()
    if not pydantic_ok:
        return

    credentials_ok = test_google_credentials()
    agent_ok = test_agent_run() if credentials_ok else False

    # Try Vertex AI approach
    vertex_ok = test_vertex_ai_approach() if credentials_ok else False

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Pydantic AI Installation: {'✅ OK' if pydantic_ok else '❌ FAILED'}")
    print(f"Google Credentials: {'✅ OK' if credentials_ok else '❌ FAILED'}")
    print(f"Basic Agent: {'✅ OK' if agent_ok else '❌ FAILED'}")
    print(f"Vertex AI Agent: {'✅ OK' if vertex_ok else '❌ FAILED'}")

    # Provide solutions
    if not agent_ok:
        fix_abstract_class_error()

    show_working_examples()

    print("\n" + "=" * 60)
    print("🚀 RECOMMENDED NEXT STEPS")
    print("=" * 60)

    if not pydantic_ok:
        print("1. Install Pydantic AI: pip install pydantic-ai[google]")

    if not credentials_ok:
        print("2. Set up credentials:")
        print("   export GOOGLE_API_KEY=your_key")
        print("   Get key from: https://aistudio.google.com/apikey")

    if pydantic_ok and credentials_ok:
        print("✅ You're ready to go! Use simplified_vertex_integration.py")
        print("   python simplified_vertex_integration.py qa")

    print("\n📁 Use these files:")
    print("- simplified_vertex_integration.py (recommended)")
    print("- simple_pydantic_demo.py (alternative)")
    print("- Avoid vertex_pydantic_integration.py (has abstract class issues)")


if __name__ == "__main__":
    main()
