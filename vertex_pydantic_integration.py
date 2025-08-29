"""
Custom Pydantic AI Model Wrapper for Vertex AI
This module provides a custom model implementation that directly uses your existing Vertex AI setup
"""

import json
from typing import Any, Dict, List, Optional, Union, AsyncIterator
from pydantic_ai.models import Model
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    SystemPromptPart,
    UserPromptPart,
    TextPart,
)
from pydantic_ai import exceptions
from pydantic_ai.settings import ModelSettings

# Import your existing Vertex AI setup
from google.oauth2.credentials import Credentials
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import asyncio


class VertexAIWrapper(Model):
    """
    Custom Pydantic AI Model that wraps your existing Vertex AI GenerativeModel
    This ensures 100% compatibility with your current Vertex AI setup
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        vertex_project: str = "your_vertex_project",
        credentials: Optional[Credentials] = None,
        gemini_url: str = "https://gemini.example.com/api",
        system_instruction: Optional[List[str]] = None,
    ):

        self._model_name = model_name
        self.vertex_project = vertex_project
        self.gemini_url = gemini_url
        self._system_instruction = system_instruction or [
            "You are a helpful assistant."
        ]

        # Initialize Vertex AI exactly as you do
        if credentials is None:
            credentials = Credentials(
                # Use your existing credential setup
                token="your_api_key"  # Replace with your actual auth method
            )

        vertexai.init(
            project=vertex_project,
            credentials=credentials,
            api_endpoint=gemini_url,
            api_transport="rest",
        )

        # Create the GenerativeModel exactly as you do
        self.llm = GenerativeModel(
            model_name=model_name,
            system_instruction=self._system_instruction,
        )

    @property
    def model_name(self) -> str:
        """Return the model name - required abstract property"""
        return self._model_name

    def name(self) -> str:
        """Return the model name - alternative method name"""
        return self._model_name

    @property
    def system(self) -> Optional[str]:
        """Return the system prompt - required abstract property"""
        return "\n".join(self._system_instruction) if self._system_instruction else None

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: Optional[ModelSettings] = None,
    ) -> ModelResponse:
        """
        Convert Pydantic AI messages to your Vertex AI format and make the request
        """
        try:
            # Convert Pydantic AI messages to a simple prompt format
            prompt = self._convert_messages_to_prompt(messages)

            # Create generation config from model settings if provided
            generation_config = self._create_generation_config(model_settings)

            # Use your existing LLM call pattern
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.llm.generate_content(
                    prompt, generation_config=generation_config
                ),
            )

            # Convert response back to Pydantic AI format
            return self._convert_to_model_response(response)

        except Exception as e:
            raise Exception(f"Vertex AI request failed: {str(e)}")

    async def request_stream(
        self,
        messages: list[ModelMessage],
        model_settings: Optional[ModelSettings] = None,
    ) -> AsyncIterator[ModelResponse]:
        """
        Streaming version (simplified implementation)
        """
        # For now, just yield the complete response
        # You can implement true streaming if needed
        response = await self.request(messages, model_settings)
        yield response

    def _convert_messages_to_prompt(self, messages: list[ModelMessage]) -> str:
        """
        Convert Pydantic AI messages to a simple prompt string
        This matches how you currently use your Vertex AI model
        """
        prompt_parts = []

        for message in messages:
            if hasattr(message, "parts"):
                for part in message.parts:
                    if isinstance(part, SystemPromptPart):
                        prompt_parts.append(f"System: {part.content}")
                    elif isinstance(part, UserPromptPart):
                        prompt_parts.append(f"User: {part.content}")
                    elif isinstance(part, TextPart):
                        prompt_parts.append(part.content)

        return "\n".join(prompt_parts)

    def _create_generation_config(
        self, model_settings: Optional[ModelSettings]
    ) -> Optional[GenerationConfig]:
        """
        Create Vertex AI GenerationConfig from Pydantic AI ModelSettings
        """
        if not model_settings:
            return None

        config_params = {}

        if model_settings.temperature is not None:
            config_params["temperature"] = model_settings.temperature
        if model_settings.max_tokens is not None:
            config_params["max_output_tokens"] = model_settings.max_tokens
        if model_settings.top_p is not None:
            config_params["top_p"] = model_settings.top_p

        return GenerationConfig(**config_params) if config_params else None

    def _convert_to_model_response(self, vertex_response) -> ModelResponse:
        """
        Convert Vertex AI response to Pydantic AI ModelResponse
        """
        # Extract text from Vertex AI response
        text_content = (
            vertex_response.text
            if hasattr(vertex_response, "text")
            else str(vertex_response)
        )

        # Create the response parts
        parts = [TextPart(content=text_content)]

        # Create usage information (simplified) - commented out for compatibility
        # usage = Usage(
        #     model_name=self.model_name,
        #     request_tokens=0,  # You could calculate this if needed
        #     response_tokens=len(text_content.split()),  # Rough estimate
        #     total_tokens=len(text_content.split()),
        # )

        return ModelResponse(parts=parts, model_name=self.model_name)


# Updated agent creation functions using the custom wrapper
def create_vertex_model_wrapper(
    model_name: str = "gemini-2.5-flash",
) -> VertexAIWrapper:
    """
    Create a VertexAI model wrapper using your exact existing configuration
    """
    # Replace these with your actual values
    gemini_url = "https://gemini.example.com/api"
    vertex_project = "your_vertex_project"

    # Use your existing credential setup
    credentials = Credentials(
        # Replace with your actual credentials setup
        token="your_api_key"  # This should match your current auth method
    )

    return VertexAIWrapper(
        model_name=model_name,
        vertex_project=vertex_project,
        credentials=credentials,
        gemini_url=gemini_url,
        system_instruction=["You are a helpful assistant."],
    )


# Simple agent using your exact Vertex AI setup
async def simple_vertex_agent_demo():
    """
    Demo using your exact Vertex AI setup with Pydantic AI features
    """
    from pydantic_ai import Agent
    from pydantic import BaseModel, Field

    # Create output model
    class SimpleResponse(BaseModel):
        answer: str = Field(description="The main answer")
        confidence: float = Field(description="Confidence level 0-1", ge=0, le=1)
        source: str = Field(description="Information source")

    # Create model using your exact Vertex setup
    model = create_vertex_model_wrapper()

    # Create agent with structured output
    agent = Agent(
        model,
        output_type=SimpleResponse,
        system_prompt="You are a helpful assistant. Always provide confident, accurate answers.",
    )

    # Test the agent
    result = await agent.run("What is the capital of Kenya?")

    print("Simple Vertex Agent Result:")
    print(f"Answer: {result.data.answer}")
    print(f"Confidence: {result.data.confidence}")
    print(f"Source: {result.data.source}")
    print()

    return result


# Direct comparison with your existing approach
async def compare_existing_vs_pydantic():
    """
    Compare your existing Vertex AI approach with Pydantic AI wrapper
    """
    print("=== Comparison: Existing vs Pydantic AI ===\n")

    # Your existing approach (recreated from your code)
    print("1. Your Existing Approach:")
    try:
        # Recreate your existing setup
        from google.oauth2.credentials import Credentials
        import vertexai
        from vertexai.generative_models import GenerativeModel

        gemini_url = "https://gemini.example.com/api"
        vertex_project = "your_vertex_project"
        credentials = Credentials(
            # Your existing credentials
            token="your_api_key"
        )

        vertexai.init(
            project=vertex_project,
            credentials=credentials,
            api_endpoint=gemini_url,
            api_transport="rest",
        )

        llm = GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=["You are a helpful assistant."],
        )

        prompt = "What is the capital of Kenya?"
        response = llm.generate_content(prompt)

        print(f"Response: {response.text}")
        print("Format: Raw text response")
        print()

    except Exception as e:
        print(f"Existing approach demo failed: {e}")
        print("(This is expected in demo - replace with your actual credentials)")
        print()

    # Pydantic AI approach
    print("2. Pydantic AI Approach with same Vertex setup:")
    try:
        result = await simple_vertex_agent_demo()
        print("Format: Structured Pydantic model with validation")
        print("Benefits: Type safety, validation, tools, streaming, etc.")
    except Exception as e:
        print(f"Pydantic AI approach demo failed: {e}")
        print("(This is expected in demo - replace with your actual credentials)")


# Tool-enabled agent example
async def tool_enabled_agent_demo():
    """
    Demo showing how to add tools while keeping your Vertex setup
    """
    from pydantic_ai import Agent, RunContext
    from pydantic import BaseModel, Field
    from dataclasses import dataclass

    @dataclass
    class AgentDeps:
        user_id: str
        database_url: str

    class TaskResult(BaseModel):
        task_completed: bool = Field(description="Whether task was completed")
        steps_taken: List[str] = Field(description="Steps that were taken")
        next_actions: List[str] = Field(description="Recommended next actions")

    model = create_vertex_model_wrapper()

    agent = Agent(
        model,
        deps_type=AgentDeps,
        output_type=TaskResult,
        system_prompt="You are a task management assistant.",
    )

    @agent.tool
    async def check_database(ctx: RunContext[AgentDeps], query: str) -> str:
        """Check database for information"""
        # Simulate database check
        return f"Database query '{query}' executed for user {ctx.deps.user_id}"

    @agent.tool
    async def send_notification(ctx: RunContext[AgentDeps], message: str) -> str:
        """Send notification to user"""
        return f"Notification sent to {ctx.deps.user_id}: {message}"

    # Run the agent with tools
    deps = AgentDeps(user_id="user123", database_url="postgresql://...")

    result = await agent.run(
        "Help me complete my daily tasks. Check what's pending and notify me.",
        deps=deps,
    )

    print("Tool-enabled Agent Result:")
    print(f"Task Completed: {result.data.task_completed}")
    print(f"Steps Taken: {result.data.steps_taken}")
    print(f"Next Actions: {result.data.next_actions}")
    print()


def run_comparison_demo():
    """Run the comparison demo synchronously"""
    return asyncio.run(compare_existing_vs_pydantic())


def run_tool_demo():
    """Run the tool demo synchronously"""
    return asyncio.run(tool_enabled_agent_demo())


if __name__ == "__main__":
    print("=== Vertex AI + Pydantic AI Integration Demo ===\n")

    try:
        # Run comparison
        run_comparison_demo()

        print("\n" + "=" * 50 + "\n")

        # Run tool demo
        print("3. Tool-enabled Agent Demo:")
        run_tool_demo()

    except Exception as e:
        print(f"Demo failed: {e}")
        print("\nTo run successfully:")
        print("1. Update your credentials in create_vertex_model_wrapper()")
        print("2. Install: pip install pydantic-ai[google]")
        print("3. Make sure your Vertex AI setup is working")
