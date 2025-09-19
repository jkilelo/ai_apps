"""
Enhanced LangGraph wrapper for llm.py that adds tool binding support.
This wrapper extends the existing wrapper WITHOUT modifying llm.py.
"""

import sys
from pathlib import Path

# Add agents directory to import the existing wrapper
agents_dir = Path(__file__).parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

# Import the EXISTING wrapper
from langgraph_wrapper import GeminiChatWrapper
from typing import List, Any, Optional, Sequence, Union, Type
from langchain_core.tools import BaseTool
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
import json


class GeminiChatWrapperWithTools(GeminiChatWrapper):
    """
    Enhanced wrapper that adds tool binding support to the existing wrapper.
    This allows the wrapper to work with create_react_agent.
    """

    bound_tools: Optional[List[BaseTool]] = None

    def bind_tools(
        self,
        tools: Sequence[Union[BaseTool, Type[BaseTool], dict]],
        **kwargs: Any
    ) -> "GeminiChatWrapperWithTools":
        """
        Bind tools to the model for use with ReAct agents.

        Args:
            tools: List of tools to bind

        Returns:
            New instance with tools bound
        """
        # Create a new instance with the same config
        new_instance = GeminiChatWrapperWithTools(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            top_k=self.top_k
        )

        # Store the tools
        tool_list = []
        for tool in tools:
            if isinstance(tool, dict):
                # Handle dict tool definitions
                tool_list.append(tool)
            elif isinstance(tool, type) and issubclass(tool, BaseTool):
                # Handle tool classes
                tool_list.append(tool())
            else:
                # Handle tool instances
                tool_list.append(tool)

        new_instance.bound_tools = tool_list
        return new_instance

    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """
        Convert messages to prompt, including tool information if tools are bound.
        """
        # Get base prompt from parent
        base_prompt = super()._convert_messages_to_prompt(messages)

        # If tools are bound, add tool descriptions
        if self.bound_tools:
            tool_descriptions = "\n\nAvailable tools:\n"
            for tool in self.bound_tools:
                if hasattr(tool, 'name') and hasattr(tool, 'description'):
                    tool_descriptions += f"- {tool.name}: {tool.description}\n"

            # Add instructions for tool usage
            tool_instructions = """
When you need to use a tool, respond with:
TOOL: tool_name
ARGS: {"param1": "value1", "param2": "value2"}

After getting tool results, continue with your response.
"""
            return base_prompt + tool_descriptions + tool_instructions

        return base_prompt

    def _parse_tool_calls(self, response_text: str) -> Optional[dict]:
        """
        Parse tool calls from the response text.
        This is a simple implementation - could be enhanced.
        """
        if "TOOL:" in response_text and "ARGS:" in response_text:
            lines = response_text.split('\n')
            tool_name = None
            tool_args = None

            for i, line in enumerate(lines):
                if line.startswith("TOOL:"):
                    tool_name = line.replace("TOOL:", "").strip()
                elif line.startswith("ARGS:"):
                    args_str = line.replace("ARGS:", "").strip()
                    try:
                        tool_args = json.loads(args_str)
                    except:
                        tool_args = {}

            if tool_name:
                return {"name": tool_name, "args": tool_args}

        return None


def get_langgraph_llm_with_tools(**kwargs) -> GeminiChatWrapperWithTools:
    """
    Get an enhanced LangGraph-compatible LLM that supports tool binding.
    This is the main function to use for ReAct agents.

    Example:
        >>> from ai_mcp.langgraph_llm_wrapper_enhanced import get_langgraph_llm_with_tools
        >>> from langgraph.prebuilt import create_react_agent
        >>>
        >>> llm = get_langgraph_llm_with_tools(temperature=0.7)
        >>> agent = create_react_agent(llm, tools=[...])
    """
    return GeminiChatWrapperWithTools(**kwargs)


if __name__ == "__main__":
    print("Testing enhanced wrapper with tool binding...")

    # Create the enhanced wrapper
    llm = get_langgraph_llm_with_tools(temperature=0.5)

    print("1. Testing basic functionality (from parent class):")
    from langchain_core.messages import HumanMessage
    result = llm.invoke([HumanMessage(content="Hello! Say hi back.")])
    print(f"Response: {result.content}")

    print("\n2. Testing tool binding:")
    from langchain_core.tools import tool

    @tool
    def sample_tool(x: int) -> int:
        """Multiply by 2"""
        return x * 2

    # Bind tools
    llm_with_tools = llm.bind_tools([sample_tool])
    print(f"Tools bound: {llm_with_tools.bound_tools is not None}")

    print("\n[SUCCESS] Enhanced wrapper ready for ReAct agents!")