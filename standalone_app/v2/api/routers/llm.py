"""LLM Router with improved error handling and caching"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel, Field, validator
import hashlib
import json

from services.llm_service import LLMService
from services.cache import CacheService
from services.validation import validate_prompt

router = APIRouter()
llm_service = LLMService()
cache_service = CacheService()

class LLMQueryRequest(BaseModel):
    """LLM query request model with validation"""
    prompt: str = Field(..., min_length=1, max_length=4000, description="The prompt to send to the LLM")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(2000, ge=1, le=4000, description="Maximum tokens in response")
    model: str = Field("gpt-4", description="Model to use")
    
    @validator('prompt')
    def validate_prompt_content(cls, v):
        """Validate prompt content"""
        # Remove excessive whitespace
        v = ' '.join(v.split())
        
        # Check for minimum meaningful content
        if len(v.strip()) < 3:
            raise ValueError("Prompt must contain meaningful content")
        
        return v

class LLMQueryResponse(BaseModel):
    """LLM query response model"""
    response: str
    model: str
    tokens_used: Optional[int] = None
    cache_hit: bool = False
    request_id: Optional[str] = None

@router.post("/llm_query", response_model=LLMQueryResponse)
async def query_llm(
    request: LLMQueryRequest,
    req: Request
):
    """
    Query the LLM with advanced features:
    - Input validation
    - Response caching
    - Error handling
    - Request tracking
    """
    request_id = getattr(req.state, 'request_id', None)
    
    try:
        # Validate prompt
        validation_result = validate_prompt(request.prompt)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid prompt: {validation_result['reason']}"
            )
        
        # Generate cache key
        cache_key = generate_cache_key(request)
        
        # Check cache
        cached_response = await cache_service.get(cache_key)
        if cached_response:
            return LLMQueryResponse(
                response=cached_response["response"],
                model=cached_response["model"],
                tokens_used=cached_response.get("tokens_used"),
                cache_hit=True,
                request_id=request_id
            )
        
        # Query LLM
        result = await llm_service.query(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            model=request.model
        )
        
        # Cache successful response
        await cache_service.set(
            cache_key,
            {
                "response": result["response"],
                "model": result["model"],
                "tokens_used": result.get("tokens_used")
            },
            ttl=3600  # Cache for 1 hour
        )
        
        return LLMQueryResponse(
            response=result["response"],
            model=result["model"],
            tokens_used=result.get("tokens_used"),
            cache_hit=False,
            request_id=request_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM query error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process LLM query"
        )

@router.post("/llm_stream")
async def stream_llm(request: LLMQueryRequest, req: Request):
    """
    Stream LLM responses using Server-Sent Events
    """
    from fastapi.responses import StreamingResponse
    import asyncio
    
    async def generate():
        try:
            async for chunk in llm_service.stream(
                prompt=request.prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                model=request.model
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                await asyncio.sleep(0)  # Yield control
                
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable Nginx buffering
        }
    )

@router.get("/llm_models")
async def get_available_models():
    """Get list of available LLM models"""
    try:
        models = await llm_service.get_available_models()
        return {
            "models": models,
            "default": "gpt-4"
        }
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available models"
        )

def generate_cache_key(request: LLMQueryRequest) -> str:
    """Generate a cache key for the request"""
    # Create a dictionary of relevant fields
    key_data = {
        "prompt": request.prompt,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "model": request.model
    }
    
    # Convert to JSON and hash
    key_string = json.dumps(key_data, sort_keys=True)
    return f"llm:{hashlib.sha256(key_string.encode()).hexdigest()}"

# Import logger
import logging
logger = logging.getLogger(__name__)