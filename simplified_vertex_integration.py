"""
Simplified Pydantic AI Integration with Vertex AI
This version uses the built-in Google model support to avoid abstract class complexity
"""

import asyncio
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# This approach uses Pydantic AI's built-in Google model support
# which is compatible with your Vertex AI setup


def get_vertex_credentials():
    """
    Configure your Vertex AI credentials here
    Update this function with your actual authentication method
    """
    # Option 1: Use environment variable (recommended)
    import os

    if os.getenv("GOOGLE_API_KEY"):
        return None  # Will use environment variable automatically

    # Option 2: Use service account (if you have one)
    # from google.oauth2 import service_account
    # return service_account.Credentials.from_service_account_file(
    #     "path/to/your/service-account.json",
    #     scopes=['https://www.googleapis.com/auth/cloud-platform']
    # )

    # Option 3: Use your existing credentials object
    # from google.oauth2.credentials import Credentials
    # return Credentials(
    #     token="your_access_token",
    #     refresh_token="your_refresh_token",
    #     token_uri="https://oauth2.googleapis.com/token",
    #     client_id="your_client_id",
    #     client_secret="your_client_secret"
    # )

    return None


def create_vertex_agent(
    model_name: str = "gemini-1.5-flash",
    output_type=str,
    system_prompt: str = "You are a helpful assistant.",
    use_vertex_ai: bool = True,
):
    """
    Create a Pydantic AI agent using Google/Vertex AI models
    This uses the built-in Google integration which supports Vertex AI
    """
    try:
        from pydantic_ai import Agent

        if use_vertex_ai:
            # Use Pydantic AI's built-in Google model with Vertex AI
            from pydantic_ai.models.google import GoogleModel
            from pydantic_ai.providers.google import GoogleProvider

            credentials = get_vertex_credentials()

            # Create provider for Vertex AI
            provider = GoogleProvider(
                vertexai=True,  # Enable Vertex AI
                credentials=credentials,
                # Uncomment and set these if needed:
                # project="your_vertex_project",
                # location="us-central1"
            )

            model = GoogleModel(model_name, provider=provider)
        else:
            # Use simple model string (will use Generative Language API)
            model = f"google:{model_name}"

        return Agent(model, output_type=output_type, system_prompt=system_prompt)

    except ImportError as e:
        print(f"Pydantic AI not installed: {e}")
        print("Install with: pip install pydantic-ai[google]")
        return None
    except Exception as e:
        print(f"Error creating agent: {e}")
        return None


# Example structured output models
class SimpleResponse(BaseModel):
    """Simple response with confidence"""

    answer: str = Field(description="The main answer")
    confidence: float = Field(description="Confidence level 0-1", ge=0, le=1)
    reasoning: str = Field(description="Brief explanation of the reasoning")


class TaskPlan(BaseModel):
    """Structured task planning output"""

    main_task: str = Field(description="Main task description")
    subtasks: List[str] = Field(description="List of subtasks")
    estimated_hours: float = Field(description="Estimated time in hours")
    priority: str = Field(description="Priority: high, medium, low")
    resources_needed: List[str] = Field(description="Required resources")


class CodeAnalysis(BaseModel):
    """Code analysis output"""

    quality_score: int = Field(description="Quality score 1-10", ge=1, le=10)
    issues: List[str] = Field(description="Issues found")
    suggestions: List[str] = Field(description="Improvement suggestions")
    security_rating: str = Field(description="Security rating: secure, moderate, risky")


# Demo functions
async def demo_simple_qa():
    """Simple Q&A with structured output"""
    print("=== Simple Q&A Demo ===")

    agent = create_vertex_agent(
        output_type=SimpleResponse,
        system_prompt="You are a knowledgeable assistant. Provide confident, accurate answers.",
    )

    if not agent:
        print("Failed to create agent")
        return

    try:
        result = await agent.run(
            "What is the capital of Kenya and why is it important?"
        )

        print(f"Answer: {result.data.answer}")
        print(f"Confidence: {result.data.confidence:.2f}")
        print(f"Reasoning: {result.data.reasoning}")
        print()

    except Exception as e:
        print(f"Demo failed: {e}")
        print("Make sure you have set up your Google AI credentials")


async def demo_task_planning():
    """Task planning demo"""
    print("=== Task Planning Demo ===")

    agent = create_vertex_agent(
        output_type=TaskPlan,
        system_prompt="You are a project manager. Create detailed, actionable task plans.",
    )

    if not agent:
        print("Failed to create agent")
        return

    try:
        result = await agent.run(
            "I need to create a customer management web application with user authentication, "
            "customer CRUD operations, and reporting features. Help me plan this project."
        )

        print(f"Main Task: {result.data.main_task}")
        print(f"Estimated Hours: {result.data.estimated_hours}")
        print(f"Priority: {result.data.priority}")
        print("\nSubtasks:")
        for i, subtask in enumerate(result.data.subtasks, 1):
            print(f"  {i}. {subtask}")
        print("\nResources Needed:")
        for resource in result.data.resources_needed:
            print(f"  - {resource}")
        print()

    except Exception as e:
        print(f"Demo failed: {e}")


async def demo_code_analysis():
    """Code analysis demo"""
    print("=== Code Analysis Demo ===")

    agent = create_vertex_agent(
        output_type=CodeAnalysis,
        system_prompt="You are a senior software engineer. Analyze code for quality, security, and best practices.",
    )

    if not agent:
        print("Failed to create agent")
        return

    code_sample = """
def authenticate_user(username, password):
    # Hardcoded admin bypass
    if password == "admin123":
        return {"user": "admin", "role": "admin"}
    
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = database.execute(query)
    
    if result:
        return {"user": username, "role": "user"}
    return None
"""

    try:
        result = await agent.run(
            f"Analyze this authentication function:\n\n{code_sample}"
        )

        print(f"Quality Score: {result.data.quality_score}/10")
        print(f"Security Rating: {result.data.security_rating}")
        print("\nIssues Found:")
        for issue in result.data.issues:
            print(f"  - {issue}")
        print("\nSuggestions:")
        for suggestion in result.data.suggestions:
            print(f"  - {suggestion}")
        print()

    except Exception as e:
        print(f"Demo failed: {e}")


async def demo_with_tools():
    """Demo with function tools"""
    print("=== Agent with Tools Demo ===")

    from pydantic_ai import Agent, RunContext
    from dataclasses import dataclass

    @dataclass
    class ToolContext:
        user_id: str
        session_id: str

    class ToolResponse(BaseModel):
        action_taken: str
        result: str
        next_steps: List[str]

    try:
        agent = create_vertex_agent(
            output_type=ToolResponse,
            system_prompt="You are a helpful assistant with access to various tools.",
        )

        if not agent:
            print("Failed to create agent")
            return

        # Note: This is a simplified example
        # In practice, you'd add tools using @agent.tool decorator

        result = await agent.run(
            "I need to check my account balance and send a notification to myself about it."
        )

        print(f"Action Taken: {result.data.action_taken}")
        print(f"Result: {result.data.result}")
        print("Next Steps:")
        for step in result.data.next_steps:
            print(f"  - {step}")
        print()

    except Exception as e:
        print(f"Demo failed: {e}")


async def demo_streaming():
    """Streaming response demo"""
    print("=== Streaming Demo ===")

    agent = create_vertex_agent(
        system_prompt="You are a creative writer. Write engaging stories."
    )

    if not agent:
        print("Failed to create agent")
        return

    try:
        print("Streaming story (word by word):")
        print("Story: ", end="", flush=True)

        async for message in agent.run_stream(
            "Write a short story about an AI learning to paint"
        ):
            if hasattr(message, "data") and message.data:
                print(message.data, end="", flush=True)

        print("\n")

    except Exception as e:
        print(f"Streaming demo failed: {e}")


# Synchronous wrapper functions
def run_simple_qa():
    """Run Q&A demo synchronously"""
    return asyncio.run(demo_simple_qa())


def run_task_planning():
    """Run task planning demo synchronously"""
    return asyncio.run(demo_task_planning())


def run_code_analysis():
    """Run code analysis demo synchronously"""
    return asyncio.run(demo_code_analysis())


def run_tools_demo():
    """Run tools demo synchronously"""
    return asyncio.run(demo_with_tools())


def run_streaming():
    """Run streaming demo synchronously"""
    return asyncio.run(demo_streaming())


def run_all_demos():
    """Run all demos"""
    return asyncio.run(run_all_demos_async())


async def run_all_demos_async():
    """Run all demos asynchronously"""
    demos = [
        demo_simple_qa,
        demo_task_planning,
        demo_code_analysis,
        demo_with_tools,
        demo_streaming,
    ]

    for demo in demos:
        try:
            await demo()
        except Exception as e:
            print(f"Demo {demo.__name__} failed: {e}")
        print("-" * 50)


def test_installation():
    """Test if Pydantic AI is properly installed"""
    try:
        from pydantic_ai import Agent
        from pydantic_ai.models.google import GoogleModel

        print("✅ Pydantic AI is properly installed")
        return True
    except ImportError as e:
        print(f"❌ Pydantic AI not found: {e}")
        print("Install with: pip install pydantic-ai[google]")
        return False


if __name__ == "__main__":
    print("🤖 Simplified Pydantic AI + Vertex AI Integration\n")

    # Test installation first
    if not test_installation():
        exit(1)

    print("Available demos:")
    print("1. python simplified_vertex_integration.py qa")
    print("2. python simplified_vertex_integration.py task")
    print("3. python simplified_vertex_integration.py code")
    print("4. python simplified_vertex_integration.py tools")
    print("5. python simplified_vertex_integration.py stream")
    print("6. python simplified_vertex_integration.py all")
    print()

    # Check command line arguments
    import sys

    if len(sys.argv) > 1:
        demo = sys.argv[1].lower()
        if demo == "qa":
            run_simple_qa()
        elif demo == "task":
            run_task_planning()
        elif demo == "code":
            run_code_analysis()
        elif demo == "tools":
            run_tools_demo()
        elif demo == "stream":
            run_streaming()
        elif demo == "all":
            run_all_demos()
        else:
            print(f"Unknown demo: {demo}")
    else:
        # Run a simple test
        print("Running simple Q&A demo...")
        run_simple_qa()

    print("✅ Demo completed!")
    print("\nNext steps:")
    print("1. Set up your Google AI API key: export GOOGLE_API_KEY=your_key")
    print("2. Or configure Vertex AI credentials in get_vertex_credentials()")
    print("3. Try different demos to explore Pydantic AI features")
