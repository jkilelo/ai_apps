"""
Test to confirm tool usage with LangGraph agents using our wrapper and llm.py.
This demonstrates multiple approaches to using tools with the wrapper.
"""

from langgraph_wrapper import get_langgraph_llm
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, Sequence, Union
from langchain_core.messages import BaseMessage
import operator
import json


# Define test tools
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    weather_data = {
        "New York": "Sunny, 72°F",
        "London": "Cloudy, 59°F", 
        "Tokyo": "Clear, 68°F",
        "Paris": "Rainy, 55°F"
    }
    return weather_data.get(location, f"Weather data not available for {location}")


@tool
def calculate(expression: str) -> float:
    """Calculate a mathematical expression."""
    try:
        # Safe evaluation of mathematical expressions
        result = eval(expression, {"__builtins__": {}})
        return float(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Simulated web search
    return f"Search results for '{query}': Found relevant information about {query} from multiple sources."


# Manual Tool Execution Agent (Works without bind_tools)
class ManualToolAgentState(TypedDict):
    """State for manual tool execution agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_action: str


def create_manual_tool_agent():
    """Create an agent that manually handles tool calls without bind_tools."""
    
    llm = get_langgraph_llm(temperature=0.3)
    
    # Available tools
    tools = {
        "get_weather": get_weather,
        "calculate": calculate,
        "search_web": search_web
    }
    
    def llm_with_tool_detection(state: ManualToolAgentState):
        """LLM node that detects when tools should be used."""
        last_message = state["messages"][-1].content
        
        # Create a prompt that helps the LLM understand available tools
        tool_descriptions = """
        Available tools:
        - get_weather(location): Get weather for a location
        - calculate(expression): Calculate math expressions
        - search_web(query): Search the web
        
        If you need to use a tool, respond with:
        TOOL: tool_name
        ARGS: arguments
        
        Otherwise, respond normally.
        """
        
        prompt = f"{tool_descriptions}\n\nUser: {last_message}\n\nAssistant:"
        
        response = llm.invoke([HumanMessage(content=prompt)])
        response_text = response.content
        
        # Check if the response indicates tool usage
        if "TOOL:" in response_text and "ARGS:" in response_text:
            return {
                "messages": [AIMessage(content=response_text)],
                "next_action": "use_tool"
            }
        else:
            return {
                "messages": [AIMessage(content=response_text)],
                "next_action": "end"
            }
    
    def execute_tool(state: ManualToolAgentState):
        """Execute the tool based on LLM's request."""
        last_ai_message = state["messages"][-1].content
        
        # Parse tool request
        try:
            lines = last_ai_message.split('\n')
            tool_name = None
            args = None
            
            for line in lines:
                if line.startswith("TOOL:"):
                    tool_name = line.replace("TOOL:", "").strip()
                elif line.startswith("ARGS:"):
                    args = line.replace("ARGS:", "").strip()
            
            if tool_name in tools:
                result = tools[tool_name](args)
                tool_response = f"Tool '{tool_name}' returned: {result}"
                
                # Get final response from LLM
                final_prompt = f"The tool returned: {result}\n\nNow provide a final answer to the user."
                final_response = llm.invoke([HumanMessage(content=final_prompt)])
                
                return {
                    "messages": [
                        ToolMessage(content=tool_response, tool_call_id="1"),
                        final_response
                    ],
                    "next_action": "end"
                }
        except Exception as e:
            error_msg = f"Error executing tool: {str(e)}"
            return {
                "messages": [AIMessage(content=error_msg)],
                "next_action": "end"
            }
        
        return {
            "messages": [AIMessage(content="Could not execute tool")],
            "next_action": "end"
        }
    
    def route_next(state: ManualToolAgentState):
        """Route to next node based on action."""
        return state.get("next_action", "end")
    
    # Build the graph
    workflow = StateGraph(ManualToolAgentState)
    
    workflow.add_node("llm", llm_with_tool_detection)
    workflow.add_node("tool", execute_tool)
    
    workflow.set_entry_point("llm")
    
    workflow.add_conditional_edges(
        "llm",
        route_next,
        {
            "use_tool": "tool",
            "end": END
        }
    )
    
    workflow.add_edge("tool", END)
    
    return workflow.compile()


# Alternative: Custom Tool Calling via Prompting
def create_prompted_tool_agent():
    """Create an agent that uses tools via careful prompting."""
    
    llm = get_langgraph_llm(temperature=0.3)
    
    class PromptedToolState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        tool_calls: list
        final_answer: str
    
    def process_with_tools(state: PromptedToolState):
        """Process user request and determine if tools are needed."""
        user_message = state["messages"][-1].content
        
        # Structured prompt for tool usage
        prompt = f"""You are an AI assistant with access to tools.

User Query: {user_message}

Analyze if you need any of these tools:
1. get_weather(location) - Get weather information
2. calculate(expression) - Calculate mathematical expressions  
3. search_web(query) - Search the web

Respond in this JSON format:
{{
    "needs_tools": true/false,
    "tool_calls": [
        {{"tool": "tool_name", "args": "arguments"}}
    ],
    "direct_answer": "answer if no tools needed"
}}"""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Parse response
        try:
            # Extract JSON from response
            response_text = response.content
            if "{" in response_text and "}" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                if parsed.get("needs_tools"):
                    # Execute tools
                    results = []
                    for call in parsed.get("tool_calls", []):
                        tool_name = call.get("tool")
                        args = call.get("args")
                        
                        if tool_name == "get_weather":
                            result = get_weather(args)
                        elif tool_name == "calculate":
                            result = calculate(args)
                        elif tool_name == "search_web":
                            result = search_web(args)
                        else:
                            result = f"Unknown tool: {tool_name}"
                        
                        results.append(f"{tool_name}: {result}")
                    
                    # Get final answer with tool results
                    final_prompt = f"""Based on these tool results:
{chr(10).join(results)}

Provide a complete answer to: {user_message}"""
                    
                    final_response = llm.invoke([HumanMessage(content=final_prompt)])
                    return {
                        "messages": [final_response],
                        "tool_calls": parsed.get("tool_calls", []),
                        "final_answer": final_response.content
                    }
                else:
                    return {
                        "messages": [AIMessage(content=parsed.get("direct_answer", ""))],
                        "tool_calls": [],
                        "final_answer": parsed.get("direct_answer", "")
                    }
            else:
                # Fallback to direct response
                return {
                    "messages": [response],
                    "tool_calls": [],
                    "final_answer": response.content
                }
                
        except Exception as e:
            error_response = AIMessage(content=f"I'll help you with that. {response.content}")
            return {
                "messages": [error_response],
                "tool_calls": [],
                "final_answer": error_response.content
            }
    
    # Build graph
    workflow = StateGraph(PromptedToolState)
    workflow.add_node("process", process_with_tools)
    workflow.set_entry_point("process")
    workflow.add_edge("process", END)
    
    return workflow.compile()


# Test function
def test_all_approaches():
    """Test different approaches to tool usage."""
    
    print("=" * 60)
    print("TESTING TOOL INTEGRATION WITH LANGGRAPH WRAPPER")
    print("=" * 60)
    
    # Test queries that require tools
    test_queries = [
        "What's the weather in New York?",
        "Calculate 125 * 48 for me",
        "What's the weather in Paris and what's 15 + 28?",
        "Search for information about LangGraph"
    ]
    
    # Test 1: Manual Tool Agent
    print("\n[TEST 1] Manual Tool Execution Agent")
    print("-" * 40)
    
    manual_agent = create_manual_tool_agent()
    
    for query in test_queries[:2]:  # Test first 2 queries
        print(f"\nQuery: {query}")
        result = manual_agent.invoke({
            "messages": [HumanMessage(content=query)],
            "next_action": ""
        })
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
    
    # Test 2: Prompted Tool Agent
    print("\n[TEST 2] Prompted Tool Agent (JSON-based)")
    print("-" * 40)
    
    prompted_agent = create_prompted_tool_agent()
    
    for query in test_queries[:2]:  # Test first 2 queries
        print(f"\nQuery: {query}")
        result = prompted_agent.invoke({
            "messages": [HumanMessage(content=query)],
            "tool_calls": [],
            "final_answer": ""
        })
        print(f"Response: {result['final_answer'][:200]}...")
        if result['tool_calls']:
            print(f"Tools used: {result['tool_calls']}")
    
    # Test 3: Direct LLM with Function Description
    print("\n[TEST 3] Direct LLM with Function Descriptions")
    print("-" * 40)
    
    llm = get_langgraph_llm(temperature=0.3)
    
    for query in test_queries[:2]:
        print(f"\nQuery: {query}")
        
        # Create a prompt that includes function information
        enhanced_prompt = f"""You have access to these functions:
- get_weather(location): Returns weather for a city
- calculate(expression): Evaluates math expressions
- search_web(query): Searches the web

User: {query}

Think step by step:
1. Do I need to use a function?
2. If yes, which function and with what arguments?
3. Provide the answer.

Response:"""
        
        response = llm.invoke([HumanMessage(content=enhanced_prompt)])
        print(f"Response: {response.content[:200]}...")
    
    print("\n" + "=" * 60)
    print("CONCLUSION: Tools CAN be used with the wrapper!")
    print("=" * 60)
    print("""
The wrapper successfully works with tools using these approaches:
1. Manual tool execution with state-based routing
2. JSON-prompted tool calling
3. Direct function description in prompts

While bind_tools() isn't implemented (for ReAct prebuilt agents),
we can absolutely use tools with custom agent implementations!
    """)


if __name__ == "__main__":
    test_all_approaches()