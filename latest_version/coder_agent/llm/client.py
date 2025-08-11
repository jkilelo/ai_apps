#!/usr/bin/env python3
"""
Production LLM Client - CODER v3.1 Compliant
Uses REAL API connections with proper error handling
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from dotenv import load_dotenv

from .contracts import (
    LLMRequestInput, LLMResponseOutput,
    CodeGenerationInput, CodeGenerationOutput,
    LLMProvider, LLMMessage
)

# Load environment variables
env_path = Path(__file__).parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try default location
    load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionLLMClient:
    """Production-grade LLM client with CODER v3.1 compliance"""
    
    def __init__(self):
        """Initialize LLM clients with API keys from environment"""
        # OpenAI client
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Google Gemini client
        self.gemini_client = OpenAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        # Anthropic Claude client
        self.claude_client = OpenAI(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url="https://api.anthropic.com/v1/"
        )
        
        # Model mappings
        self.model_map = {
            LLMProvider.OPENAI: os.getenv("OPENAI_MODEL", "gpt-4"),
            LLMProvider.GOOGLE: os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash"),
            LLMProvider.ANTHROPIC: os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        }
        
        logger.info("Production LLM client initialized with real API connections")
    
    def query_llm(self, request: LLMRequestInput) -> LLMResponseOutput:
        """
        Query LLM with validated input contract
        
        Args:
            request: Validated LLM request
            
        Returns:
            LLMResponseOutput: Validated response with guarantees
        """
        start_time = time.time()
        
        try:
            # Select client and model
            if request.provider == LLMProvider.OPENAI:
                client = self.openai_client
                model = request.model or self.model_map[LLMProvider.OPENAI]
            elif request.provider == LLMProvider.GOOGLE:
                client = self.gemini_client
                model = request.model or self.model_map[LLMProvider.GOOGLE]
            elif request.provider == LLMProvider.ANTHROPIC:
                client = self.claude_client
                model = request.model or self.model_map[LLMProvider.ANTHROPIC]
            else:
                raise ValueError(f"Unsupported provider: {request.provider}")
            
            # Convert messages to dict format
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            # Make API call with timeout
            logger.info(f"Calling {request.provider} API with model {model}")
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                timeout=request.timeout_seconds
            )
            
            # Extract response content
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            logger.info(f"LLM response received in {execution_time_ms:.2f}ms, tokens: {tokens_used}")
            
            return LLMResponseOutput(
                success=True,
                content=content,
                provider=request.provider,
                model=model,
                tokens_used=tokens_used,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = f"LLM query failed: {str(e)}"
            logger.error(error_msg)
            
            return LLMResponseOutput(
                success=False,
                content=None,
                provider=request.provider,
                model=request.model or self.model_map.get(request.provider, "unknown"),
                tokens_used=0,
                execution_time_ms=execution_time_ms,
                error_message=error_msg
            )
    
    def generate_code(self, request: CodeGenerationInput) -> CodeGenerationOutput:
        """
        Generate code following CODER v3.1 protocol
        
        Args:
            request: Validated code generation request
            
        Returns:
            CodeGenerationOutput: Generated code with contracts and tests
        """
        start_time = time.time()
        
        try:
            # Build CODER v3.1 compliant prompt
            system_prompt = """You are a CODER v3.1 compliant code generator.
You MUST:
1. Write Pydantic v2 contracts FIRST
2. Write tests BEFORE implementation (TDD)
3. Ensure platform-agnostic code
4. Include comprehensive error handling
5. Add proper documentation
6. Follow security best practices
7. Maintain performance bounds

ALWAYS generate in this order:
1. Pydantic contracts
2. Tests (that initially fail)
3. Implementation
4. Documentation"""

            user_prompt = f"""Generate {request.language} code for the following task:

Task: {request.task_description}

Requirements:
{chr(10).join(f"- {req}" for req in request.requirements)}

Context:
{request.context or "No additional context provided"}

You MUST provide:
1. Pydantic v2 input/output contracts
2. Comprehensive tests (TDD style)
3. Production-ready implementation
4. Complete documentation

Follow CODER v3.1 protocol STRICTLY."""

            # Create LLM request
            llm_request = LLMRequestInput(
                provider=LLMProvider.OPENAI,  # Use best model for code generation
                messages=[
                    LLMMessage(role="system", content=system_prompt),
                    LLMMessage(role="user", content=user_prompt)
                ],
                temperature=0.3,  # Lower temperature for code generation
                max_tokens=8000
            )
            
            # Query LLM
            logger.info("Generating code with CODER v3.1 compliance")
            response = self.query_llm(llm_request)
            
            if not response.success:
                raise Exception(response.error_message)
            
            # Parse response to extract components
            content = response.content
            
            # Extract contracts, tests, and code sections
            contracts = self._extract_section(content, "contracts", "```python")
            tests = self._extract_section(content, "test", "```python")
            implementation = self._extract_section(content, "implementation", "```python")
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            return CodeGenerationOutput(
                success=True,
                code=implementation or content,
                tests=tests,
                contracts=contracts,
                documentation=self._extract_documentation(content),
                language=request.language,
                tokens_used=response.tokens_used,
                execution_time_ms=execution_time_ms,
                coder_v3_compliant=bool(contracts and tests)
            )
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = f"Code generation failed: {str(e)}"
            logger.error(error_msg)
            
            return CodeGenerationOutput(
                success=False,
                code=None,
                tests=None,
                contracts=None,
                documentation=None,
                language=request.language,
                tokens_used=0,
                execution_time_ms=execution_time_ms,
                error_message=error_msg,
                coder_v3_compliant=False
            )
    
    def _extract_section(self, content: str, keyword: str, delimiter: str = "```") -> Optional[str]:
        """Extract code section from response"""
        try:
            lower_content = content.lower()
            if keyword.lower() in lower_content:
                # Find code block after keyword
                start_idx = lower_content.find(keyword.lower())
                remaining = content[start_idx:]
                
                if delimiter in remaining:
                    code_start = remaining.find(delimiter) + len(delimiter)
                    # Skip language identifier if present
                    if remaining[code_start:code_start+10].strip().startswith(('python', 'javascript', 'typescript')):
                        code_start = remaining.find('\n', code_start) + 1
                    
                    code_end = remaining.find(delimiter, code_start)
                    if code_end > code_start:
                        return remaining[code_start:code_end].strip()
            
            return None
        except Exception:
            return None
    
    def _extract_documentation(self, content: str) -> Optional[str]:
        """Extract documentation from response"""
        try:
            # Look for documentation sections
            markers = ["documentation:", "## documentation", "### documentation", "docs:"]
            for marker in markers:
                if marker in content.lower():
                    start_idx = content.lower().find(marker)
                    # Extract until next section or code block
                    end_markers = ["```", "##", "###", "\n\n\n"]
                    remaining = content[start_idx + len(marker):]
                    
                    for end_marker in end_markers:
                        if end_marker in remaining:
                            end_idx = remaining.find(end_marker)
                            return remaining[:end_idx].strip()
                    
                    return remaining.strip()
            
            return None
        except Exception:
            return None
    
    def verify_connectivity(self) -> Dict[str, bool]:
        """Verify LLM connectivity for all providers"""
        results = {}
        
        test_message = LLMMessage(
            role="user",
            content="Reply with 'OK' if you receive this."
        )
        
        for provider in LLMProvider:
            try:
                request = LLMRequestInput(
                    provider=provider,
                    messages=[test_message],
                    max_tokens=10,
                    timeout_seconds=10
                )
                
                response = self.query_llm(request)
                results[provider.value] = response.success
                
                if response.success:
                    logger.info(f"✅ {provider.value} connectivity verified")
                else:
                    logger.warning(f"❌ {provider.value} connectivity failed: {response.error_message}")
                    
            except Exception as e:
                results[provider.value] = False
                logger.error(f"❌ {provider.value} connectivity error: {str(e)}")
        
        return results


# Singleton instance
_llm_client: Optional[ProductionLLMClient] = None


def get_llm_client() -> ProductionLLMClient:
    """Get singleton LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = ProductionLLMClient()
    return _llm_client