#!/usr/bin/env python3
"""
Tests for Production LLM Client - CODER v3.1 Compliant
Tests MUST be written BEFORE implementation
"""

import pytest
import sys
from pathlib import Path
from typing import List

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from coder_agent.llm.contracts import (
    LLMRequestInput, LLMResponseOutput,
    CodeGenerationInput, CodeGenerationOutput,
    LLMProvider, LLMMessage
)
from coder_agent.llm.client import ProductionLLMClient, get_llm_client
from pydantic import ValidationError


class TestLLMContracts:
    """Test Pydantic v2 contracts enforcement"""
    
    def test_llm_message_validation(self):
        """Test message validation"""
        # Valid message
        msg = LLMMessage(role="user", content="Test message")
        assert msg.role == "user"
        assert msg.content == "Test message"
        
        # Invalid role
        with pytest.raises(ValidationError):
            LLMMessage(role="invalid", content="Test")
        
        # Empty content
        with pytest.raises(ValidationError):
            LLMMessage(role="user", content="")
    
    def test_llm_request_validation(self):
        """Test request validation"""
        # Valid request
        request = LLMRequestInput(
            provider=LLMProvider.OPENAI,
            messages=[LLMMessage(role="user", content="Test")]
        )
        assert request.provider == LLMProvider.OPENAI
        assert len(request.messages) == 1
        
        # No user message
        with pytest.raises(ValidationError):
            LLMRequestInput(
                messages=[LLMMessage(role="system", content="System only")]
            )
        
        # Invalid temperature
        with pytest.raises(ValidationError):
            LLMRequestInput(
                messages=[LLMMessage(role="user", content="Test")],
                temperature=3.0  # Too high
            )
    
    def test_code_generation_input_validation(self):
        """Test code generation input validation"""
        # Valid input
        input_data = CodeGenerationInput(
            task_description="Create a function to sort a list",
            language="python"
        )
        assert input_data.language == "python"
        
        # Invalid language
        with pytest.raises(ValidationError):
            CodeGenerationInput(
                task_description="Test task",
                language="cobol"  # Not supported
            )
        
        # Too short description
        with pytest.raises(ValidationError):
            CodeGenerationInput(task_description="Test")


class TestProductionLLMClient:
    """Test production LLM client"""
    
    @pytest.fixture
    def client(self):
        """Get LLM client instance"""
        return get_llm_client()
    
    def test_client_initialization(self, client):
        """Test client initializes with API keys"""
        assert client is not None
        assert client.openai_client is not None
        assert client.gemini_client is not None
        assert client.claude_client is not None
    
    @pytest.mark.integration
    def test_connectivity_verification(self, client):
        """Test LLM connectivity verification"""
        results = client.verify_connectivity()
        
        # At least one provider should be connected
        assert any(results.values()), "No LLM providers are connected"
        
        # Log results
        for provider, connected in results.items():
            print(f"{provider}: {'✅' if connected else '❌'}")
    
    @pytest.mark.integration
    def test_real_llm_query(self, client):
        """Test actual LLM query"""
        request = LLMRequestInput(
            provider=LLMProvider.OPENAI,
            messages=[
                LLMMessage(role="system", content="You are a helpful assistant."),
                LLMMessage(role="user", content="Reply with 'Hello World' only.")
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        response = client.query_llm(request)
        
        assert isinstance(response, LLMResponseOutput)
        assert response.success == True
        assert response.content is not None
        assert "hello" in response.content.lower() or "world" in response.content.lower()
        assert response.tokens_used > 0
        assert response.execution_time_ms > 0
    
    @pytest.mark.integration
    def test_code_generation(self, client):
        """Test code generation with CODER v3.1 compliance"""
        request = CodeGenerationInput(
            task_description="Create a Python function that validates email addresses using regex",
            language="python",
            requirements=[
                "Use Pydantic v2 for input/output contracts",
                "Include comprehensive tests",
                "Handle edge cases"
            ],
            follow_coder_v3=True
        )
        
        response = client.generate_code(request)
        
        assert isinstance(response, CodeGenerationOutput)
        assert response.success == True
        assert response.code is not None
        assert response.language == "python"
        
        # Should have CODER v3.1 components
        if response.coder_v3_compliant:
            assert response.contracts is not None
            assert response.tests is not None
    
    def test_error_handling(self, client):
        """Test error handling with invalid provider"""
        request = LLMRequestInput(
            provider=LLMProvider.OPENAI,
            messages=[LLMMessage(role="user", content="Test")],
            timeout_seconds=1  # Very short timeout to force error
        )
        
        # Modify model to invalid one
        request.model = "invalid-model-xyz"
        
        response = client.query_llm(request)
        
        assert isinstance(response, LLMResponseOutput)
        # Should handle error gracefully
        assert response.error_message is not None
    
    def test_section_extraction(self, client):
        """Test code section extraction"""
        sample_content = """
        Here is the solution:
        
        ## Contracts
        ```python
        from pydantic import BaseModel
        
        class Input(BaseModel):
            value: str
        ```
        
        ## Tests
        ```python
        def test_function():
            assert True
        ```
        
        ## Implementation
        ```python
        def main():
            return "Hello"
        ```
        """
        
        contracts = client._extract_section(sample_content, "contracts", "```python")
        tests = client._extract_section(sample_content, "tests", "```python")
        impl = client._extract_section(sample_content, "implementation", "```python")
        
        assert contracts is not None
        assert "BaseModel" in contracts
        assert tests is not None
        assert "test_function" in tests
        assert impl is not None
        assert "main()" in impl


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])