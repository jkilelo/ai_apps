import os
from pathlib import Path
import sys
from openai import OpenAI
import json
import logging
import time
from openai.types.chat import ChatCompletion


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Add project root to path
sys.path.append(str(Path(__file__).parent))
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# clients
gemini_client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),  # Your Google API key
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
openai_client = OpenAI()

claude_client = OpenAI(
    api_key=os.getenv("ANTHROPIC_API_KEY"),  # Your Anthropic API key
    base_url="https://api.anthropic.com/v1/"  # Anthropic's API endpoint
)



def query_llm(provider, model, messages) -> ChatCompletion:
    """Query the LLM with the given provider, model, and messages."""
    if provider == "gemini":
        return gemini_client.chat.completions.create(
            model=model,
            messages=messages
        )
    elif provider == "openai":
        return openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
    elif provider == "claude":
        return claude_client.chat.completions.create(
            model=model,
            messages=messages
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def default_llm(messages: list = None) -> ChatCompletion:   
    timeout: int = 30 
    provider: str = "openai"
    model: str = "gpt-4.1"
    """Default LLM query function."""
    if messages is None:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that genuinely helps users."
            },
            {
                "role": "user",
                "content": "What is the meaning of life? Reply with 10 words or less."
            }
        ]
    
    start_time = time.time()
    response = query_llm(provider, model, messages)
    
    elapsed_time = time.time() - start_time
    if elapsed_time > timeout:
        logging.warning(f"Response took too long: {elapsed_time:.2f} seconds")
    
    return response
if __name__ == "__main__":
    # test all llm
    provider_and_models = [
        ("gemini", "gemini-2.5-pro"),
        ("openai", "gpt-4.1"),
        ("claude", "claude-sonnet-4-20250514")
    ]
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that genuinely helps users."
        },
        {
            "role": "user",
            "content": "What is the meaning of life? Reply with 10 words or less."
        }
    ]
    for provider, model in provider_and_models:
        response = query_llm(provider, model, messages)
        res = response.model_dump()
        logging.info(f"Response from {provider}: {res}")