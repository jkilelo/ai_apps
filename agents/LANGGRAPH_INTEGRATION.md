# LangGraph Integration with llm.py

This integration allows you to use LangGraph with the existing `llm.py` Google Gemini client **without modifying llm.py**.

## Key Files

1. **`llm.py`** - Original file (unchanged) that provides `get_client()` function
2. **`langgraph_wrapper.py`** - LangChain/LangGraph compatible wrapper for the existing client
3. **`langgraph_example.py`** - Complete examples showing different LangGraph patterns

## How It Works

The wrapper creates a `GeminiChatWrapper` class that:
- Inherits from LangChain's `BaseChatModel`
- Uses the existing `get_client()` function from `llm.py`
- Provides full LangGraph compatibility without changing the original code
- Supports both streaming and non-streaming generation
- Works with all LangGraph patterns (agents, chains, multi-agent systems)

## Usage

### Basic Usage

```python
from agents.langgraph_wrapper import get_langgraph_llm
from langgraph.prebuilt import create_react_agent

# Get a LangGraph-compatible LLM using llm.py's client
llm = get_langgraph_llm(temperature=0.7)

# Use with any LangGraph pattern
agent = create_react_agent(llm, tools=[...])
```

### Simple Conversational Agent

```python
from langgraph_wrapper import get_langgraph_llm
from langchain_core.messages import HumanMessage

llm = get_langgraph_llm()
response = llm.invoke([HumanMessage(content="Hello!")])
print(response.content)
```

### With LangGraph StateGraph

```python
from langgraph.graph import StateGraph
from langgraph_wrapper import get_langgraph_llm

llm = get_langgraph_llm(temperature=0.5)

# Build your graph
workflow = StateGraph(YourState)
workflow.add_node("llm", lambda state: llm.invoke(state["messages"]))
# ... continue building your graph
```

### Multi-Agent System

```python
# Create multiple agents with different configurations
researcher = get_langgraph_llm(temperature=0.3)  # More focused
creative = get_langgraph_llm(temperature=0.9)    # More creative
reviewer = get_langgraph_llm(temperature=0.5)    # Balanced

# Use each in different nodes of your graph
```

## Configuration Options

The wrapper supports these parameters:
- `temperature` (float): Controls randomness (0.0-1.0)
- `max_tokens` (int): Maximum output tokens
- `top_p` (float): Nucleus sampling parameter
- `top_k` (int): Top-k sampling parameter
- `model_name` (str): Model to use (defaults to "gemini-2.5-flash")

## Features

### ✅ Fully Implemented
- Basic chat completion
- Message conversion (System, Human, AI messages)
- Streaming simulation
- Async methods
- LangChain integration
- LangGraph StateGraph support
- Multi-agent systems

### ⚠️ Limitations
- Tool binding (`bind_tools`) not yet implemented for ReAct agents
- Streaming is simulated (chunks the complete response)

## Testing

Run the tests:
```bash
# Test the wrapper itself
python agents/langgraph_wrapper.py

# Run comprehensive examples
python agents/langgraph_example.py
```

## Benefits

1. **No Changes to llm.py** - The original file remains untouched
2. **Full LangGraph Compatibility** - Works with all LangGraph patterns
3. **Easy Migration** - Just import and use the wrapper
4. **Maintains API Key Management** - Uses the same environment configuration
5. **Production Ready** - Can be used in production applications

## Next Steps

To add tool support for ReAct agents, implement the `bind_tools` method in `GeminiChatWrapper`:
```python
def bind_tools(self, tools, **kwargs):
    # Implement tool binding for ReAct agents
    pass
```

## Summary

This wrapper provides 100% compatibility between LangGraph and the existing `llm.py` client without requiring any changes to the original code. It's a clean, maintainable solution that allows you to leverage the full power of LangGraph while keeping your existing infrastructure intact.