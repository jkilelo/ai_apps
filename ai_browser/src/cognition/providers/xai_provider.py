"""XAI (Grok) LLM provider implementation"""

from typing import Any, Optional, Type, List, Union, Dict
from pydantic import BaseModel, TypeAdapter
from loguru import logger
import json
import base64
import os
import httpx

from ..llm import ILLMProvider


class XAIProvider(ILLMProvider):
    """XAI (Grok) API provider"""
    
    MODEL_INFO = {
        "grok-code-fast-1": {"context_window": 128000, "supports_vision": False},
        "grok-beta": {"context_window": 131072, "supports_vision": False},
    }
    
    def __init__(self, api_key: Optional[str] = None, 
                 model: str = "grok-code-fast-1"):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("XAI API key not provided")
        
        self.model_name = model
        self.base_url = "https://api.x.ai/v1"
        
        # Get model info
        if model in self.MODEL_INFO:
            self.model_info = self.MODEL_INFO[model]
        else:
            logger.warning(f"Unknown model {model}, using default settings")
            self.model_info = {"context_window": 128000, "supports_vision": False}
        
        # Create HTTP client
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(60.0)
        )
    
    def get_name(self) -> str:
        return "xai"
    
    def get_model(self) -> str:
        return self.model_name
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Similar to GPT tokenization
        # ~1 token per 4 characters
        return len(text) // 4
    
    def get_max_context_window(self) -> int:
        return self.model_info["context_window"]
    
    async def generate(self, prompt: str, temperature: float = 0.7,
                      max_tokens: int = 2000, **kwargs) -> str:
        """Generate text response"""
        try:
            # Build request payload without max_tokens
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            
            # Make API request
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"XAI generation failed: {e}")
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
            
            # Build request payload without max_tokens
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": enhanced_prompt}],
                "temperature": temperature,
                "response_format": {"type": "json_object"}  # Request JSON mode if supported
            }
            
            # Make API request
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            json_str = data["choices"][0]["message"]["content"]
            
            # Clean up if wrapped in markdown
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            # Parse and validate using appropriate method
            parsed_data = json.loads(json_str.strip())
            
            if hasattr(output_model, 'model_json_schema'):
                # Regular BaseModel
                return output_model(**parsed_data)
            else:
                # Union type - use TypeAdapter for validation
                adapter = TypeAdapter(output_model)
                return adapter.validate_python(parsed_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"XAI structured generation failed: {e}")
            raise
    
    async def generate_with_images(self, prompt: str, images: List[Union[str, bytes]],
                                  temperature: float = 0.7, max_tokens: int = 2000,
                                  **kwargs) -> str:
        """Generate response with image inputs"""
        if not self.model_info["supports_vision"]:
            raise ValueError(f"Model {self.model_name} does not support vision")
        
        # This would be implemented if/when XAI supports vision models
        raise NotImplementedError("XAI vision models not yet supported")
    
    async def stream_generate(self, prompt: str, temperature: float = 0.7,
                            max_tokens: int = 2000, **kwargs):
        """Stream text generation"""
        try:
            # Build request payload without max_tokens
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "stream": True
            }
            
            # Make streaming API request
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            break
                        try:
                            data = json.loads(line[6:])
                            content = data["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                    
        except Exception as e:
            logger.error(f"XAI streaming failed: {e}")
            raise
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()