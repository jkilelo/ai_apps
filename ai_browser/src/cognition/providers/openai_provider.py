"""OpenAI LLM provider implementation"""

from typing import Any, Optional, Type, List, Union, Dict
from pydantic import BaseModel, TypeAdapter
from loguru import logger
import json
import base64
import os

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available")

from ..llm import ILLMProvider


class OpenAIProvider(ILLMProvider):
    """OpenAI API provider for GPT models"""
    
    MODEL_INFO = {
        "gpt-4o": {"context_window": 128000, "supports_vision": True},
        "gpt-4o-mini": {"context_window": 128000, "supports_vision": True},
        "gpt-4-turbo": {"context_window": 128000, "supports_vision": True},
        "gpt-4": {"context_window": 8192, "supports_vision": False},
        "gpt-3.5-turbo": {"context_window": 16385, "supports_vision": False},
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o",
                 organization: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library is not installed")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.model = model
        self.organization = organization
        self.client = AsyncOpenAI(api_key=self.api_key, organization=organization)
        
        # Validate model
        if model not in self.MODEL_INFO:
            logger.warning(f"Unknown model {model}, using default settings")
            self.model_info = {"context_window": 8192, "supports_vision": False}
        else:
            self.model_info = self.MODEL_INFO[model]
    
    def get_name(self) -> str:
        return "openai"
    
    def get_model(self) -> str:
        return self.model
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # OpenAI uses tiktoken, but for simplicity:
        # ~1 token per 4 characters is a reasonable estimate
        return len(text) // 4
    
    def get_max_context_window(self) -> int:
        return self.model_info["context_window"]
    
    async def generate(self, prompt: str, temperature: float = 0.7,
                      max_tokens: int = 2000, **kwargs) -> str:
        """Generate text response"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def generate_structured(self, prompt: str, output_model: Type[BaseModel],
                                 temperature: float = 0.7, max_tokens: int = 2000,
                                 **kwargs) -> BaseModel:
        """Generate structured output using function calling"""
        # Check if output_model is a Union type
        import typing
        origin = typing.get_origin(output_model)
        
        if origin is Union or origin is typing.Union:
            # For Union types, use JSON mode directly
            return await self._generate_structured_union(
                prompt, output_model, temperature, max_tokens, **kwargs
            )
        
        try:
            # Convert Pydantic model to OpenAI function schema
            function_schema = self._pydantic_to_openai_function(output_model)
            
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Respond with the requested structured output."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=[{"type": "function", "function": function_schema}],
                tool_choice={"type": "function", "function": {"name": output_model.__name__}},
                **kwargs
            )
            
            # Extract function call arguments
            tool_call = response.choices[0].message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            
            # Create and return Pydantic model instance
            return output_model(**arguments)
            
        except Exception as e:
            logger.error(f"OpenAI structured generation failed: {e}")
            # Fallback to JSON mode
            try:
                return await self._generate_structured_json_mode(
                    prompt, output_model, temperature, max_tokens, **kwargs
                )
            except Exception as fallback_error:
                logger.error(f"Fallback JSON mode also failed: {fallback_error}")
                raise e
    
    async def _generate_structured_union(self, prompt: str, output_model: Type,
                                        temperature: float = 0.7, max_tokens: int = 2000,
                                        **kwargs) -> BaseModel:
        """Generate structured output for Union types"""
        import typing
        from pydantic import TypeAdapter
        
        # Use TypeAdapter for Union types
        adapter = TypeAdapter(output_model)
        schema = adapter.json_schema()
        schema_str = json.dumps(schema, indent=2)
        
        enhanced_prompt = f"""{prompt}

Respond with a valid JSON object that conforms to ONE of the types in this schema:
{schema_str}

IMPORTANT: 
- Choose the most appropriate action type based on the task
- Include an "action" field that specifies which action type you're using
- Respond ONLY with the JSON object, no additional text."""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that responds in JSON format."},
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            **kwargs
        )
        
        # Parse JSON and validate with TypeAdapter
        json_str = response.choices[0].message.content
        data = json.loads(json_str)
        
        # Use TypeAdapter to validate and parse
        return adapter.validate_python(data)
    
    async def _generate_structured_json_mode(self, prompt: str, output_model: Type[BaseModel],
                                            temperature: float = 0.7, max_tokens: int = 2000,
                                            **kwargs) -> BaseModel:
        """Fallback structured generation using JSON mode"""
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

Important: Respond ONLY with the JSON object, no additional text."""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that responds in JSON format."},
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            **kwargs
        )
        
        # Parse JSON and create model
        json_str = response.choices[0].message.content
        data = json.loads(json_str)
        
        if hasattr(output_model, 'model_json_schema'):
            # Regular BaseModel
            return output_model(**data)
        else:
            # Union type - use TypeAdapter for validation
            adapter = TypeAdapter(output_model)
            return adapter.validate_python(data)
    
    async def generate_with_images(self, prompt: str, images: List[Union[str, bytes]],
                                  temperature: float = 0.7, max_tokens: int = 2000,
                                  **kwargs) -> str:
        """Generate response with image inputs"""
        if not self.model_info["supports_vision"]:
            raise ValueError(f"Model {self.model} does not support vision")
        
        try:
            # Build message with images
            content = [{"type": "text", "text": prompt}]
            
            for image in images:
                if isinstance(image, bytes):
                    # Convert bytes to base64
                    image_b64 = base64.b64encode(image).decode('utf-8')
                    image_url = f"data:image/jpeg;base64,{image_b64}"
                elif isinstance(image, str):
                    if image.startswith('data:') or image.startswith('http'):
                        image_url = image
                    else:
                        # Assume it's a base64 string
                        image_url = f"data:image/jpeg;base64,{image}"
                else:
                    raise ValueError(f"Invalid image type: {type(image)}")
                
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })
            
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant that can analyze images."},
                {"role": "user", "content": content}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI image generation failed: {e}")
            raise
    
    def _pydantic_to_openai_function(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """Convert Pydantic model to OpenAI function schema"""
        # Handle Union types with TypeAdapter, regular BaseModel with direct method
        if hasattr(model, 'model_json_schema'):
            # Regular BaseModel class
            schema = model.model_json_schema()
        else:
            # Union type or other complex type - use TypeAdapter
            try:
                adapter = TypeAdapter(model)
                schema = adapter.json_schema()
            except Exception as adapter_error:
                logger.error(f"Failed to create TypeAdapter for {model}: {adapter_error}")
                # Fallback: try to get schema from first type if it's a Union
                if hasattr(model, '__origin__') and model.__origin__ is Union:
                    first_type = model.__args__[0]
                    if hasattr(first_type, 'model_json_schema'):
                        schema = first_type.model_json_schema()
                        logger.warning(f"Using schema from first Union type: {first_type}")
                    else:
                        raise adapter_error
                else:
                    raise adapter_error
        
        # Convert to OpenAI function format
        function = {
            "name": model.__name__,
            "description": model.__doc__ or f"Generate {model.__name__}",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        # Extract properties
        if "properties" in schema:
            function["parameters"]["properties"] = schema["properties"]
        
        # Extract required fields
        if "required" in schema:
            function["parameters"]["required"] = schema["required"]
        
        # Add definitions if present
        if "definitions" in schema:
            function["parameters"]["definitions"] = schema["definitions"]
        
        # Handle $defs (Pydantic v2)
        if "$defs" in schema:
            function["parameters"]["$defs"] = schema["$defs"]
        
        return function
    
    async def stream_generate(self, prompt: str, temperature: float = 0.7,
                            max_tokens: int = 2000, **kwargs):
        """Stream text generation (async generator)"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise