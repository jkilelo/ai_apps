import dotenv, os
import logging
from typing import Optional
from google.genai import Client

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

# Load environment from ui_testing_framework
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui_testing_framework", ".env")
dotenv.load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

model = "gemini-2.5-flash"

# Initialize client lazily only when needed
_client = None

def get_api_key() -> str:
    """Get API key from environment."""
    # Try GEMINI_API_KEY first, then fall back to GOOGLE_API_KEY
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "No GEMINI_API_KEY or GOOGLE_API_KEY found. Please set a valid API key in environment variables."
        )
    return api_key

def get_client():
    global _client
    if _client is None:
        api_key = get_api_key()
        _client = Client(api_key=api_key)
    return _client

############ BASE FUNCTIONS #
def agent():
    return Agent(GoogleModel(model, provider=GoogleProvider(client=get_client())))

def llm():
    return get_client().models.generate_content

####### SIMPLE USAGE FUNCTIONS ##
def ask_llm(prompt: str) -> str:
    """Ask LLM directly."""
    logger.info(f"LLM prompt: {prompt[:100]}...")
    
    try:
        l = llm()
        response = l(model=model, contents=prompt)
        
        if response and response.text:
            return response.text
        else:
            return ""
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise

def ask_agent(prompt: str) -> str:
    """Ask agent directly."""
    logger.info(f"Agent prompt: {prompt[:100]}...")
    
    try:
        a = agent()
        result = a.run_sync(prompt)
        
        if result:
            return str(result)
        else:
            return ""
    except Exception as e:
        logger.error(f"Agent call failed: {e}")
        raise

if __name__ == "__main__":
    # Simple test
    try:
        prompt = "What's the capital of Kenya? Reply in one word."
        print("Testing LLM call...")
        print(ask_llm(prompt))
        print("\nTesting agent call...")
        print(ask_agent(prompt))
    except Exception as e:
        print(f"Error during testing: {e}")
