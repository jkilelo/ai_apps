import os
from google.oauth2.credentials import Credentials
from google.genai.types import HttpOptions
from google import genai

def initialize_client():
    """Initialize the Gemini client with fresh credentials."""
    credentials = None
    try:
        credentials = Credentials("123")
        client = genai.Client(
            http_options=HttpOptions(base_url=os.getenv("BASE_URL_VERTEX")),
            credentials=credentials,
            project=os.getenv("VERTEX_PROJECT_ID"),
            vertexai=True,
            location=os.getenv("VERTEX_PROJECT_LOCATION"),
        )
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        raise
    return client