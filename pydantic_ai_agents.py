"""
Pydantic AI Agents using custom Vertex AI setup
This module demonstrates how to build AI agents with Pydantic AI while
maintaining compatibility with your existing Vertex AI configuration.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

# Import your existing Vertex AI setup
from google.oauth2.credentials import Credentials
import vertexai
from vertexai.generative_models import GenerativeModel


class VertexAICustomModel(GoogleModel):
    """
    Custom Pydantic AI Model that wraps your existing Vertex AI setup
    """

    def __init__(
        self,
        model_name: str,
        vertex_project: str,
        credentials: Credentials,
        gemini_url: str,
        system_instruction: Optional[List[str]] = None,
    ):

        # Initialize Vertex AI with your existing configuration
        vertexai.init(
            project=vertex_project,
            credentials=credentials,
            api_endpoint=gemini_url,
            api_transport="rest",
        )

        # Create your existing GenerativeModel instance
        self.vertex_model = GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction or ["You are a helpful assistant."],
        )

        # Create a custom GoogleProvider that uses your credentials
        provider = GoogleProvider(vertexai=True, credentials=credentials)

        # Initialize the parent GoogleModel with your custom provider
        super().__init__(model_name, provider=provider)

    async def request(self, messages, **kwargs):
        """Override request method to use your existing Vertex model if needed"""
        try:
            # Try using the parent GoogleModel first (for Pydantic AI features)
            return await super().request(messages, **kwargs)
        except Exception as e:
            # Fallback to your existing Vertex setup if needed
            print(f"Fallback to custom Vertex model due to: {e}")
            # Here you could implement fallback logic using your vertex_model
            raise


# Pydantic models for structured outputs
class TaskOutput(BaseModel):
    """Structured output for task completion"""

    task_description: str = Field(description="Description of the completed task")
    status: str = Field(description="Status: completed, failed, or in_progress")
    confidence: float = Field(
        description="Confidence level (0.0 to 1.0)", ge=0.0, le=1.0
    )
    recommendations: List[str] = Field(
        description="List of recommendations or next steps"
    )


class AnalysisResult(BaseModel):
    """Structured output for data analysis"""

    summary: str = Field(description="Summary of the analysis")
    key_findings: List[str] = Field(description="Key findings from the analysis")
    metrics: Dict[str, float] = Field(description="Numerical metrics")
    risk_level: int = Field(description="Risk level from 1-10", ge=1, le=10)


class CodeReviewOutput(BaseModel):
    """Structured output for code review"""

    code_quality_score: int = Field(
        description="Code quality score (1-10)", ge=1, le=10
    )
    issues_found: List[str] = Field(description="List of issues found")
    suggestions: List[str] = Field(description="Improvement suggestions")
    security_concerns: List[str] = Field(description="Security-related concerns")
    is_production_ready: bool = Field(description="Whether code is production ready")


# Dependencies for agents
@dataclass
class AgentDependencies:
    """Dependencies that can be injected into agents"""

    user_id: str
    session_id: str
    project_context: Optional[str] = None
    api_keys: Optional[Dict[str, str]] = None


def create_vertex_model(model_name: str = "gemini-2.5-flash") -> VertexAICustomModel:
    """
    Create a VertexAI model using your existing configuration
    """
    # Your existing configuration (replace with actual values)
    gemini_url = "https://gemini.example.com/api"
    vertex_project = "your_vertex_project"
    credentials = Credentials(
        # Replace with your actual credentials
        token="your_api_key"  # This might need to be adapted based on your auth
    )

    return VertexAICustomModel(
        model_name=model_name,
        vertex_project=vertex_project,
        credentials=credentials,
        gemini_url=gemini_url,
        system_instruction=["You are a helpful AI assistant."],
    )


# Create different specialized agents
def create_task_completion_agent() -> Agent[AgentDependencies, TaskOutput]:
    """
    Agent specialized in task completion and management
    """
    model = create_vertex_model()

    agent = Agent(
        model,
        deps_type=AgentDependencies,
        output_type=TaskOutput,
        system_prompt=(
            "You are a task completion specialist. Help users complete tasks efficiently "
            "and provide structured feedback with confidence levels and recommendations."
        ),
    )

    @agent.system_prompt
    async def add_user_context(ctx: RunContext[AgentDependencies]) -> str:
        return f"User ID: {ctx.deps.user_id}, Session: {ctx.deps.session_id}"

    @agent.tool
    async def check_task_status(
        ctx: RunContext[AgentDependencies], task_id: str
    ) -> str:
        """Check the status of a specific task"""
        # Implement your task checking logic here
        return f"Task {task_id} is currently in progress"

    @agent.tool
    async def create_subtasks(
        ctx: RunContext[AgentDependencies], main_task: str, complexity_level: int
    ) -> List[str]:
        """Break down a main task into subtasks"""
        # Implement subtask creation logic
        subtasks = [
            f"Subtask 1 for: {main_task}",
            f"Subtask 2 for: {main_task}",
            f"Subtask 3 for: {main_task}",
        ]
        return subtasks[:complexity_level]

    return agent


def create_data_analysis_agent() -> Agent[AgentDependencies, AnalysisResult]:
    """
    Agent specialized in data analysis and insights
    """
    model = create_vertex_model()

    agent = Agent(
        model,
        deps_type=AgentDependencies,
        output_type=AnalysisResult,
        system_prompt=(
            "You are a data analysis expert. Analyze data, provide insights, "
            "identify patterns, and assess risks with structured outputs."
        ),
    )

    @agent.system_prompt
    async def add_analysis_context(ctx: RunContext[AgentDependencies]) -> str:
        context = f"Analysis for user {ctx.deps.user_id}"
        if ctx.deps.project_context:
            context += f" in project: {ctx.deps.project_context}"
        return context

    @agent.tool
    async def calculate_metrics(
        ctx: RunContext[AgentDependencies], data_points: List[float]
    ) -> Dict[str, float]:
        """Calculate statistical metrics from data points"""
        if not data_points:
            return {"error": -1}

        import statistics

        return {
            "mean": statistics.mean(data_points),
            "median": statistics.median(data_points),
            "std_dev": statistics.stdev(data_points) if len(data_points) > 1 else 0,
            "min": min(data_points),
            "max": max(data_points),
        }

    @agent.tool
    async def assess_data_quality(
        ctx: RunContext[AgentDependencies], data_size: int, missing_values: int
    ) -> str:
        """Assess the quality of a dataset"""
        missing_percentage = (
            (missing_values / data_size) * 100 if data_size > 0 else 100
        )

        if missing_percentage < 5:
            return "High quality data with minimal missing values"
        elif missing_percentage < 15:
            return "Good quality data with some missing values"
        elif missing_percentage < 30:
            return "Fair quality data with significant missing values"
        else:
            return "Poor quality data with many missing values"

    return agent


def create_code_review_agent() -> Agent[AgentDependencies, CodeReviewOutput]:
    """
    Agent specialized in code review and security analysis
    """
    model = create_vertex_model()

    agent = Agent(
        model,
        deps_type=AgentDependencies,
        output_type=CodeReviewOutput,
        system_prompt=(
            "You are a senior software engineer specializing in code review. "
            "Analyze code for quality, security, performance, and best practices. "
            "Provide constructive feedback and actionable suggestions."
        ),
    )

    @agent.tool
    async def check_security_patterns(
        ctx: RunContext[AgentDependencies], code_snippet: str
    ) -> List[str]:
        """Check for common security vulnerabilities"""
        security_issues = []

        # Simple pattern matching (in practice, you'd use more sophisticated tools)
        if "eval(" in code_snippet:
            security_issues.append("Dangerous eval() usage detected")
        if "exec(" in code_snippet:
            security_issues.append("Dangerous exec() usage detected")
        if "subprocess.shell=True" in code_snippet:
            security_issues.append("Shell injection vulnerability possible")
        if "password" in code_snippet.lower() and "=" in code_snippet:
            security_issues.append("Potential hardcoded password")

        return security_issues

    @agent.tool
    async def analyze_complexity(
        ctx: RunContext[AgentDependencies], function_lines: int, nested_levels: int
    ) -> str:
        """Analyze code complexity"""
        if function_lines > 50 or nested_levels > 4:
            return "High complexity - consider refactoring"
        elif function_lines > 20 or nested_levels > 2:
            return "Medium complexity - acceptable but could be improved"
        else:
            return "Low complexity - well structured"

    return agent


# Simple general-purpose agent for basic queries
def create_general_assistant() -> Agent[None, str]:
    """
    General-purpose assistant for simple queries
    """
    model = create_vertex_model()

    agent = Agent(
        model,
        system_prompt="You are a helpful AI assistant. Provide clear, concise, and accurate responses.",
    )

    return agent


# Example usage functions
async def demo_task_completion():
    """Demo the task completion agent"""
    agent = create_task_completion_agent()
    deps = AgentDependencies(
        user_id="user123",
        session_id="session456",
        project_context="AI Development Project",
    )

    result = await agent.run(
        "I need to build a machine learning model for customer segmentation. "
        "Help me break this down into manageable tasks.",
        deps=deps,
    )

    print("Task Completion Agent Result:")
    print(f"Task: {result.data.task_description}")
    print(f"Status: {result.data.status}")
    print(f"Confidence: {result.data.confidence}")
    print(f"Recommendations: {result.data.recommendations}")
    print()


async def demo_data_analysis():
    """Demo the data analysis agent"""
    agent = create_data_analysis_agent()
    deps = AgentDependencies(
        user_id="analyst001",
        session_id="analysis789",
        project_context="Sales Performance Analysis",
    )

    result = await agent.run(
        "Analyze the following sales data: Q1 sales were $150k, Q2 $180k, Q3 $120k, Q4 $200k. "
        "The target was $160k per quarter. Assess performance and risks.",
        deps=deps,
    )

    print("Data Analysis Agent Result:")
    print(f"Summary: {result.data.summary}")
    print(f"Key Findings: {result.data.key_findings}")
    print(f"Metrics: {result.data.metrics}")
    print(f"Risk Level: {result.data.risk_level}")
    print()


async def demo_code_review():
    """Demo the code review agent"""
    agent = create_code_review_agent()
    deps = AgentDependencies(user_id="dev001", session_id="review123")

    code_to_review = """
def login(username, password):
    if password == "admin123":
        return True
    query = f"SELECT * FROM users WHERE username='{username}'"
    result = exec(query)
    return result
"""

    result = await agent.run(
        f"Please review this login function for security and quality:\n\n{code_to_review}",
        deps=deps,
    )

    print("Code Review Agent Result:")
    print(f"Quality Score: {result.data.code_quality_score}/10")
    print(f"Issues Found: {result.data.issues_found}")
    print(f"Suggestions: {result.data.suggestions}")
    print(f"Security Concerns: {result.data.security_concerns}")
    print(f"Production Ready: {result.data.is_production_ready}")
    print()


async def demo_general_assistant():
    """Demo the general assistant"""
    agent = create_general_assistant()

    result = await agent.run("What is the capital of Kenya?")
    print("General Assistant Result:")
    print(result.data)
    print()


# Synchronous versions for easier testing
def run_task_completion_demo():
    """Run task completion demo synchronously"""
    return asyncio.run(demo_task_completion())


def run_data_analysis_demo():
    """Run data analysis demo synchronously"""
    return asyncio.run(demo_data_analysis())


def run_code_review_demo():
    """Run code review demo synchronously"""
    return asyncio.run(demo_code_review())


def run_general_demo():
    """Run general assistant demo synchronously"""
    return asyncio.run(demo_general_assistant())


if __name__ == "__main__":
    print("=== Pydantic AI Agents Demo ===\n")

    # Run all demos
    try:
        print("1. General Assistant Demo:")
        run_general_demo()

        print("2. Task Completion Agent Demo:")
        run_task_completion_demo()

        print("3. Data Analysis Agent Demo:")
        run_data_analysis_demo()

        print("4. Code Review Agent Demo:")
        run_code_review_demo()

    except Exception as e:
        print(f"Demo failed: {e}")
        print(
            "Make sure to update your Vertex AI credentials in the create_vertex_model function"
        )
