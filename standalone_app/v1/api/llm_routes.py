"""
LLM query API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import os
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize OpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


class LLMQueryRequest(BaseModel):
    input: str


class LLMQueryResponse(BaseModel):
    output: str


@router.post("/llm_query", response_model=LLMQueryResponse)
async def llm_query(request: LLMQueryRequest):
    """
    Process LLM query
    """
    try:
        if not request.input:
            raise HTTPException(status_code=400, detail="Input cannot be empty")
        
        # Call OpenAI API
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant specialized in web automation and data quality analysis."},
                {"role": "user", "content": request.input}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        output = response.choices[0].message.content
        
        return LLMQueryResponse(output=output)
        
    except Exception as e:
        logger.error(f"LLM query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM query failed: {str(e)}")