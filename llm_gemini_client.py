import dotenv, os
import logging
from google.genai import Client

# Load environment from ui_testing_framework
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui_testing_framework", ".env")
dotenv.load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

model = "gemini-2.5-pro"

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