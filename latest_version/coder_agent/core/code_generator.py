#!/usr/bin/env python3
"""
Code Generator - Uses real LLM for code generation following CODER v3.1
"""

import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import structlog

from ..llm import (
    get_llm_client, 
    CodeGenerationInput, 
    CodeGenerationOutput,
    LLMRequestInput,
    LLMMessage,
    LLMProvider
)
from ..contracts.base import ValidationResult

logger = structlog.get_logger()


class CodeGenerator:
    """
    Production code generator using real LLM connections.
    Strictly follows CODER v3.1 protocol.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.llm_client = get_llm_client()
        self.generation_history: List[Dict[str, Any]] = []
        
    async def generate_code(
        self,
        task_description: str,
        language: str = "python",
        context: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        follow_coder_v3: bool = True
    ) -> CodeGenerationOutput:
        """
        Generate code using real LLM following CODER v3.1 protocol.
        
        Args:
            task_description: What code to generate
            language: Programming language
            context: Additional context or existing code
            requirements: Specific requirements
            follow_coder_v3: Whether to follow CODER v3.1 protocol
            
        Returns:
            CodeGenerationOutput with generated code, tests, and contracts
        """
        logger.info("Generating code with real LLM", language=language)
        
        # Create code generation request
        request = CodeGenerationInput(
            task_description=task_description,
            language=language,
            context=context,
            requirements=requirements or [],
            follow_coder_v3=follow_coder_v3
        )
        
        # Generate code using real LLM
        result = self.llm_client.generate_code(request)
        
        # Record in history
        self.generation_history.append({
            "task": task_description,
            "language": language,
            "success": result.success,
            "tokens": result.tokens_used,
            "coder_v3_compliant": result.coder_v3_compliant
        })
        
        if result.success:
            logger.info(
                "Code generation successful",
                tokens=result.tokens_used,
                coder_v3=result.coder_v3_compliant
            )
        else:
            logger.error("Code generation failed", error=result.error_message)
        
        return result
    
    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "review"
    ) -> Dict[str, Any]:
        """
        Analyze existing code using real LLM.
        
        Args:
            code: Code to analyze
            language: Programming language
            analysis_type: Type of analysis (review, security, performance, etc.)
            
        Returns:
            Analysis results
        """
        logger.info("Analyzing code with real LLM", type=analysis_type)
        
        # Build analysis prompt
        system_prompt = f"""You are a code analyzer performing {analysis_type} analysis.
Analyze the provided {language} code and provide:
1. Issues found
2. Suggestions for improvement
3. Security concerns (if any)
4. Performance considerations
5. CODER v3.1 compliance assessment"""

        user_prompt = f"""Analyze this {language} code:

```{language}
{code}
```

Provide a comprehensive {analysis_type} analysis."""

        # Create LLM request
        request = LLMRequestInput(
            provider=LLMProvider.OPENAI,
            messages=[
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        # Query LLM
        response = self.llm_client.query_llm(request)
        
        if response.success:
            # Parse analysis results
            analysis = self._parse_analysis(response.content)
            analysis["tokens_used"] = response.tokens_used
            analysis["success"] = True
            return analysis
        else:
            return {
                "success": False,
                "error": response.error_message,
                "issues": [],
                "suggestions": []
            }
    
    async def fix_code(
        self,
        code: str,
        error_message: str,
        language: str = "python"
    ) -> CodeGenerationOutput:
        """
        Fix code based on error message using real LLM.
        
        Args:
            code: Code with error
            error_message: Error message to fix
            language: Programming language
            
        Returns:
            Fixed code with explanation
        """
        logger.info("Fixing code with real LLM", language=language)
        
        task_description = f"""Fix the following {language} code that produces this error:

Error: {error_message}

Code:
```{language}
{code}
```

Fix the code and ensure it:
1. Resolves the error
2. Follows best practices
3. Includes proper error handling
4. Has Pydantic v2 contracts (if Python)"""

        return await self.generate_code(
            task_description=task_description,
            language=language,
            context=code,
            requirements=[
                "Fix the error",
                "Maintain existing functionality",
                "Add error handling",
                "Follow CODER v3.1 principles"
            ],
            follow_coder_v3=True
        )
    
    async def generate_tests(
        self,
        code: str,
        language: str = "python",
        test_framework: Optional[str] = None
    ) -> str:
        """
        Generate tests for code using real LLM.
        
        Args:
            code: Code to test
            language: Programming language
            test_framework: Testing framework to use
            
        Returns:
            Generated test code
        """
        logger.info("Generating tests with real LLM", language=language)
        
        if language == "python" and not test_framework:
            test_framework = "pytest"
        elif language == "javascript" and not test_framework:
            test_framework = "jest"
        
        system_prompt = f"""You are a test generator following TDD principles.
Generate comprehensive tests for the provided code using {test_framework}.
Include:
1. Unit tests for all functions
2. Edge case tests
3. Error handling tests
4. Integration tests (if applicable)
5. Performance tests (if relevant)"""

        user_prompt = f"""Generate tests for this {language} code:

```{language}
{code}
```

Use {test_framework} and ensure 100% code coverage."""

        request = LLMRequestInput(
            provider=LLMProvider.OPENAI,
            messages=[
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ],
            temperature=0.3,
            max_tokens=6000
        )
        
        response = self.llm_client.query_llm(request)
        
        if response.success:
            # Extract test code
            test_code = self._extract_code_block(response.content, language)
            return test_code or response.content
        else:
            raise Exception(f"Test generation failed: {response.error_message}")
    
    async def validate_coder_v3_compliance(
        self,
        code: str,
        tests: Optional[str] = None,
        contracts: Optional[str] = None,
        language: str = "python"
    ) -> ValidationResult:
        """
        Validate code against CODER v3.1 requirements.
        
        Args:
            code: Implementation code
            tests: Test code
            contracts: Pydantic contracts
            language: Programming language
            
        Returns:
            Validation result with compliance assessment
        """
        logger.info("Validating CODER v3.1 compliance")
        
        failures = []
        warnings = []
        
        # Check for required components
        if not contracts and language == "python":
            failures.append("Missing Pydantic v2 contracts")
        
        if not tests:
            failures.append("Missing tests (TDD required)")
        
        # Use LLM to check compliance
        system_prompt = """You are a CODER v3.1 compliance validator.
Check if the code follows all CODER v3.1 requirements:
1. Pydantic v2 contracts for ALL functions
2. TDD (tests written before implementation)
3. Platform-agnostic code
4. Security best practices
5. Performance considerations
6. Proper error handling
7. No hardcoded values
8. Comprehensive documentation

Respond with JSON: {"compliant": bool, "issues": [...], "score": 0-100}"""

        components = f"""
Code:
```{language}
{code}
```

Tests:
```{language}
{tests or "NOT PROVIDED"}
```

Contracts:
```{language}
{contracts or "NOT PROVIDED"}
```
"""

        request = LLMRequestInput(
            provider=LLMProvider.OPENAI,
            messages=[
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=components)
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        response = self.llm_client.query_llm(request)
        
        if response.success:
            try:
                import json
                result = json.loads(response.content)
                
                if not result.get("compliant", False):
                    failures.extend(result.get("issues", []))
                
                return ValidationResult(
                    passed=len(failures) == 0,
                    failures=failures,
                    warnings=warnings,
                    score=result.get("score", 0) / 100.0
                )
            except:
                # Fallback if JSON parsing fails
                pass
        
        # Basic validation if LLM fails
        return ValidationResult(
            passed=len(failures) == 0,
            failures=failures,
            warnings=warnings,
            score=0.5 if not failures else 0.0
        )
    
    def _parse_analysis(self, content: str) -> Dict[str, Any]:
        """Parse analysis results from LLM response."""
        analysis = {
            "issues": [],
            "suggestions": [],
            "security_concerns": [],
            "performance_notes": [],
            "coder_v3_compliance": False
        }
        
        try:
            # Simple parsing - could be enhanced with structured output
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detect sections
                if "issue" in line.lower() or "problem" in line.lower():
                    current_section = "issues"
                elif "suggestion" in line.lower() or "improvement" in line.lower():
                    current_section = "suggestions"
                elif "security" in line.lower():
                    current_section = "security_concerns"
                elif "performance" in line.lower():
                    current_section = "performance_notes"
                elif "coder" in line.lower() and "v3" in line.lower():
                    if "compliant" in line.lower() or "yes" in line.lower():
                        analysis["coder_v3_compliance"] = True
                elif current_section and line.startswith(('-', '*', '•', '1', '2', '3')):
                    # Add to current section
                    clean_line = line.lstrip('-*•0123456789. ')
                    if clean_line:
                        analysis[current_section].append(clean_line)
        except:
            pass
        
        return analysis
    
    def _extract_code_block(self, content: str, language: str) -> Optional[str]:
        """Extract code block from LLM response."""
        try:
            # Look for code blocks
            marker = f"```{language}"
            if marker in content:
                start = content.find(marker) + len(marker)
                end = content.find("```", start)
                if end > start:
                    return content[start:end].strip()
            
            # Fallback to generic code block
            if "```" in content:
                start = content.find("```") + 3
                # Skip language identifier
                if content[start:start+20].strip().split()[0].isalpha():
                    start = content.find('\n', start) + 1
                end = content.find("```", start)
                if end > start:
                    return content[start:end].strip()
        except:
            pass
        
        return None