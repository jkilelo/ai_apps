# Pydantic AI + Vertex AI Integration Guide

## Overview
This guide shows how to integrate Pydantic AI with your existing Vertex AI setup to build powerful AI agents while maintaining 100% compatibility with your current LLM instantiation method.

## Installation

### Step 1: Install Pydantic AI
```bash
pip install pydantic-ai[google]
```

### Step 2: Install Additional Dependencies
```bash
pip install google-genai>=0.7.0
pip install google-cloud-aiplatform>=1.60.0
```

### Step 3: Optional - Install Logfire for monitoring
```bash
pip install logfire>=0.30.0
```

## Key Benefits of This Integration

1. **100% Vertex AI Compatibility**: Uses your exact existing Vertex AI setup
2. **Structured Outputs**: Automatic validation and parsing with Pydantic models
3. **Type Safety**: Full typing support for better development experience
4. **Tools Integration**: Add function calling capabilities to your agents
5. **Dependency Injection**: Clean way to pass context and services to agents
6. **Streaming Support**: Built-in streaming capabilities
7. **Error Handling**: Robust error handling and retry mechanisms
8. **Monitoring**: Optional integration with Pydantic Logfire

## Migration Path

### Your Current Approach
```python
# Your existing gemini_llm_agent.py
from google.oauth2.credentials import Credentials
import vertexai
from vertexai.generative_models import GenerativeModel

# Your configuration
gemini_url = "https://gemini.example.com/api"
vertex_project = "your_vertex_project"
credentials = Credentials(api_key="your_api_key", api_secret="your_api_secret")

# Initialize Vertex AI
vertexai.init(
    project=vertex_project,
    credentials=credentials,
    api_endpoint=gemini_url,
    api_transport="rest"
)

# Create model
llm = GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=["You are a helpful assistant."]
)

# Make request
prompt = "What is the capital of Kenya?"
response = llm.generate(prompt)
```

### Enhanced Pydantic AI Approach
```python
# Enhanced approach with Pydantic AI
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from vertex_pydantic_integration import create_vertex_model_wrapper

# Define structured output
class GeographyResponse(BaseModel):
    answer: str = Field(description="The main answer")
    country: str = Field(description="The country name")
    confidence: float = Field(description="Confidence level 0-1", ge=0, le=1)
    additional_info: list[str] = Field(description="Additional relevant information")

# Create agent with your exact Vertex setup
model = create_vertex_model_wrapper("gemini-2.5-flash")
agent = Agent(
    model,
    output_type=GeographyResponse,
    system_prompt="You are a geography expert. Provide accurate information about world capitals."
)

# Get structured response
result = agent.run_sync("What is the capital of Kenya?")

# Access validated, structured data
print(f"Answer: {result.data.answer}")
print(f"Country: {result.data.country}")
print(f"Confidence: {result.data.confidence}")
print(f"Additional Info: {result.data.additional_info}")
```

## Example Use Cases

### 1. Task Management Agent
```python
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from dataclasses import dataclass

@dataclass
class TaskDeps:
    user_id: str
    project_id: str

class TaskOutput(BaseModel):
    tasks_created: list[str]
    priority_level: int
    estimated_hours: float
    dependencies: list[str]

agent = Agent(
    create_vertex_model_wrapper(),
    deps_type=TaskDeps,
    output_type=TaskOutput,
    system_prompt="You are a project management assistant."
)

@agent.tool
async def check_existing_tasks(ctx: RunContext[TaskDeps]) -> list[str]:
    # Your database query logic here
    return ["Task 1", "Task 2", "Task 3"]

# Usage
deps = TaskDeps(user_id="user123", project_id="proj456")
result = agent.run_sync("Create tasks for implementing user authentication", deps=deps)
```

### 2. Data Analysis Agent
```python
class AnalysisResult(BaseModel):
    summary: str
    key_insights: list[str]
    metrics: dict[str, float]
    risk_assessment: int = Field(ge=1, le=10)
    recommendations: list[str]

analysis_agent = Agent(
    create_vertex_model_wrapper(),
    output_type=AnalysisResult,
    system_prompt="You are a senior data analyst."
)

@analysis_agent.tool
async def calculate_statistics(data: list[float]) -> dict[str, float]:
    import statistics
    return {
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "std_dev": statistics.stdev(data) if len(data) > 1 else 0
    }

# Usage
result = analysis_agent.run_sync(
    "Analyze this sales data: [100, 150, 120, 180, 90, 200, 170]"
)
```

### 3. Code Review Agent
```python
class CodeReviewResult(BaseModel):
    quality_score: int = Field(ge=1, le=10)
    issues: list[str]
    suggestions: list[str]
    security_concerns: list[str]
    is_production_ready: bool

code_agent = Agent(
    create_vertex_model_wrapper(),
    output_type=CodeReviewResult,
    system_prompt="You are a senior software engineer reviewing code."
)

@code_agent.tool
async def check_security_patterns(code: str) -> list[str]:
    issues = []
    if "eval(" in code:
        issues.append("Dangerous eval() usage")
    if "exec(" in code:
        issues.append("Dangerous exec() usage")
    return issues
```

## Advanced Features

### Streaming Responses
```python
agent = Agent(create_vertex_model_wrapper())

async for message in agent.run_stream("Write a long story about space exploration"):
    print(message.data, end="", flush=True)
```

### Multi-Agent Workflows
```python
# Create specialized agents
researcher = Agent(create_vertex_model_wrapper(), system_prompt="You are a researcher.")
writer = Agent(create_vertex_model_wrapper(), system_prompt="You are a writer.")
reviewer = Agent(create_vertex_model_wrapper(), system_prompt="You are an editor.")

# Chain them together
research_result = researcher.run_sync("Research the latest AI trends")
draft = writer.run_sync(f"Write an article based on: {research_result.data}")
final_article = reviewer.run_sync(f"Edit and improve: {draft.data}")
```

### Error Handling and Fallbacks
```python
from pydantic_ai.models.fallback import FallbackModel

# Create fallback chain
primary_model = create_vertex_model_wrapper("gemini-2.5-flash")
backup_model = create_vertex_model_wrapper("gemini-1.5-flash")
fallback_model = FallbackModel(primary_model, backup_model)

agent = Agent(fallback_model)
```

## Best Practices

1. **Keep Your Existing Setup**: The integration preserves your exact Vertex AI configuration
2. **Start Simple**: Begin with basic structured outputs, then add tools and dependencies
3. **Use Type Hints**: Leverage Python's type system for better development experience
4. **Structure Your Outputs**: Always define Pydantic models for consistent responses
5. **Add Tools Gradually**: Start with simple tools, then build more complex integrations
6. **Monitor Performance**: Use Logfire or custom logging to track agent behavior
7. **Test Thoroughly**: Use Pydantic AI's built-in testing utilities

## Next Steps

1. Install the dependencies
2. Update the credentials in `vertex_pydantic_integration.py`
3. Run the demo scripts to see the integration in action
4. Start with simple agents and gradually add more features
5. Explore the examples in `pydantic_ai_agents.py` for more advanced patterns

## Files Created

- `pydantic_ai_agents.py`: Comprehensive examples of different agent types
- `vertex_pydantic_integration.py`: Custom Vertex AI wrapper for Pydantic AI
- `requirements_pydantic_ai.txt`: Additional dependencies needed
- This guide: `PYDANTIC_AI_INTEGRATION_GUIDE.md`

Your existing `gemini_llm_agent.py` remains unchanged and functional - you can use both approaches side by side during migration.
