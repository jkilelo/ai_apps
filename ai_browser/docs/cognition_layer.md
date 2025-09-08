# Cognition Layer Documentation

## Overview

The Cognition Layer is the "brain" of the AI-First Smart Browser, responsible for AI reasoning, decision-making, and task orchestration. It interprets page states from the Perception Layer, plans actions using LLM reasoning, and sends commands to the Execution Layer.

**Layer Position**: Layer 3 of 5 in the AI-First Smart Browser architecture

**Core Responsibility**: AI reasoning and planning ONLY (no direct browser manipulation)

## Architecture Compliance

### ✅ What This Layer CAN Do:
- Import from Execution Layer (to dispatch actions)
- Import from Perception Layer (to interpret states)
- Import from Memory Layer (to store/retrieve context)
- Make LLM/AI calls for reasoning
- Generate action plans and strategies
- Implement reasoning patterns (ReAct, CoT, ToT)
- Evaluate action results and self-correct

### ❌ What This Layer CANNOT Do:
- Directly manipulate browser (no page.click, page.fill, etc.)
- Access browser contexts or pages directly
- Execute actions (must go through Execution Layer)
- Capture page state (must go through Perception Layer)
- Store persistent data (must go through Memory Layer)

## Components

### 1. LLMManager (`llm.py`)

Manages multiple LLM providers with fallback support.

**Key Features:**
- Multi-provider support (OpenAI, Anthropic, Google Gemini)
- Automatic fallback on provider failure
- Token counting and context window management
- Usage statistics tracking
- Structured output generation with Pydantic models

**Usage Example:**
```python
manager = LLMManager()
manager.register_provider("openai", OpenAIProvider(api_key))
manager.register_provider("anthropic", AnthropicProvider(api_key))

# Generate with fallback
response = await manager.fallback_generate(
    prompt="Analyze this page",
    temperature=0.7
)

# Generate structured output
action = await manager.generate_structured(
    prompt="What action should I take?",
    output_model=AgentAction
)
```

### 2. AgentOrchestrator (`orchestrator.py`)

Implements ReAct (Reasoning + Acting) loop with self-correction.

**Key Features:**
- ReAct loop: Thought → Action → Observation → Reflection
- Multiple reasoning patterns:
  - Chain-of-Thought (CoT)
  - Tree-of-Thoughts (ToT)
  - Self-Consistency
  - Direct reasoning
- Self-correction with confidence thresholds
- Conversation history management
- Performance statistics

**ReAct Configuration:**
```python
config = ReActConfig(
    max_reasoning_iterations=5,
    self_correction_threshold=0.7,
    action_confidence_required=0.8,
    enable_tree_of_thoughts=True,
    max_correction_attempts=3
)
```

**Usage Example:**
```python
orchestrator = AgentOrchestrator(llm_provider, config)

result = await orchestrator.execute_task_with_react(
    page=page,
    task="Search for Python tutorials and bookmark the best",
    reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
)

# Result includes:
# - success: bool
# - iterations: List[ReActIteration]
# - final_result: str
# - total_duration: float
```

### 3. ActionDispatcher (`dispatcher.py`)

Maps AI decisions to concrete browser actions.

**Key Features:**
- Translates AgentActions to ExecutionLayer ActionConfigs
- Manages action execution through ActionExecutor
- Captures state after actions (optional)
- Tracks action history
- Validates action parameters

**Usage Example:**
```python
dispatcher = ActionDispatcher(action_executor, state_observer)

agent_action = AgentAction(
    action_type=ActionType.CLICK,
    selector="button#submit",
    confidence=0.9,
    reasoning="Submit button identified"
)

result = await dispatcher.dispatch(
    action=agent_action,
    page=page,
    context=execution_context,
    capture_state_after=True
)
```

### 4. PromptBuilder (`prompts.py`)

Constructs structured prompts for different reasoning tasks.

**Key Features:**
- Task-specific prompt templates
- Context injection from page state
- Conversation history formatting
- System prompts for different reasoning patterns
- Error recovery prompts

**Prompt Types:**
- **Action Generation**: Decide what action to take
- **Reasoning**: Think through the problem
- **Reflection**: Evaluate results
- **Planning**: Create multi-step plans
- **Error Recovery**: Handle failures

### 5. LLM Providers (`providers/`)

Concrete implementations for different AI providers.

#### OpenAIProvider
- Models: GPT-4, GPT-4-Vision, GPT-3.5-Turbo
- Supports function calling
- Vision capabilities for screenshot analysis

#### AnthropicProvider  
- Models: Claude-3-Opus, Claude-3-Sonnet, Claude-3-Haiku
- Supports XML-based structured output
- Strong reasoning capabilities

#### GeminiProvider
- Models: Gemini-Pro, Gemini-Pro-Vision
- Multimodal support
- Google's latest AI capabilities

## Data Models (`actions.py`)

### AgentAction
Represents an AI-decided action to take.
```python
class AgentAction(BaseModel):
    action_type: ActionType
    selector: Optional[str]
    text: Optional[str]
    url: Optional[str]
    confidence: float
    reasoning: str
```

### ActionPlan
Multi-step plan for complex tasks.
```python
class ActionPlan(BaseModel):
    goal: str
    steps: List[str]
    current_step: int = 0
    confidence: float
```

### ReActIteration
Single iteration of ReAct loop.
```python
class ReActIteration(BaseModel):
    iteration_number: int
    thought: str
    action: Optional[AgentAction]
    observation: str
    reflection: Optional[str]
    confidence: float
```

## ReAct Loop Implementation

The enhanced ReAct loop follows this pattern:

```
1. THOUGHT (Reasoning)
   - Analyze current state
   - Consider task requirements
   - Evaluate available actions
   
2. ACTION (Decision)
   - Generate action with confidence score
   - Validate against thresholds
   - Prepare for execution
   
3. OBSERVATION (Execution)
   - Dispatch to Execution Layer
   - Capture results
   - Update state
   
4. REFLECTION (Evaluation)
   - Assess if goal is achieved
   - Identify errors or issues
   - Decide on continuation
   
5. ITERATION
   - Repeat until success or max iterations
   - Apply self-correction if needed
```

## Integration with Other Layers

### From Perception Layer (Layer 2):
- Receives WebPageState objects
- Gets simplified DOM and visual annotations
- Uses element mappings for action targeting

### To Execution Layer (Layer 1):
- Sends ActionConfig objects
- Never directly manipulates browser
- Receives ActionResult feedback

### With Memory Layer (Layer 4):
- Stores conversation history
- Retrieves relevant context
- Maintains session state

## Configuration

Configuration via `.claude/settings.local.json`:

```json
{
  "reasoning": {
    "enable_chain_of_thought": true,
    "max_reasoning_iterations": 5,
    "self_correction_threshold": 0.7,
    "action_confidence_required": 0.8,
    "enable_tree_of_thoughts": true
  },
  "llm_providers": [
    "openai",
    "anthropic",
    "gemini"
  ]
}
```

## Performance Optimization

1. **Token Management**: Monitor and optimize prompt sizes
2. **Provider Selection**: Choose appropriate provider for task
3. **Caching**: Cache similar reasoning patterns
4. **Parallel Processing**: Execute independent reasonings concurrently
5. **Early Stopping**: Exit loops when confidence is high

## Testing

Comprehensive unit tests in `tests/unit/test_cognition_layer.py`:

- LLMManager: 8 tests for provider management
- PromptBuilder: 3 tests for prompt construction
- ActionDispatcher: 3 tests for action dispatching
- AgentOrchestrator: 4 tests for task execution
- Layer Compliance: 2 tests ensuring no direct browser manipulation

Run tests:
```bash
pytest tests/unit/test_cognition_layer.py -v
```

## Best Practices

1. **Always validate confidence scores** before executing actions
2. **Use appropriate reasoning pattern** for task complexity
3. **Implement proper error handling** with fallbacks
4. **Log all decisions** for debugging and auditing
5. **Monitor token usage** to prevent context overflow
6. **Cache reasoning results** when possible
7. **Use structured outputs** for reliable parsing
8. **Test with multiple providers** for robustness

## Common Issues and Solutions

### Issue: Low action confidence
**Solution**: Use Tree-of-Thoughts for better exploration, adjust thresholds

### Issue: Context window overflow
**Solution**: Truncate prompts, use summarization, implement sliding window

### Issue: Provider failures
**Solution**: Configure fallback providers, implement retry logic

### Issue: Incorrect action selection
**Solution**: Improve prompts, add more context, use self-correction

## Advanced Features

### Multi-Agent Coordination
The orchestrator can coordinate multiple specialized agents:
- PlannerAgent: High-level task decomposition
- BrowserAgent: Low-level action execution
- SelfCorrectingAgent: Error recovery

### Reasoning Patterns

#### Chain-of-Thought (CoT)
Step-by-step reasoning for complex problems.

#### Tree-of-Thoughts (ToT)
Explore multiple reasoning paths and select best.

#### Self-Consistency
Generate multiple solutions and vote on best.

## Future Enhancements

- [ ] Implement more reasoning patterns (Graph-of-Thoughts)
- [ ] Add reinforcement learning for action selection
- [ ] Implement multi-modal reasoning with screenshots
- [ ] Add natural language explanations for actions
- [ ] Implement collaborative multi-agent systems
- [ ] Add A/B testing for prompt optimization

---

*Last Updated: 2025-01-05 | Layer: Cognition (3/5) | Status: Production Ready with ReAct*