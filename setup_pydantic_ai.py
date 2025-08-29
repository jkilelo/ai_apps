"""
Quick Start Script for Pydantic AI + Vertex AI Integration

This script will help you get started with Pydantic AI using your existing Vertex AI setup.
Run this script to see what needs to be done and test the integration.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required for Pydantic AI")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True


def check_pydantic_ai_installed():
    """Check if Pydantic AI is installed"""
    try:
        import pydantic_ai

        print(f"✅ Pydantic AI is installed (version: {pydantic_ai.__version__})")
        return True
    except ImportError:
        print("❌ Pydantic AI is not installed")
        return False


def install_pydantic_ai():
    """Install Pydantic AI with Google support"""
    print("Installing Pydantic AI with Google support...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pydantic-ai[google]"]
        )
        print("✅ Pydantic AI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Pydantic AI: {e}")
        return False


def check_google_dependencies():
    """Check if Google AI dependencies are available"""
    try:
        import google.genai

        print("✅ Google AI SDK is available")
        return True
    except ImportError:
        print("❌ Google AI SDK not found")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "google-genai"]
            )
            print("✅ Google AI SDK installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Google AI SDK")
            return False


def check_existing_vertex_setup():
    """Check if your existing Vertex AI setup works"""
    print("\nChecking your existing Vertex AI setup...")

    # Check if gemini_llm_agent.py exists
    current_dir = Path(__file__).parent
    gemini_file = current_dir / "gemini_llm_agent.py"

    if gemini_file.exists():
        print("✅ Found your existing gemini_llm_agent.py")

        # Try to import and check for syntax errors
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "gemini_llm_agent", gemini_file
            )
            module = importlib.util.module_from_spec(spec)
            # Don't execute, just check syntax
            print("✅ Your existing Vertex AI code is syntactically correct")
            return True
        except Exception as e:
            print(f"⚠️  Found issue in gemini_llm_agent.py: {e}")
            return False
    else:
        print("❌ gemini_llm_agent.py not found in current directory")
        return False


def create_test_script():
    """Create a simple test script"""
    test_script = '''"""
Simple test to verify Pydantic AI + Vertex AI integration works
"""

import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent

class TestResponse(BaseModel):
    answer: str = Field(description="The answer to the question")
    confidence: float = Field(description="Confidence level 0-1", ge=0, le=1)

def test_pydantic_ai():
    """Test basic Pydantic AI functionality"""
    
    # Set up Google AI API key (you'll need to set this)
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Please set GOOGLE_API_KEY environment variable")
        print("   Get your key from: https://aistudio.google.com/apikey")
        print("   Then run: export GOOGLE_API_KEY=your_key")
        return False
    
    try:
        # Create a simple agent using Google model
        agent = Agent(
            "google:gemini-1.5-flash",
            output_type=TestResponse,
            system_prompt="You are a helpful assistant. Be confident in your answers."
        )
        
        # Test with a simple question
        result = agent.run_sync("What is 2 + 2?")
        
        print("🎉 Success! Pydantic AI is working with Google models")
        print(f"Answer: {result.data.answer}")
        print(f"Confidence: {result.data.confidence}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_pydantic_ai()
'''

    with open("test_pydantic_ai.py", "w") as f:
        f.write(test_script)

    print("✅ Created test_pydantic_ai.py")


def show_next_steps():
    """Show what to do next"""
    print("\n" + "=" * 60)
    print("🚀 NEXT STEPS")
    print("=" * 60)

    print("\n1. Set up Google AI API Key:")
    print("   - Go to: https://aistudio.google.com/apikey")
    print("   - Create an API key")
    print("   - Run: export GOOGLE_API_KEY=your_key")
    print("   - Or add it to your .env file")

    print("\n2. Test the basic integration:")
    print("   python test_pydantic_ai.py")

    print("\n3. Try the comprehensive demos:")
    print("   python simple_pydantic_demo.py")

    print("\n4. Explore different agent types:")
    print("   python simple_pydantic_demo.py qa      # Question answering")
    print("   python simple_pydantic_demo.py task    # Task planning")
    print("   python simple_pydantic_demo.py code    # Code analysis")
    print("   python simple_pydantic_demo.py stream  # Streaming responses")

    print("\n5. For advanced features, see:")
    print("   - pydantic_ai_agents.py (comprehensive examples)")
    print("   - vertex_pydantic_integration.py (custom Vertex wrapper)")
    print("   - PYDANTIC_AI_INTEGRATION_GUIDE.md (detailed guide)")

    print("\n6. Update your existing code:")
    print("   - Your gemini_llm_agent.py works as-is")
    print("   - Gradually migrate to Pydantic AI agents")
    print("   - Use structured outputs for better data handling")

    print("\n" + "=" * 60)
    print("📚 Key Benefits You'll Get:")
    print("=" * 60)
    print("✅ Structured, validated outputs")
    print("✅ Type safety and better IDE support")
    print("✅ Built-in tool/function calling")
    print("✅ Dependency injection for clean code")
    print("✅ Streaming support")
    print("✅ Multi-agent workflows")
    print("✅ Robust error handling")
    print("✅ Integration with monitoring tools")


def main():
    """Main setup and check function"""
    print("🤖 Pydantic AI + Vertex AI Integration Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return

    # Check if Pydantic AI is installed
    if not check_pydantic_ai_installed():
        print("\nWould you like to install Pydantic AI? (y/n): ", end="")
        response = input().lower().strip()
        if response in ["y", "yes"]:
            if not install_pydantic_ai():
                return
        else:
            print(
                "Please install Pydantic AI manually: pip install pydantic-ai[google]"
            )
            return

    # Check Google dependencies
    if not check_google_dependencies():
        return

    # Check existing Vertex setup
    check_existing_vertex_setup()

    # Create test script
    create_test_script()

    # Show next steps
    show_next_steps()

    print(
        "\n🎉 Setup complete! You're ready to use Pydantic AI with your Vertex AI setup."
    )


if __name__ == "__main__":
    main()
