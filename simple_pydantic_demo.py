"""
Simple Pydantic AI Demo with your Vertex AI Setup
This is a minimal working example that you can run immediately.

Instructions:
1. Install: pip install pydantic-ai[google]
2. Update your credentials in the get_credentials() function below
3. Run this file to see Pydantic AI in action with your Vertex setup
"""

import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent


def get_credentials():
    """
    Update this function with your actual Vertex AI credentials
    This should match exactly how you authenticate in gemini_llm_agent.py
    """
    # Option 1: If you use API keys
    # return {"api_key": "your_actual_api_key"}

    # Option 2: If you use OAuth credentials
    # from google.oauth2.credentials import Credentials
    # return Credentials(token="your_token", refresh_token="your_refresh_token")

    # Option 3: Service account
    # from google.oauth2 import service_account
    # return service_account.Credentials.from_service_account_file("path/to/service-account.json")

    # For demo purposes - replace with your actual method
    return {"api_key": "your_api_key_here"}


# Define structured output models
class SimpleAnswer(BaseModel):
    """Simple structured response"""

    answer: str = Field(description="The main answer to the question")
    confidence: float = Field(
        description="Confidence level from 0.0 to 1.0", ge=0.0, le=1.0
    )
    category: str = Field(
        description="Category of the question (geography, history, science, etc.)"
    )


class TaskBreakdown(BaseModel):
    """Structured output for task planning"""

    main_task: str = Field(description="The main task description")
    subtasks: List[str] = Field(description="List of subtasks")
    estimated_hours: float = Field(description="Estimated time in hours")
    priority: str = Field(description="Priority level: high, medium, or low")
    dependencies: List[str] = Field(description="Dependencies or prerequisites")


class CodeAnalysis(BaseModel):
    """Structured output for code analysis"""

    code_quality: int = Field(description="Code quality score from 1-10", ge=1, le=10)
    issues: List[str] = Field(description="List of issues found")
    suggestions: List[str] = Field(description="Improvement suggestions")
    is_secure: bool = Field(description="Whether the code appears secure")


# Simple agents using standard Pydantic AI Google integration
def create_simple_agent(output_type=str, system_prompt="You are a helpful assistant."):
    """
    Create a simple agent using Pydantic AI's built-in Google model support
    This uses the standard Google integration, which should work with your credentials
    """
    # You can use either approach:

    # Approach 1: Simple model string (recommended for start)
    model = "google:gemini-1.5-flash"

    # Approach 2: Custom provider (if you need specific settings)
    # from pydantic_ai.models.google import GoogleModel
    # from pydantic_ai.providers.google import GoogleProvider
    #
    # credentials = get_credentials()
    # provider = GoogleProvider(
    #     vertexai=True,  # Use Vertex AI
    #     credentials=credentials,
    #     # location="us-central1"  # Specify region if needed
    # )
    # model = GoogleModel("gemini-1.5-flash", provider=provider)

    return Agent(model, output_type=output_type, system_prompt=system_prompt)


# Demo functions
async def demo_simple_qa():
    """Simple question answering with structured output"""
    print("=== Simple Q&A Agent ===")

    agent = create_simple_agent(
        output_type=SimpleAnswer,
        system_prompt="You are a knowledgeable assistant. Always provide confident, accurate answers.",
    )

    result = await agent.run("What is the capital of Kenya?")

    print(f"Answer: {result.data.answer}")
    print(f"Confidence: {result.data.confidence:.2f}")
    print(f"Category: {result.data.category}")
    print()


async def demo_task_planning():
    """Task planning agent"""
    print("=== Task Planning Agent ===")

    agent = create_simple_agent(
        output_type=TaskBreakdown,
        system_prompt="You are a project manager. Break down complex tasks into manageable subtasks.",
    )

    result = await agent.run(
        "I need to build a web application for customer management. "
        "Help me break this down into tasks."
    )

    print(f"Main Task: {result.data.main_task}")
    print(f"Estimated Hours: {result.data.estimated_hours}")
    print(f"Priority: {result.data.priority}")
    print("Subtasks:")
    for i, subtask in enumerate(result.data.subtasks, 1):
        print(f"  {i}. {subtask}")
    print("Dependencies:")
    for dep in result.data.dependencies:
        print(f"  - {dep}")
    print()


async def demo_code_analysis():
    """Code analysis agent"""
    print("=== Code Analysis Agent ===")

    agent = create_simple_agent(
        output_type=CodeAnalysis,
        system_prompt="You are a senior developer. Analyze code for quality, security, and best practices.",
    )

    code_to_analyze = """
def login(username, password):
    if password == "admin123":
        return True
    
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}'"
    result = database.execute(query)
    return len(result) > 0
"""

    result = await agent.run(f"Analyze this Python code:\n\n{code_to_analyze}")

    print(f"Code Quality Score: {result.data.code_quality}/10")
    print(f"Is Secure: {result.data.is_secure}")
    print("Issues Found:")
    for issue in result.data.issues:
        print(f"  - {issue}")
    print("Suggestions:")
    for suggestion in result.data.suggestions:
        print(f"  - {suggestion}")
    print()


async def demo_streaming():
    """Streaming response demo"""
    print("=== Streaming Agent ===")

    agent = create_simple_agent(
        system_prompt="You are a creative writer. Write engaging, detailed stories."
    )

    print("Streaming story (type-by-type effect):")
    print("Story: ", end="", flush=True)

    async for message in agent.run_stream(
        "Write a short story about a robot learning to paint"
    ):
        if hasattr(message, "data") and message.data:
            print(message.data, end="", flush=True)

    print("\n")


async def demo_conversation():
    """Conversation with memory demo"""
    print("=== Conversation Agent ===")

    agent = create_simple_agent(
        system_prompt="You are a helpful assistant. Remember context from previous messages."
    )

    # First message
    result1 = await agent.run("My name is John and I live in Nairobi.")
    print(f"Agent: {result1.data}")

    # Follow-up that should remember context
    result2 = await agent.run(
        "What city did I mention?", message_history=result1.new_messages()
    )
    print(f"Agent: {result2.data}")
    print()


# Synchronous wrapper functions for easy testing
def run_simple_qa():
    return asyncio.run(demo_simple_qa())


def run_task_planning():
    return asyncio.run(demo_task_planning())


def run_code_analysis():
    return asyncio.run(demo_code_analysis())


def run_streaming():
    return asyncio.run(demo_streaming())


def run_conversation():
    return asyncio.run(demo_conversation())


def run_all_demos():
    """Run all demos"""
    return asyncio.run(run_all_demos_async())


async def run_all_demos_async():
    """Run all demos asynchronously"""
    try:
        await demo_simple_qa()
        await demo_task_planning()
        await demo_code_analysis()
        await demo_streaming()
        await demo_conversation()
    except Exception as e:
        print(f"Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have installed: pip install pydantic-ai[google]")
        print("2. Set up your Google AI API key: export GOOGLE_API_KEY=your_key")
        print(
            "3. Or update the get_credentials() function with your Vertex AI credentials"
        )


if __name__ == "__main__":
    print("🤖 Pydantic AI + Vertex AI Integration Demo\n")
    print("This demo shows how to use Pydantic AI with structured outputs")
    print("while maintaining compatibility with your Vertex AI setup.\n")

    # Check if we should run a specific demo
    import sys

    if len(sys.argv) > 1:
        demo_name = sys.argv[1].lower()
        if demo_name == "qa":
            run_simple_qa()
        elif demo_name == "task":
            run_task_planning()
        elif demo_name == "code":
            run_code_analysis()
        elif demo_name == "stream":
            run_streaming()
        elif demo_name == "conversation":
            run_conversation()
        else:
            print(f"Unknown demo: {demo_name}")
            print("Available demos: qa, task, code, stream, conversation")
    else:
        # Run all demos
        run_all_demos()

    print("\n✅ Demo completed!")
    print("\nNext steps:")
    print("1. Update get_credentials() with your actual Vertex AI credentials")
    print("2. Explore the examples in pydantic_ai_agents.py for more advanced patterns")
    print("3. Read PYDANTIC_AI_INTEGRATION_GUIDE.md for detailed information")
