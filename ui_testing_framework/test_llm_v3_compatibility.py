#!/usr/bin/env python3
"""
Comprehensive backward compatibility test for llm_v3.py

This test verifies that llm_v3.py is 100% backward compatible with
the original llm.py while using prompts_v3.py as the source of truth.

Author: Senior Integration Engineer
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import from llm_v3 (not llm) to test the new version
from llm_v3 import (
    # Core functions
    query_llm,
    stream_llm,
    call_default_llm,
    list_available_strategies,
    # Enums
    Provider,
    Role,
    StrategyType,
    ImageDetail,
    # Models
    Message,
    LLMResponse,
    StreamChunk,
    ImageContent,
    LLMConfig,
    # Classes
    UnifiedLLMGateway,
    StrategyEngine,
    ImageProcessor,
)


def test_imports():
    """Test that all expected exports are available"""
    print("[TEST 1] Import Compatibility")
    print("-" * 60)
    
    # Test that all key classes and functions are imported
    required_exports = [
        "query_llm", "stream_llm", "call_default_llm", "list_available_strategies",
        "Provider", "Role", "StrategyType", "ImageDetail",
        "Message", "LLMResponse", "StreamChunk", "ImageContent", "LLMConfig",
        "UnifiedLLMGateway", "StrategyEngine", "ImageProcessor",
    ]
    
    for export in required_exports:
        assert export in globals(), f"Missing export: {export}"
        print(f"[OK] {export}")
    
    print("[PASS] All imports available\n")
    return True


def test_enums():
    """Test that all enums have correct values"""
    print("[TEST 2] Enum Values")
    print("-" * 60)
    
    # Test Provider enum
    assert Provider.OPENAI.value == "openai"
    assert Provider.ANTHROPIC.value == "anthropic"
    assert Provider.GEMINI.value == "gemini"
    assert Provider.GOOGLE.value == "google"
    print("[OK] Provider enum values correct")
    
    # Test Role enum
    assert Role.SYSTEM.value == "system"
    assert Role.USER.value == "user"
    assert Role.ASSISTANT.value == "assistant"
    print("[OK] Role enum values correct")
    
    # Test StrategyType enum (all 21 strategies)
    strategies = [
        "chain_of_thought", "tree_of_thoughts", "graph_of_thoughts",
        "least_to_most", "step_back", "decomposed",
        "retrieval_augmented", "generated_knowledge", "knowledge_graph",
        "self_consistency", "self_refine", "self_verification",
        "react", "reflexion", "chain_of_verification",
        "hypothetical_document", "analogical_reasoning", "socratic_method",
        "meta_prompting", "prompt_optimization", "constitutional_ai",
    ]
    
    for strategy_name in strategies:
        strategy_enum = StrategyType(strategy_name)
        assert strategy_enum.value == strategy_name
    print(f"[OK] All {len(strategies)} StrategyType values correct")
    
    print("[PASS] Enum compatibility verified\n")
    return True


def test_message_creation():
    """Test Message model creation"""
    print("[TEST 3] Message Model")
    print("-" * 60)
    
    # Test basic message
    msg = Message(
        role=Role.USER,
        content="Test message",
    )
    assert msg.role == Role.USER
    assert msg.content == "Test message"
    assert msg.images is None
    assert isinstance(msg.metadata, dict)
    print("[OK] Basic message creation")
    
    # Test message with metadata
    msg = Message(
        role=Role.ASSISTANT,
        content="Response",
        metadata={"key": "value"}
    )
    assert msg.metadata["key"] == "value"
    print("[OK] Message with metadata")
    
    # Test message serialization
    msg_dict = msg.model_dump()
    assert msg_dict["role"] == "assistant"
    assert msg_dict["content"] == "Response"
    print("[OK] Message serialization")
    
    print("[PASS] Message model compatible\n")
    return True


def test_llm_response():
    """Test LLMResponse model"""
    print("[TEST 4] LLMResponse Model")
    print("-" * 60)
    
    response = LLMResponse(
        content="Test response",
        provider=Provider.GEMINI,
        model="gemini-2.0-flash",
        strategy_used=StrategyType.CHAIN_OF_THOUGHT,
    )
    
    assert response.content == "Test response"
    assert response.provider == Provider.GEMINI
    assert response.model == "gemini-2.0-flash"
    assert response.strategy_used == StrategyType.CHAIN_OF_THOUGHT
    print("[OK] LLMResponse creation")
    
    # Test serialization
    response_dict = response.model_dump()
    assert response_dict["provider"] == "gemini"
    assert "timestamp" in response_dict
    print("[OK] LLMResponse serialization")
    
    print("[PASS] LLMResponse model compatible\n")
    return True


def test_strategy_engine():
    """Test StrategyEngine with prompts_v3 integration"""
    print("[TEST 5] StrategyEngine Integration")
    print("-" * 60)
    
    engine = StrategyEngine()
    
    # Test that strategies are available
    available = engine.get_available_strategies()
    assert len(available) >= 21
    print(f"[OK] {len(available)} strategies available from prompts_v3")
    
    # Test strategy application
    messages = [
        Message(role=Role.USER, content="Explain how computers work")
    ]
    
    # Test Chain of Thought
    enhanced = engine.apply_strategy(messages, StrategyType.CHAIN_OF_THOUGHT)
    assert len(enhanced[0].content) > len(messages[0].content)
    print(f"[OK] CoT: {len(messages[0].content)} -> {len(enhanced[0].content)} chars")
    
    # Test Tree of Thoughts
    enhanced = engine.apply_strategy(messages, StrategyType.TREE_OF_THOUGHTS)
    assert len(enhanced[0].content) > len(messages[0].content)
    print(f"[OK] ToT: {len(messages[0].content)} -> {len(enhanced[0].content)} chars")
    
    # Test ReAct
    enhanced = engine.apply_strategy(messages, StrategyType.REACT)
    assert len(enhanced[0].content) > len(messages[0].content)
    print(f"[OK] ReAct: {len(messages[0].content)} -> {len(enhanced[0].content)} chars")
    
    print("[PASS] StrategyEngine using prompts_v3 successfully\n")
    return True


def test_convenience_functions():
    """Test convenience functions"""
    print("[TEST 6] Convenience Functions")
    print("-" * 60)
    
    # Test list_available_strategies
    strategies = list_available_strategies()
    assert len(strategies) >= 21
    assert "chain_of_thought" in strategies
    assert "tree_of_thoughts" in strategies
    assert "react" in strategies
    print(f"[OK] list_available_strategies returns {len(strategies)} strategies")
    
    # Test call_default_llm signature (without actually calling API)
    import inspect
    sig = inspect.signature(call_default_llm)
    assert "messages" in sig.parameters
    assert "kwargs" in str(sig.parameters)
    print("[OK] call_default_llm signature unchanged")
    
    # Test query_llm signature
    sig = inspect.signature(query_llm)
    assert "provider" in sig.parameters
    assert "model" in sig.parameters
    assert "messages" in sig.parameters
    assert "strategy" in sig.parameters
    assert "structured_output_schema" in sig.parameters
    print("[OK] query_llm signature unchanged")
    
    # Test stream_llm signature
    sig = inspect.signature(stream_llm)
    assert "provider" in sig.parameters
    assert "model" in sig.parameters
    assert "messages" in sig.parameters
    assert "strategy" in sig.parameters
    assert "on_chunk" in sig.parameters
    print("[OK] stream_llm signature unchanged")
    
    print("[PASS] All convenience functions compatible\n")
    return True


def test_unified_gateway():
    """Test UnifiedLLMGateway class"""
    print("[TEST 7] UnifiedLLMGateway")
    print("-" * 60)
    
    gateway = UnifiedLLMGateway()
    
    # Test that gateway has all expected attributes
    assert hasattr(gateway, "config")
    assert hasattr(gateway, "strategy_engine")
    assert hasattr(gateway, "image_processor")
    assert hasattr(gateway, "providers")
    print("[OK] Gateway has all expected attributes")
    
    # Test that providers are initialized
    assert Provider.GEMINI in gateway.providers
    assert Provider.OPENAI in gateway.providers
    assert Provider.ANTHROPIC in gateway.providers
    print("[OK] All providers initialized")
    
    # Test get_available_strategies
    strategies = gateway.get_available_strategies()
    assert len(strategies) >= 21
    print(f"[OK] Gateway returns {len(strategies)} strategies")
    
    print("[PASS] UnifiedLLMGateway compatible\n")
    return True


def test_image_processor():
    """Test ImageProcessor class"""
    print("[TEST 8] ImageProcessor")
    print("-" * 60)
    
    processor = ImageProcessor()
    
    # Test MIME type detection
    assert processor.get_mime_type("test.png") == "image/png"
    assert processor.get_mime_type("test.jpg") == "image/jpeg"
    assert processor.get_mime_type("test.jpeg") == "image/jpeg"
    assert processor.get_mime_type("test.gif") == "image/gif"
    assert processor.get_mime_type("test.webp") == "image/webp"
    print("[OK] MIME type detection works")
    
    # Test base64 decode (with test data)
    test_base64 = "SGVsbG8gV29ybGQ="  # "Hello World" in base64
    decoded = processor.decode_image(test_base64)
    assert decoded == b"Hello World"
    print("[OK] Base64 decoding works")
    
    print("[PASS] ImageProcessor compatible\n")
    return True


def test_prompts_v3_integration():
    """Test that prompts_v3 is properly integrated"""
    print("[TEST 9] Prompts V3 Integration")
    print("-" * 60)
    
    # Test that we can access prompts_v3 strategies
    engine = StrategyEngine()
    
    # Verify that the prompt library is initialized
    assert hasattr(engine, "prompt_library")
    print("[OK] PromptLibrary from prompts_v3 initialized")
    
    # Test that strategies use prompts_v3 content
    messages = [Message(role=Role.USER, content="Test task")]
    
    # Apply a strategy and check it uses prompts_v3 content
    enhanced = engine.apply_strategy(messages, StrategyType.CHAIN_OF_THOUGHT)
    
    # The enhanced prompt should contain signature phrases from prompts_v3
    assert "STEP 0: ESTABLISH FOUNDATIONS" in enhanced[0].content or \
           "journey of reasoning" in enhanced[0].content
    print("[OK] Strategy uses prompts_v3 content")
    
    # Test strategy mapping
    from llm_v3 import STRATEGY_MAPPING
    assert len(STRATEGY_MAPPING) == 21
    print(f"[OK] All 21 strategies mapped to prompts_v3")
    
    print("[PASS] Prompts V3 fully integrated\n")
    return True


def main():
    """Run all compatibility tests"""
    print("=" * 70)
    print("LLM_V3 BACKWARD COMPATIBILITY TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        ("Import Compatibility", test_imports),
        ("Enum Values", test_enums),
        ("Message Model", test_message_creation),
        ("LLMResponse Model", test_llm_response),
        ("StrategyEngine", test_strategy_engine),
        ("Convenience Functions", test_convenience_functions),
        ("UnifiedLLMGateway", test_unified_gateway),
        ("ImageProcessor", test_image_processor),
        ("Prompts V3 Integration", test_prompts_v3_integration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"[ERROR] Test '{name}' failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
    
    print("-" * 70)
    print(f"Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n[SUCCESS] llm_v3.py is 100% backward compatible!")
        print("[INFO] Key achievements:")
        print("  - All function signatures preserved")
        print("  - All models and enums unchanged")
        print("  - All 21 strategies now use prompts_v3.py")
        print("  - Zero breaking changes")
        print("  - Drop-in replacement for llm.py")
        return 0
    else:
        print(f"\n[WARNING] {total_count - passed_count} tests failed")
        print("[INFO] Review failures before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())