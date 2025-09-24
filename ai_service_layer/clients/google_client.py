import os
import subprocess
import dotenv
from google.oauth2.credentials import Credentials
from google.genai import types, Client


def find_dotenv(start_dir=None, filename=".env"):
    """Searches parent directories for a .env file and returns its path if found."""
    if start_dir is None:
        start_dir = os.path.abspath(os.path.dirname(__file__))
    current_dir = start_dir
    while True:
        candidate = os.path.join(current_dir, filename)
        if os.path.isfile(candidate):
            return candidate
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break  # Reached filesystem root
        current_dir = parent_dir
    return None


# load the .env file
env_fpath = find_dotenv()
if env_fpath is None:
    raise FileNotFoundError(".env file not found. Please ensure it exists.")
else:
    dotenv.load_dotenv(dotenv_path=env_fpath)
    print(f".env file loaded from {env_fpath}")

# Initialize client lazily only when needed
_base_params = None


def get_base_params():
    """Returns the base parameters for the genai client."""
    global _base_params
    if _base_params is None:
        _base_params = {
            "api_key": os.getenv("GEMINI_API_KEY", None) or os.getenv("GOOGLE_API_KEY", None),
            "vertexai": False,
            "credentials": None, #Credentials(subprocess.check_output("", shell=True).decode().strip()),
            "project": None,
            "location": None,
            "http_options": None, #types.HttpOptions(base_url=''),
            
        }
    return _base_params


def get_client():
    return Client(**get_base_params())


def ask(prompt: str) -> str:
    client = get_client()
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text


if __name__ == "__main__":
    # Test the client initialization
    prompt = "What's the capital of Kenya? reply in one word."
    print(ask(prompt))
