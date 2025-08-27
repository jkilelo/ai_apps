#!/usr/bin/env python3
"""
Test script for enhanced LLM V2 module with streaming and image support
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "base"))

# Import the enhanced module
from base.llm_v2_enhanced import (
    EnhancedLLMGateway,
    LLMConfig,
    ImageContent,
    StreamChunk,
    ImageProcessor,
    query_with_images,
    stream_response,
    aquery_with_images,
    astream_response
)

from pydantic import BaseModel, Field

# Test data models
class UIElement(BaseModel):
    """Model for testing structured output"""
    selector: str = Field(..., description="CSS selector or XPath")
    element_type: str = Field(..., description="Type of element (button, input, etc)")
    text: str = Field("", description="Visible text content")
    confidence: float = Field(0.0, ge=0, le=1, description="Confidence score")

class TestResult(BaseModel):
    """Test result tracking"""
    test_name: str
    passed: bool
    details: str = ""

async def test_basic_query():
    """Test basic query functionality"""
    print("\n[TEST 1] Basic Query (Text)")
    print("-" * 60)
    
    gateway = EnhancedLLMGateway()
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello World' and nothing else."}
    ]
    
    try:
        # Test with each provider if available
        providers = ["gemini", "openai", "anthropic"]
        
        for provider in providers:
            try:
                response = gateway.query(messages, provider=provider)
                print(f"[OK] {provider}: {response.content[:50]}...")
                return TestResult(test_name="Basic Query", passed=True, details=f"Tested with {provider}")
            except Exception as e:
                print(f"[SKIP] {provider}: {str(e)[:50]}")
                continue
        
        return TestResult(test_name="Basic Query", passed=False, details="No providers available")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return TestResult(test_name="Basic Query", passed=False, details=str(e))

async def test_structured_output():
    """Test structured output with Pydantic models"""
    print("\n[TEST 2] Structured Output")
    print("-" * 60)
    
    gateway = EnhancedLLMGateway()
    
    messages = [
        {"role": "system", "content": "You identify UI elements."},
        {"role": "user", "content": "Create a sample button element with selector '#submit-btn', type 'button', text 'Submit', and confidence 0.95"}
    ]
    
    try:
        element = gateway.query(messages, output_model=UIElement, provider="gemini")
        print(f"[OK] Structured output received:")
        print(f"     Selector: {element.selector}")
        print(f"     Type: {element.element_type}")
        print(f"     Text: {element.text}")
        print(f"     Confidence: {element.confidence}")
        
        return TestResult(test_name="Structured Output", passed=True, details="Successfully parsed to Pydantic model")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return TestResult(test_name="Structured Output", passed=False, details=str(e))

async def test_streaming():
    """Test streaming responses"""
    print("\n[TEST 3] Streaming Response")
    print("-" * 60)
    
    messages = [
        {"role": "user", "content": "Count from 1 to 5 slowly, one number at a time."}
    ]
    
    try:
        print("Streaming: ", end="", flush=True)
        chunk_count = 0
        
        for chunk in stream_response(messages, provider="gemini"):
            if chunk.content:
                print(chunk.content, end="", flush=True)
                chunk_count += 1
            if chunk.is_final:
                break
        
        print(f"\n[OK] Received {chunk_count} chunks")
        return TestResult(test_name="Streaming", passed=True, details=f"Streamed {chunk_count} chunks")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return TestResult(test_name="Streaming", passed=False, details=str(e))

async def test_async_operations():
    """Test async query and streaming"""
    print("\n[TEST 4] Async Operations")
    print("-" * 60)
    
    messages = [
        {"role": "user", "content": "Say 'Async works!' and nothing else."}
    ]
    
    try:
        # Test async query
        response = await aquery_with_images(messages, provider="gemini")
        print(f"[OK] Async query: {response.content[:50]}...")
        
        # Test async streaming
        print("Async streaming: ", end="", flush=True)
        chunk_count = 0
        
        async for chunk in astream_response(messages, provider="gemini"):
            if chunk.content:
                print(".", end="", flush=True)
                chunk_count += 1
            if chunk.is_final:
                break
        
        print(f"\n[OK] Async streamed {chunk_count} chunks")
        return TestResult(test_name="Async Operations", passed=True, details="Both async query and streaming work")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return TestResult(test_name="Async Operations", passed=False, details=str(e))

async def test_image_processing():
    """Test image processing utilities"""
    print("\n[TEST 5] Image Processing")
    print("-" * 60)
    
    processor = ImageProcessor()
    
    try:
        # Test base64 encoding of bytes
        test_image_data = b"fake_image_data_for_testing"
        image_content = processor.encode_bytes(test_image_data, "image/png")
        
        print(f"[OK] Encoded {len(test_image_data)} bytes to base64")
        print(f"     MIME type: {image_content.mime_type}")
        print(f"     Data length: {len(image_content.data)} chars")
        
        # Test with actual image if PIL is available
        try:
            from PIL import Image
            import io
            
            # Create a small test image
            img = Image.new('RGB', (100, 100), color='red')
            image_content = processor.encode_pil_image(img, format="PNG")
            
            print(f"[OK] Encoded PIL Image to base64")
            print(f"     MIME type: {image_content.mime_type}")
            
            return TestResult(test_name="Image Processing", passed=True, details="Image encoding works")
            
        except ImportError:
            print("[INFO] PIL not available, skipping PIL image test")
            return TestResult(test_name="Image Processing", passed=True, details="Basic encoding works (PIL not tested)")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return TestResult(test_name="Image Processing", passed=False, details=str(e))

async def test_image_with_query():
    """Test sending images with queries"""
    print("\n[TEST 6] Query with Images")
    print("-" * 60)
    
    try:
        # Create a simple test image using PIL if available
        try:
            from PIL import Image, ImageDraw
            import io
            
            # Create a test image with text
            img = Image.new('RGB', (200, 100), color='white')
            draw = ImageDraw.Draw(img)
            draw.rectangle([50, 30, 150, 70], fill='blue')
            draw.text((75, 45), "BUTTON", fill='white')
            
            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()
            
            messages = [
                {"role": "system", "content": "You analyze UI screenshots."},
                {"role": "user", "content": "What UI element do you see in this image? Respond with just the element type."}
            ]
            
            # Test with image
            response = query_with_images(
                messages,
                images=[img_bytes],
                provider="gemini"  # Gemini has good vision support
            )
            
            print(f"[OK] Sent image with query")
            print(f"     Response: {response.content[:100]}...")
            print(f"     Images processed: {response.images_processed}")
            
            return TestResult(test_name="Query with Images", passed=True, details="Successfully sent and processed image")
            
        except ImportError:
            print("[SKIP] PIL not available, cannot create test image")
            return TestResult(test_name="Query with Images", passed=False, details="PIL not available")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return TestResult(test_name="Query with Images", passed=False, details=str(e))

async def test_multimodal_structured():
    """Test structured output with image input"""
    print("\n[TEST 7] Multimodal Structured Output")
    print("-" * 60)
    
    try:
        # This test requires PIL
        from PIL import Image, ImageDraw
        import io
        
        # Create a test UI image
        img = Image.new('RGB', (300, 200), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Draw a button
        draw.rectangle([100, 80, 200, 120], fill='#007bff', outline='#0056b3')
        draw.text((125, 95), "Submit", fill='white')
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        messages = [
            {"role": "system", "content": "You analyze UI elements in screenshots and return structured data."},
            {"role": "user", "content": "Analyze the button in this image. Use selector '#submit-btn'."}
        ]
        
        # Query with image and structured output
        element = query_with_images(
            messages,
            images=[img_bytes],
            output_model=UIElement,
            provider="gemini"
        )
        
        print(f"[OK] Multimodal structured output:")
        print(f"     Selector: {element.selector}")
        print(f"     Type: {element.element_type}")
        print(f"     Text: {element.text}")
        print(f"     Confidence: {element.confidence}")
        
        return TestResult(test_name="Multimodal Structured", passed=True, details="Image analysis with structured output works")
        
    except ImportError:
        print("[SKIP] PIL not available")
        return TestResult(test_name="Multimodal Structured", passed=False, details="PIL not available")
    except Exception as e:
        print(f"[ERROR] {e}")
        return TestResult(test_name="Multimodal Structured", passed=False, details=str(e))

async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("TESTING ENHANCED LLM V2 MODULE")
    print("=" * 60)
    
    # Check environment
    print("\n[ENVIRONMENT CHECK]")
    print(f"Python: {sys.version}")
    print(f"Working dir: {os.getcwd()}")
    
    # Check API keys
    api_keys = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY",
        "Google": "GOOGLE_API_KEY"
    }
    
    for provider, key_name in api_keys.items():
        key_value = os.getenv(key_name)
        if key_value:
            print(f"[OK] {provider} API key found ({len(key_value)} chars)")
        else:
            print(f"[MISSING] {provider} API key not found")
    
    # Run tests
    test_results = []
    
    # Run sync tests
    test_results.append(await test_basic_query())
    test_results.append(await test_structured_output())
    test_results.append(await test_streaming())
    
    # Run async tests
    test_results.append(await test_async_operations())
    
    # Run image tests
    test_results.append(await test_image_processing())
    test_results.append(await test_image_with_query())
    test_results.append(await test_multimodal_structured())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in test_results if r.passed)
    total = len(test_results)
    
    for result in test_results:
        status = "[PASS]" if result.passed else "[FAIL]"
        print(f"{status} {result.test_name}: {result.details}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Enhanced LLM module is working correctly.")
    else:
        print(f"\n[WARNING] {total - passed} tests failed. Check the details above.")

if __name__ == "__main__":
    # Run all tests
    asyncio.run(run_all_tests())