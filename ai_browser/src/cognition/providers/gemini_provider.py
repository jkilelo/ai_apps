"""Google Gemini LLM provider implementation"""

from typing import Any, Optional, Type, List, Union, Dict
from pydantic import BaseModel, TypeAdapter
from loguru import logger
import json
import base64
import os

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI library not available")

from ..llm import ILLMProvider


class GeminiProvider(ILLMProvider):
    """Google Gemini API provider"""
    
    MODEL_INFO = {
        "gemini-1.5-pro": {"context_window": 1000000, "supports_vision": True},
        "gemini-1.5-flash": {"context_window": 1000000, "supports_vision": True},
        "gemini-2.5-flash-lite": {"context_window": 1000000, "supports_vision": True},
        "gemini-pro": {"context_window": 32768, "supports_vision": False},
        "gemini-pro-vision": {"context_window": 32768, "supports_vision": True},
    }
    
    def __init__(self, api_key: Optional[str] = None, 
                 model: str = "gemini-2.5-flash-lite"):
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library is not installed")
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Google/Gemini API key not provided")
        
        self.model_name = model
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(model)
        
        # Get model info
        if model in self.MODEL_INFO:
            self.model_info = self.MODEL_INFO[model]
        else:
            logger.warning(f"Unknown model {model}, using default settings")
            self.model_info = {"context_window": 32768, "supports_vision": False}
        
        # Configure generation settings
        self.generation_config = genai.GenerationConfig(
            candidate_count=1,
            stop_sequences=None,
            temperature=0.7,
        )
    
    def get_name(self) -> str:
        return "gemini"
    
    def get_model(self) -> str:
        return self.model_name
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Gemini uses similar tokenization
        # ~1 token per 4 characters
        return len(text) // 4
    
    def get_max_context_window(self) -> int:
        return self.model_info["context_window"]
    
    async def generate(self, prompt: str, temperature: float = 0.7,
                      max_tokens: int = 2000, **kwargs) -> str:
        """Generate text response"""
        try:
            # Update generation config
            self.generation_config.temperature = temperature
            # max_tokens parameter removed as per requirements
            
            # Generate response
            response = await self.model.generate_content_async(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
    
    async def generate_structured(self, prompt: str, output_model: Type[BaseModel],
                                 temperature: float = 0.7, max_tokens: int = 2000,
                                 **kwargs) -> BaseModel:
        """Generate structured output"""
        try:
            # Handle Union types with TypeAdapter, regular BaseModel with direct method
            if hasattr(output_model, 'model_json_schema'):
                # Regular BaseModel class
                schema = output_model.model_json_schema()
            else:
                # Union type or other complex type - use TypeAdapter
                try:
                    adapter = TypeAdapter(output_model)
                    schema = adapter.json_schema()
                except Exception as adapter_error:
                    logger.error(f"Failed to create TypeAdapter for {output_model}: {adapter_error}")
                    # Fallback: try to get schema from first type if it's a Union
                    if hasattr(output_model, '__origin__') and output_model.__origin__ is Union:
                        first_type = output_model.__args__[0]
                        if hasattr(first_type, 'model_json_schema'):
                            schema = first_type.model_json_schema()
                            logger.warning(f"Using schema from first Union type: {first_type}")
                        else:
                            raise adapter_error
                    else:
                        raise adapter_error
            
            schema_str = json.dumps(schema, indent=2)
            
            enhanced_prompt = f"""{prompt}

Respond with a valid JSON object that conforms to this schema:
{schema_str}

IMPORTANT:
- Output ONLY valid JSON
- Include all required fields
- Use correct data types
- Do not include any text before or after the JSON"""
            
            # Update generation config
            self.generation_config.temperature = temperature
            # max_tokens parameter removed as per requirements
            
            # Generate response
            response = await self.model.generate_content_async(
                enhanced_prompt,
                generation_config=self.generation_config
            )
            
            # Extract and parse JSON
            json_str = response.text
            
            # Clean up if wrapped in markdown
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            # Parse and validate using appropriate method
            data = json.loads(json_str.strip())
            
            if hasattr(output_model, 'model_json_schema'):
                # Regular BaseModel
                return output_model(**data)
            else:
                # Union type - use TypeAdapter for validation
                adapter = TypeAdapter(output_model)
                return adapter.validate_python(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
            raise
        except Exception as e:
            logger.error(f"Gemini structured generation failed: {e}")
            raise
    
    async def generate_with_images(self, prompt: str, images: List[Union[str, bytes]],
                                  temperature: float = 0.7, max_tokens: int = 2000,
                                  **kwargs) -> str:
        """Generate response with image inputs"""
        if not self.model_info["supports_vision"]:
            # Switch to vision model if needed
            if "pro" in self.model_name:
                self.model = genai.GenerativeModel("gemini-pro-vision")
            else:
                raise ValueError(f"Model {self.model_name} does not support vision")
        
        try:
            # Prepare content parts
            parts = [prompt]
            
            # Add images
            for image in images:
                if isinstance(image, bytes):
                    # Create image part from bytes
                    from PIL import Image
                    import io
                    img = Image.open(io.BytesIO(image))
                    parts.append(img)
                elif isinstance(image, str):
                    if image.startswith('data:'):
                        # Extract base64 from data URL
                        base64_data = image.split(',')[1]
                        image_bytes = base64.b64decode(base64_data)
                        from PIL import Image
                        import io
                        img = Image.open(io.BytesIO(image_bytes))
                        parts.append(img)
                    elif image.startswith('http'):
                        # Gemini doesn't directly support URLs
                        raise ValueError("Please provide image as bytes or base64")
                    else:
                        # Assume base64 string
                        image_bytes = base64.b64decode(image)
                        from PIL import Image
                        import io
                        img = Image.open(io.BytesIO(image_bytes))
                        parts.append(img)
                else:
                    raise ValueError(f"Invalid image type: {type(image)}")
            
            # Update generation config
            self.generation_config.temperature = temperature
            # max_tokens parameter removed as per requirements
            
            # Generate response
            response = await self.model.generate_content_async(
                parts,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini image generation failed: {e}")
            raise
    
    async def count_tokens(self, text: str) -> int:
        """Count actual tokens using Gemini's tokenizer"""
        try:
            return self.model.count_tokens(text).total_tokens
        except:
            # Fallback to estimation
            return self.estimate_tokens(text)
    
    async def stream_generate(self, prompt: str, temperature: float = 0.7,
                            max_tokens: int = 2000, **kwargs):
        """Stream text generation"""
        try:
            # Update generation config
            self.generation_config.temperature = temperature
            # max_tokens parameter removed as per requirements
            
            # Generate streaming response
            response = await self.model.generate_content_async(
                prompt,
                generation_config=self.generation_config,
                stream=True
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}")
            raise