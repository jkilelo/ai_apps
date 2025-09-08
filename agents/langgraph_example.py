"""
Example of using the LangGraph wrapper with llm.py's existing client.
This demonstrates how to build LangGraph agents without modifying llm.py.
"""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph_wrapper import get_langgraph_llm
import operator


# Define the state for our graph
class AgentState(TypedDict):
    """State that gets passed between nodes in the graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str


def create_simple_agent():
    """Create a simple conversational agent using LangGraph and our wrapper."""
    
    # Get the wrapped LLM that uses llm.py's get_client()
    llm = get_langgraph_llm(temperature=0.7)
    
    # Define nodes
    def chatbot_node(state: AgentState) -> AgentState:
        """Process messages and generate response."""
        response = llm.invoke(state["messages"])
        return {
            "messages": [response],
            "next_step": "end"
        }
    
    def should_continue(state: AgentState) -> str:
        """Determine if we should continue or end."""
        return state.get("next_step", "chatbot")
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("chatbot", chatbot_node)
    
    # Set entry point
    workflow.set_entry_point("chatbot")
    
    # Add edges
    workflow.add_conditional_edges(
        "chatbot",
        should_continue,
        {
            "end": END,
            "chatbot": "chatbot"
        }
    )
    
    # Compile with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


def create_react_agent_example():
    """Create a ReAct agent using LangGraph prebuilts and our wrapper."""
    try:
        from langgraph.prebuilt import create_react_agent
        from langchain_core.tools import tool
        
        # Get the wrapped LLM
        llm = get_langgraph_llm(temperature=0.5)
        
        # Define some example tools
        @tool
        def get_weather(location: str) -> str:
            """Get the weather for a location."""
            return f"The weather in {location} is sunny and 72°F"
        
        @tool
        def calculate(expression: str) -> str:
            """Calculate a mathematical expression."""
            try:
                result = eval(expression)
                return f"Result: {result}"
            except:
                return "Error: Invalid expression"
        
        # Create the ReAct agent
        tools = [get_weather, calculate]
        agent = create_react_agent(llm, tools)
        
        return agent
        
    except ImportError:
        print("Note: Install langgraph with 'pip install langgraph' for ReAct agent example")
        return None


def create_multi_agent_system():
    """Create a multi-agent system using our wrapper."""
    
    # Get wrapped LLMs with different configurations
    researcher = get_langgraph_llm(temperature=0.3)  # More focused
    creative = get_langgraph_llm(temperature=0.9)    # More creative
    reviewer = get_langgraph_llm(temperature=0.5)    # Balanced
    
    class MultiAgentState(TypedDict):
        """State for multi-agent collaboration."""
        task: str
        research: str
        creative_output: str
        review: str
        messages: Sequence[BaseMessage]
    
    def research_node(state: MultiAgentState) -> MultiAgentState:
        """Research agent node."""
        prompt = f"Research the following topic and provide facts: {state['task']}"
        response = researcher.invoke([HumanMessage(content=prompt)])
        return {**state, "research": response.content}
    
    def creative_node(state: MultiAgentState) -> MultiAgentState:
        """Creative agent node."""
        prompt = f"Based on this research: {state['research']}\nCreate something creative about: {state['task']}"
        response = creative.invoke([HumanMessage(content=prompt)])
        return {**state, "creative_output": response.content}
    
    def review_node(state: MultiAgentState) -> MultiAgentState:
        """Review agent node."""
        prompt = f"Review this creative output: {state['creative_output']}\nProvide constructive feedback."
        response = reviewer.invoke([HumanMessage(content=prompt)])
        return {**state, "review": response.content, "messages": [AIMessage(content=response.content)]}
    
    # Build the graph
    workflow = StateGraph(MultiAgentState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("creative", creative_node)
    workflow.add_node("review", review_node)
    
    # Define the flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "creative")
    workflow.add_edge("creative", "review")
    workflow.add_edge("review", END)
    
    # Compile
    app = workflow.compile()
    
    return app


if __name__ == "__main__":
    print("LangGraph Integration Examples")
    print("=" * 50)
    
    # Example 1: Simple conversational agent
    print("\nExample 1: Simple Conversational Agent")
    print("-" * 40)
    
    agent = create_simple_agent()
    config = {"configurable": {"thread_id": "test-thread"}}
    
    # Test the agent
    input_message = HumanMessage(content="Hello! What's the capital of Japan?")
    result = agent.invoke({"messages": [input_message]}, config)
    print(f"User: {input_message.content}")
    print(f"Agent: {result['messages'][-1].content}")
    
    # Example 2: Multi-agent collaboration
    print("\nExample 2: Multi-Agent Collaboration")
    print("-" * 40)
    
    multi_agent = create_multi_agent_system()
    
    # Run the multi-agent system
    task = "artificial intelligence"
    result = multi_agent.invoke({"task": task, "research": "", "creative_output": "", "review": "", "messages": []})
    
    print(f"Task: Write about {task}")
    print(f"\nResearch Agent Output: {result['research'][:200]}...")
    print(f"\nCreative Agent Output: {result['creative_output'][:200]}...")
    print(f"\nReview Agent Feedback: {result['review'][:200]}...")
    
    # Example 3: ReAct Agent (if available)
    print("\nExample 3: ReAct Agent with Tools")
    print("-" * 40)
    
    react_agent = create_react_agent_example()
    if react_agent:
        # Test with tool usage
        result = react_agent.invoke({
            "messages": [HumanMessage(content="What's the weather in Paris and what's 15 * 23?")]
        })
        print(f"User: What's the weather in Paris and what's 15 * 23?")
        print(f"Agent: {result['messages'][-1].content}")
    else:
        print("ReAct agent requires additional dependencies.")
    
    print("\n[SUCCESS] All examples completed successfully!")
    print("\n[INFO] You can now use these patterns to build LangGraph agents with llm.py's client!")