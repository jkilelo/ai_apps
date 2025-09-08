"""
LangGraph-compatible wrapper for the existing llm.py Google Gemini client.
This wrapper allows LangGraph to use the existing get_client() function without modification.
"""

import sys
import os
from typing import List, Optional, Any, Iterator, AsyncIterator
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.messages import AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk
import asyncio

# Import the existing llm.py functions
from llm import get_client, model as default_model


class GeminiChatWrapper(BaseChatModel):
    """
    A LangChain-compatible wrapper for the existing Google Gemini client from llm.py.
    This allows LangGraph to use the existing client without modification.
    """
    
    model_name: str = default_model
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for this model."""
        return "gemini-custom-wrapper"
    
    @property
    def _identifying_params(self) -> dict:
        """Return model parameters for identification."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
        }
    
    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a single prompt string for Gemini."""
        prompt_parts = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                prompt_parts.append(f"System: {message.content}")
            elif isinstance(message, HumanMessage):
                prompt_parts.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {message.content}")
            else:
                prompt_parts.append(str(message.content))
        
        return "\n\n".join(prompt_parts)
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response using the existing Gemini client."""
        # Get the client from llm.py
        client = get_client()
        
        # Convert messages to prompt
        prompt = self._convert_messages_to_prompt(messages)
        
        # Prepare generation config
        generation_config = {
            "temperature": kwargs.get("temperature", self.temperature),
        }
        
        if self.max_tokens:
            generation_config["max_output_tokens"] = self.max_tokens
        if self.top_p:
            generation_config["top_p"] = self.top_p
        if self.top_k:
            generation_config["top_k"] = self.top_k
        if stop:
            generation_config["stop_sequences"] = stop
        
        # Use the client's generate_content method
        response = client.models.generate_content(
            model=kwargs.get("model", self.model_name),
            contents=prompt,
            config=generation_config
        )
        
        # Extract the response text
        response_text = response.text if response and response.text else ""
        
        # Create AIMessage
        message = AIMessage(content=response_text)
        
        # Create ChatGeneration
        generation = ChatGeneration(message=message)
        
        # Create and return ChatResult
        return ChatResult(generations=[generation])
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream responses from Gemini."""
        # Note: Google's genai client doesn't support streaming in the same way
        # We'll simulate streaming by yielding the full response in chunks
        result = self._generate(messages, stop, run_manager, **kwargs)
        
        # Get the full response text
        full_text = result.generations[0].message.content
        
        # Simulate streaming by yielding chunks
        chunk_size = 50  # Characters per chunk
        for i in range(0, len(full_text), chunk_size):
            chunk_text = full_text[i:i+chunk_size]
            message_chunk = AIMessageChunk(content=chunk_text)
            chunk_result = ChatGenerationChunk(message=message_chunk)
            if run_manager:
                run_manager.on_llm_new_token(chunk_text)
            yield chunk_result
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async generation - wraps sync generation in async."""
        return await asyncio.get_event_loop().run_in_executor(
            None,
            self._generate,
            messages,
            stop,
            run_manager,
            **kwargs
        )
    
    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Async streaming - wraps sync streaming in async."""
        for chunk in self._stream(messages, stop, None, **kwargs):
            if run_manager:
                await run_manager.on_llm_new_token(chunk.message.content)
            yield chunk


def create_langgraph_model(**kwargs) -> GeminiChatWrapper:
    """
    Factory function to create a LangGraph-compatible model using the existing client.
    
    Args:
        **kwargs: Optional parameters for the model (temperature, max_tokens, etc.)
    
    Returns:
        GeminiChatWrapper: A LangGraph-compatible chat model
    
    Example:
        >>> model = create_langgraph_model(temperature=0.5)
        >>> # Use with LangGraph
        >>> from langgraph.prebuilt import create_react_agent
        >>> agent = create_react_agent(model, tools=[...])
    """
    return GeminiChatWrapper(**kwargs)


# For direct LangGraph usage
def get_langgraph_llm(**kwargs) -> GeminiChatWrapper:
    """
    Get a LangGraph-compatible LLM instance using the existing client.
    This is the main function to use when integrating with LangGraph.
    
    Example:
        >>> from agents.langgraph_wrapper import get_langgraph_llm
        >>> from langgraph.prebuilt import create_react_agent
        >>> 
        >>> llm = get_langgraph_llm(temperature=0.7)
        >>> agent = create_react_agent(llm, tools=[...])
    """
    return GeminiChatWrapper(**kwargs)


if __name__ == "__main__":
    # Test the wrapper
    print("Testing LangGraph wrapper for llm.py...")
    
    # Create the wrapped model
    llm = get_langgraph_llm(temperature=0.5)
    
    # Test with messages
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What's the capital of France? Answer in one word.")
    ]
    
    print("\n1. Testing non-streaming generation:")
    result = llm.invoke(messages)
    print(f"Response: {result.content}")
    
    print("\n2. Testing streaming generation:")
    print("Response: ", end="")
    for chunk in llm.stream(messages):
        print(chunk.content, end="", flush=True)
    print()
    
    print("\n3. Testing with LangChain integration:")
    from langchain_core.prompts import ChatPromptTemplate
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"input": "What's 2+2? Answer with just the number."})
    print(f"Math response: {response.content}")
    
    print("\n[SUCCESS] LangGraph wrapper is ready to use!")