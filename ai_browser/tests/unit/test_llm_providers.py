"""Unit tests for LLM providers"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.cognition.llm import LLMManager
from src.cognition.providers.openai_provider import OpenAIProvider
from src.cognition.providers.anthropic_provider import AnthropicProvider
from src.cognition.providers.gemini_provider import GeminiProvider


class TestLLMManager:
    """Test cases for LLMManager"""
    
    def test_manager_initialization(self):
        """Test LLM manager initializes correctly"""
        manager = LLMManager()
        assert manager is not None
        assert hasattr(manager, 'providers')
    
    def test_provider_registration(self):
        """Test provider registration"""
        manager = LLMManager()
        
        # Should have default providers
        assert 'openai' in manager.providers
        assert 'anthropic' in manager.providers
        assert 'gemini' in manager.providers
    
    @pytest.mark.asyncio
    async def test_generate_with_default_provider(self):
        """Test text generation with default provider"""
        manager = LLMManager()
        
        with patch.object(manager, '_get_default_provider') as mock_provider:
            mock_provider.generate = AsyncMock(return_value="Test response")
            
            response = await manager.generate("Test prompt")
            assert response == "Test response"
    
    @pytest.mark.asyncio
    async def test_generate_structured(self):
        """Test structured output generation"""
        manager = LLMManager()
        
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            action: str
            target: str
        
        with patch.object(manager, '_get_default_provider') as mock_provider:
            mock_provider.generate_structured = AsyncMock(
                return_value=TestModel(action="click", target="button")
            )
            
            result = await manager.generate_structured("Test prompt", TestModel)
            assert isinstance(result, TestModel)
            assert result.action == "click"
    
    def test_provider_switching(self):
        """Test switching between providers"""
        manager = LLMManager()
        
        # Switch to OpenAI
        manager.set_provider('openai')
        assert manager.current_provider == 'openai'
        
        # Switch to Anthropic
        manager.set_provider('anthropic')
        assert manager.current_provider == 'anthropic'
    
    @pytest.mark.asyncio
    async def test_fallback_on_failure(self):
        """Test fallback to secondary provider on failure"""
        manager = LLMManager()
        
        with patch.object(manager, '_get_provider') as mock_get_provider:
            # First provider fails
            failed_provider = AsyncMock()
            failed_provider.generate = AsyncMock(side_effect=Exception("API Error"))
            
            # Second provider succeeds
            success_provider = AsyncMock()
            success_provider.generate = AsyncMock(return_value="Fallback response")
            
            mock_get_provider.side_effect = [failed_provider, success_provider]
            
            response = await manager.generate_with_fallback("Test prompt")
            assert response == "Fallback response"


class TestOpenAIProvider:
    """Test cases for OpenAI provider"""
    
    def test_provider_initialization(self):
        """Test OpenAI provider initializes correctly"""
        with patch('openai.OpenAI'):
            provider = OpenAIProvider(api_key="test-key")
            assert provider is not None
    
    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test text generation with OpenAI"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "Generated text"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            provider = OpenAIProvider(api_key="test-key")
            result = await provider.generate("Test prompt")
            
            assert result == "Generated text"
            mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self):
        """Test generation with system prompt"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "System response"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            provider = OpenAIProvider(api_key="test-key")
            result = await provider.generate(
                "User prompt", 
                system_prompt="You are a helpful assistant"
            )
            
            # Check that system message was included
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args[1]['messages']
            assert any(msg['role'] == 'system' for msg in messages)
    
    def test_token_counting(self):
        """Test token counting functionality"""
        with patch('openai.OpenAI'):
            provider = OpenAIProvider(api_key="test-key")
            
            # Mock token counting
            with patch.object(provider, '_count_tokens', return_value=10):
                token_count = provider.count_tokens("Test message")
                assert token_count == 10


class TestAnthropicProvider:
    """Test cases for Anthropic provider"""
    
    def test_provider_initialization(self):
        """Test Anthropic provider initializes correctly"""
        with patch('anthropic.Anthropic'):
            provider = AnthropicProvider(api_key="test-key")
            assert provider is not None
    
    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test text generation with Anthropic"""
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content[0].text = "Generated text"
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            provider = AnthropicProvider(api_key="test-key")
            result = await provider.generate("Test prompt")
            
            assert result == "Generated text"
            mock_client.messages.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_streaming_response(self):
        """Test streaming response handling"""
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            
            # Mock streaming response
            async def mock_stream():
                yield MagicMock(delta=MagicMock(text="chunk1"))
                yield MagicMock(delta=MagicMock(text="chunk2"))
            
            mock_client.messages.stream.return_value.__aenter__.return_value = mock_stream()
            mock_anthropic.return_value = mock_client
            
            provider = AnthropicProvider(api_key="test-key")
            chunks = []
            
            async for chunk in provider.generate_stream("Test prompt"):
                chunks.append(chunk)
            
            assert len(chunks) == 2


class TestGeminiProvider:
    """Test cases for Gemini provider"""
    
    def test_provider_initialization(self):
        """Test Gemini provider initializes correctly"""
        with patch('google.generativeai.configure'):
            provider = GeminiProvider(api_key="test-key")
            assert provider is not None
    
    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test text generation with Gemini"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Generated text"
            mock_instance.generate_content.return_value = mock_response
            mock_model.return_value = mock_instance
            
            provider = GeminiProvider(api_key="test-key")
            result = await provider.generate("Test prompt")
            
            assert result == "Generated text"
            mock_instance.generate_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multimodal_input(self):
        """Test multimodal input handling"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Image description"
            mock_instance.generate_content.return_value = mock_response
            mock_model.return_value = mock_instance
            
            provider = GeminiProvider(api_key="test-key")
            
            # Mock image data
            image_data = b"fake_image_data"
            result = await provider.generate_multimodal("Describe this image", image_data)
            
            assert result == "Image description"


@pytest.mark.integration
class TestLLMIntegration:
    """Integration tests for LLM providers"""
    
    @pytest.mark.asyncio
    async def test_provider_health_check(self):
        """Test all providers can connect (requires API keys)"""
        manager = LLMManager()
        
        # Skip if no API keys available
        if not any(provider.has_valid_key() for provider in manager.providers.values()):
            pytest.skip("No API keys available for integration testing")
        
        for name, provider in manager.providers.items():
            if provider.has_valid_key():
                try:
                    response = await provider.health_check()
                    assert response is not None
                except Exception as e:
                    pytest.fail(f"Provider {name} health check failed: {e}")
    
    @pytest.mark.asyncio
    async def test_cross_provider_consistency(self):
        """Test that all providers give reasonable responses to same prompt"""
        manager = LLMManager()
        test_prompt = "What is 2 + 2? Answer with just the number."
        
        responses = {}
        for name, provider in manager.providers.items():
            if provider.has_valid_key():
                try:
                    response = await provider.generate(test_prompt)
                    responses[name] = response
                except Exception:
                    continue  # Skip providers that fail
        
        # Check that we got at least one response
        assert len(responses) > 0
        
        # Check that responses contain "4"
        for name, response in responses.items():
            assert "4" in response, f"Provider {name} gave unexpected response: {response}"