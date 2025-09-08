"""Anthropic Claude LLM provider implementation"""

from typing import Any, Optional, Type, List, Union, Dict
from pydantic import BaseModel, TypeAdapter
from loguru import logger
import json
import base64
import os

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available")

from ..llm import ILLMProvider


class AnthropicProvider(ILLMProvider):
    """Anthropic API provider for Claude models"""
    
    MODEL_INFO = {
        "claude-3-opus-20240229": {"context_window": 200000, "supports_vision": True},
        "claude-3-sonnet-20240229": {"context_window": 200000, "supports_vision": True},
        "claude-3-haiku-20240307": {"context_window": 200000, "supports_vision": True},
        "claude-2.1": {"context_window": 200000, "supports_vision": False},
        "claude-2.0": {"context_window": 100000, "supports_vision": False},
    }
    
    def __init__(self, api_key: Optional[str] = None, 
                 model: str = "claude-3-sonnet-20240229"):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library is not installed")
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        self.model = model
        self.client = AsyncAnthropic(api_key=self.api_key)
        
        # Validate model
        if model not in self.MODEL_INFO:
            logger.warning(f"Unknown model {model}, using default settings")
            self.model_info = {"context_window": 100000, "supports_vision": False}
        else:
            self.model_info = self.MODEL_INFO[model]
    
    def get_name(self) -> str:
        return "anthropic"
    
    def get_model(self) -> str:
        return self.model
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Claude uses a similar tokenization to GPT
        # ~1 token per 4 characters is reasonable
        return len(text) // 4
    
    def get_max_context_window(self) -> int:
        return self.model_info["context_window"]
    
    async def generate(self, prompt: str, temperature: float = 0.7,
                      max_tokens: int = 2000, **kwargs) -> str:
        """Generate text response"""
        try:
            message = await self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract text from response
            if message.content and len(message.content) > 0:
                return message.content[0].text
            return ""
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
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

Please respond with a valid JSON object that conforms to this schema:
{schema_str}

Important: 
- Respond ONLY with the JSON object
- Ensure all required fields are present
- Use the correct data types as specified"""
            
            # Generate response
            message = await self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": enhanced_prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract and parse JSON
            if message.content and len(message.content) > 0:
                json_str = message.content[0].text
                
                # Clean up JSON if wrapped in markdown
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
            
            raise ValueError("No content in response")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Anthropic structured generation failed: {e}")
            raise
    
    async def generate_with_images(self, prompt: str, images: List[Union[str, bytes]],
                                  temperature: float = 0.7, max_tokens: int = 2000,
                                  **kwargs) -> str:
        """Generate response with image inputs"""
        if not self.model_info["supports_vision"]:
            raise ValueError(f"Model {self.model} does not support vision")
        
        try:
            # Build message content with images
            content = []
            
            # Add text prompt
            content.append({"type": "text", "text": prompt})
            
            # Add images
            for image in images:
                if isinstance(image, bytes):
                    # Direct bytes
                    image_data = base64.b64encode(image).decode('utf-8')
                elif isinstance(image, str):
                    if image.startswith('data:'):
                        # Extract base64 from data URL
                        image_data = image.split(',')[1]
                    elif image.startswith('http'):
                        raise ValueError("Claude doesn't support image URLs directly")
                    else:
                        # Assume it's already base64
                        image_data = image
                else:
                    raise ValueError(f"Invalid image type: {type(image)}")
                
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",  # Assume JPEG
                        "data": image_data
                    }
                })
            
            # Create message
            message = await self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract response
            if message.content and len(message.content) > 0:
                return message.content[0].text
            return ""
            
        except Exception as e:
            logger.error(f"Anthropic image generation failed: {e}")
            raise
    
    async def stream_generate(self, prompt: str, temperature: float = 0.7,
                            max_tokens: int = 2000, **kwargs):
        """Stream text generation"""
        try:
            async with self.client.messages.stream(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            raise