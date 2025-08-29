# Fixed typo: credentails -> credentials
from google.oauth2.credentials import Credentials
import vertexai
from vertexai.generative_models import GenerativeModel

# Your Vertex AI configuration
gemini_url = "https://gemini.example.com/api"
vertex_project = "your_vertex_project"

# Update this with your actual credentials
credentials = Credentials(
    # Note: The Credentials class doesn't take api_key and api_secret directly
    # You'll need to use your actual authentication method here
    # For example:
    token="your_access_token",
    # refresh_token="your_refresh_token",
    # token_uri="https://oauth2.googleapis.com/token",
    # client_id="your_client_id",
    # client_secret="your_client_secret"
)

# Initialize Vertex AI with your configuration
vertexai.init(
    project=vertex_project,
    credentials=credentials,
    api_endpoint=gemini_url,
    api_transport="rest",
)

# Create the GenerativeModel
llm = GenerativeModel(
    model_name="gemini-2.5-flash", system_instruction=["You are a helpful assistant."]
)

# Example usage
prompt = "What is the capital of Kenya?"

# Fixed method name: generate -> generate_content
response = llm.generate_content(prompt)

print(f"Response: {response.text}")

# Optional: Add error handling
try:
    response = llm.generate_content("What is machine learning?")
    print(f"ML Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
