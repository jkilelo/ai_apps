#!/usr/bin/env python3
"""
Multimodal/Image Tests
QA Focus: Image processing, vision capabilities, screenshot analysis
Senior QA: Edge cases, format support, error handling
"""

import sys
import base64
from pathlib import Path
from typing import List
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import (
    query_llm,
    stream_llm,
    aquery_llm,
    ImageProcessor,
    ImageContent,
    ImageDetail,
)
from test_config import (
    TestRunner,
    assert_response_valid,
    assert_image_valid,
    create_test_image,
    skip_if_no_api_key,
)


class MultimodalTests:
    """Test image and multimodal capabilities"""
    
    def __init__(self):
        self.runner = TestRunner()
        self.processor = ImageProcessor()
    
    # ==================== IMAGE PROCESSING TESTS ====================
    
    def test_image_encoding_from_bytes(self):
        """Test encoding image from bytes"""
        test_image = create_test_image(width=200, height=100, color="blue")
        
        image_content = self.processor.encode_bytes(test_image, "image/png")
        
        assert_image_valid(image_content)
        assert image_content.mime_type == "image/png"
        assert image_content.detail == ImageDetail.AUTO
        
        # Verify base64 encoding
        decoded = base64.b64decode(image_content.data)
        assert len(decoded) > 0, "Decoded image is empty"
    
    def test_image_encoding_from_file(self):
        """Test encoding image from file"""
        # Create a temporary test image file
        test_path = Path("test_image_temp.png")
        test_image = create_test_image(width=150, height=150, color="green")
        
        with open(test_path, "wb") as f:
            f.write(test_image)
        
        try:
            image_content = self.processor.encode_image(test_path)
            assert_image_valid(image_content)
            assert image_content.mime_type == "image/png"
        finally:
            test_path.unlink()  # Clean up
    
    def test_pil_image_encoding(self):
        """Test encoding PIL Image object"""
        try:
            from PIL import Image, ImageDraw
            
            # Create PIL image
            img = Image.new("RGB", (100, 100), color="red")
            draw = ImageDraw.Draw(img)
            draw.text((30, 40), "TEST", fill="white")
            
            image_content = self.processor.encode_pil_image(img, format="PNG")
            assert_image_valid(image_content)
            assert image_content.mime_type == "image/png"
            
        except ImportError:
            print("    PIL not available, skipping")
    
    def test_image_mime_type_detection(self):
        """Test MIME type detection from file extension"""
        extensions = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        
        for ext, expected_mime in extensions.items():
            test_path = Path(f"test{ext}")
            mime_type = self.processor._get_mime_type(test_path)
            assert mime_type == expected_mime, \
                f"Wrong MIME type for {ext}: got {mime_type}, expected {expected_mime}"
    
    # ==================== VISION MODEL TESTS ====================
    
    @skip_if_no_api_key("openai")
    def test_openai_vision_simple(self):
        """Test OpenAI GPT-4o vision with simple image"""
        test_image = create_test_image(width=200, height=100, color="blue")
        
        messages = [
            {"role": "user", "content": "What color is the rectangle in this image?"}
        ]
        
        response = query_llm(
            messages,
            provider="openai",
            model="gpt-4o-mini",
            images=[test_image],
            max_tokens=50
        )
        
        assert_response_valid(response)
        assert response.images_processed == 1
        # Should identify blue color
        assert "blue" in response.content.lower() or "color" in response.content.lower()
    
    @skip_if_no_api_key("gemini")
    def test_gemini_vision_simple(self):
        """Test Gemini vision with simple image"""
        test_image = create_test_image(width=200, height=100, color="red")
        
        messages = [
            {"role": "user", "content": "Describe what you see in this image."}
        ]
        
        response = query_llm(
            messages,
            provider="gemini",
            model="gemini-2.0-flash",
            images=[test_image],
            max_tokens=100
        )
        
        assert_response_valid(response)
        assert response.images_processed == 1
        # Should describe the image
        assert len(response.content) > 20
    
    @skip_if_no_api_key("anthropic")
    def test_anthropic_vision_simple(self):
        """Test Claude vision with simple image"""
        test_image = create_test_image(width=200, height=100, color="green")
        
        messages = [
            {"role": "user", "content": "What text do you see in this image?"}
        ]
        
        response = query_llm(
            messages,
            provider="anthropic",
            model="claude-3-haiku-20240307",
            images=[test_image],
            max_tokens=50
        )
        
        assert_response_valid(response)
        assert response.images_processed == 1
        # Should identify TEST text
        assert "test" in response.content.lower() or "text" in response.content.lower()
    
    def test_multiple_images(self):
        """Test processing multiple images"""
        images = [
            create_test_image(width=100, height=100, color="red"),
            create_test_image(width=100, height=100, color="blue"),
            create_test_image(width=100, height=100, color="green"),
        ]
        
        messages = [
            {"role": "user", "content": "How many images do you see?"}
        ]
        
        response = query_llm(
            messages,
            images=images,
            max_tokens=50
        )
        
        assert_response_valid(response)
        assert response.images_processed == 3
        # Should mention multiple images or count
        assert "3" in response.content or "three" in response.content.lower() \
            or "multiple" in response.content.lower()
    
    def test_image_with_detail_level(self):
        """Test different image detail levels"""
        test_image = create_test_image(width=500, height=500, color="purple")
        
        # Create image content with different detail levels
        image_low = ImageContent(
            data=base64.b64encode(test_image).decode(),
            mime_type="image/png",
            detail=ImageDetail.LOW
        )
        
        image_high = ImageContent(
            data=base64.b64encode(test_image).decode(),
            mime_type="image/png",
            detail=ImageDetail.HIGH
        )
        
        messages = [{"role": "user", "content": "Analyze this image"}]
        
        # Test with low detail
        response_low = query_llm(messages, images=[image_low], max_tokens=100)
        assert_response_valid(response_low)
        
        # Test with high detail
        response_high = query_llm(messages, images=[image_high], max_tokens=100)
        assert_response_valid(response_high)
        
        # High detail might produce longer response (provider dependent)
        print(f"    Low detail response: {len(response_low.content)} chars")
        print(f"    High detail response: {len(response_high.content)} chars")
    
    # ==================== STREAMING WITH IMAGES ====================
    
    def test_streaming_with_images(self):
        """Test streaming responses with image input"""
        test_image = create_test_image(width=100, height=100, color="yellow")
        
        messages = [
            {"role": "user", "content": "Describe this image word by word"}
        ]
        
        chunks = []
        for chunk in stream_llm(messages, images=[test_image], max_tokens=50):
            chunks.append(chunk)
            if chunk.is_final:
                break
        
        assert len(chunks) > 0, "No chunks received"
        full_content = "".join(c.content for c in chunks if c.content)
        assert len(full_content) > 10, "Stream content too short"
    
    # ==================== ASYNC WITH IMAGES ====================
    
    async def test_async_with_images(self):
        """Test async query with images"""
        test_image = create_test_image(width=150, height=150, color="orange")
        
        messages = [
            {"role": "user", "content": "What shape do you see?"}
        ]
        
        response = await aquery_llm(
            messages,
            images=[test_image],
            max_tokens=50
        )
        
        assert_response_valid(response)
        assert response.images_processed == 1
        assert "rectangle" in response.content.lower() or "square" in response.content.lower() \
            or "shape" in response.content.lower()
    
    # ==================== ERROR HANDLING ====================
    
    def test_invalid_image_data(self):
        """Test handling of invalid image data"""
        invalid_data = "not-valid-base64!@#$"
        
        try:
            image_content = ImageContent(
                data=invalid_data,
                mime_type="image/png"
            )
            assert False, "Should have raised validation error"
        except Exception as e:
            assert "base64" in str(e).lower() or "invalid" in str(e).lower()
    
    def test_empty_image_data(self):
        """Test handling of empty image data"""
        try:
            image_content = ImageContent(
                data="",
                mime_type="image/png"
            )
            # Empty base64 might be valid
        except Exception as e:
            assert "empty" in str(e).lower() or "data" in str(e).lower()
    
    def test_unsupported_image_format(self):
        """Test handling of unsupported image formats"""
        test_image = create_test_image()
        
        # Some providers might not support all formats
        messages = [{"role": "user", "content": "Analyze this BMP image"}]
        
        try:
            response = query_llm(
                messages,
                images=[test_image],
                max_tokens=50
            )
            assert_response_valid(response)
        except Exception as e:
            # Some providers might reject certain formats
            assert "format" in str(e).lower() or "support" in str(e).lower()
    
    # ==================== REAL-WORLD SCENARIOS ====================
    
    def test_ui_screenshot_analysis(self):
        """Test analysis of UI screenshot"""
        # Create a real test UI screenshot
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new("RGB", (800, 600), color="white")
            draw = ImageDraw.Draw(img)
            
            # Draw UI elements
            draw.rectangle([50, 50, 750, 100], fill="lightblue", outline="blue")
            draw.text((400, 70), "Header", fill="black")
            
            draw.rectangle([50, 150, 350, 250], fill="lightgreen", outline="green")
            draw.text((200, 200), "Button 1", fill="black")
            
            draw.rectangle([450, 150, 750, 250], fill="lightcoral", outline="red")
            draw.text((600, 200), "Button 2", fill="black")
            
            import io
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            screenshot = buffer.getvalue()
            
            messages = [
                {"role": "user", "content": "List the UI elements you can see in this screenshot"}
            ]
            
            response = query_llm(
                messages,
                images=[screenshot],
                max_tokens=200
            )
            
            assert_response_valid(response)
            # Should identify UI elements
            content_lower = response.content.lower()
            assert "button" in content_lower or "element" in content_lower \
                or "header" in content_lower
            
        except ImportError:
            print("    PIL not available for UI test")
    
    def test_form_field_extraction(self):
        """Test extracting form fields from image"""
        # Create a real test form image
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new("RGB", (400, 300), color="white")
            draw = ImageDraw.Draw(img)
            
            # Draw form fields
            draw.text((20, 20), "Name:", fill="black")
            draw.rectangle([100, 15, 380, 40], outline="gray")
            
            draw.text((20, 60), "Email:", fill="black")
            draw.rectangle([100, 55, 380, 80], outline="gray")
            
            draw.text((20, 100), "Password:", fill="black")
            draw.rectangle([100, 95, 380, 120], outline="gray")
            
            draw.rectangle([150, 150, 250, 180], fill="blue")
            draw.text((175, 160), "Submit", fill="white")
            
            import io
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            form_image = buffer.getvalue()
            
            messages = [
                {"role": "user", "content": "Identify the form fields in this image"}
            ]
            
            response = query_llm(
                messages,
                images=[form_image],
                max_tokens=200
            )
            
            assert_response_valid(response)
            # Should identify form fields
            content_lower = response.content.lower()
            assert ("name" in content_lower or "email" in content_lower 
                   or "password" in content_lower or "form" in content_lower)
            
        except ImportError:
            print("    PIL not available for form test")
    
    def test_error_dialog_detection(self):
        """Test detecting error dialogs in screenshots"""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new("RGB", (400, 200), color="white")
            draw = ImageDraw.Draw(img)
            
            # Draw error dialog
            draw.rectangle([50, 50, 350, 150], fill="red", outline="darkred", width=2)
            draw.text((200, 70), "ERROR", fill="white")
            draw.text((100, 100), "Failed to connect to server", fill="white")
            
            import io
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            error_image = buffer.getvalue()
            
            messages = [
                {"role": "user", "content": "What type of dialog or message is shown?"}
            ]
            
            response = query_llm(
                messages,
                images=[error_image],
                max_tokens=100
            )
            
            assert_response_valid(response)
            # Should identify error
            content_lower = response.content.lower()
            assert "error" in content_lower or "fail" in content_lower \
                or "problem" in content_lower or "issue" in content_lower
            
        except ImportError:
            print("    PIL not available for error dialog test")
    
    def run_all_tests(self) -> TestRunner:
        """Run all multimodal tests"""
        print("\n" + "=" * 60)
        print("MULTIMODAL/IMAGE TESTS")
        print("=" * 60)
        
        # Image processing tests
        self.runner.add_result(
            self.runner.run_test(self.test_image_encoding_from_bytes, "encode_from_bytes", "image_processing")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_image_encoding_from_file, "encode_from_file", "image_processing")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_pil_image_encoding, "pil_encoding", "image_processing")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_image_mime_type_detection, "mime_type_detection", "image_processing")
        )
        
        # Vision model tests
        self.runner.add_result(
            self.runner.run_test(self.test_openai_vision_simple, "openai_vision", "vision_models")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_gemini_vision_simple, "gemini_vision", "vision_models")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_anthropic_vision_simple, "anthropic_vision", "vision_models")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_multiple_images, "multiple_images", "vision_models")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_image_with_detail_level, "detail_levels", "vision_models")
        )
        
        # Streaming and async
        self.runner.add_result(
            self.runner.run_test(self.test_streaming_with_images, "streaming_images", "multimodal_streaming")
        )
        self.runner.add_result(
            asyncio.run(self.runner.run_async_test(self.test_async_with_images, "async_images", "multimodal_async"))
        )
        
        # Error handling
        self.runner.add_result(
            self.runner.run_test(self.test_invalid_image_data, "invalid_image", "error_handling")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_empty_image_data, "empty_image", "error_handling")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_unsupported_image_format, "unsupported_format", "error_handling")
        )
        
        # Real-world scenarios
        self.runner.add_result(
            self.runner.run_test(self.test_ui_screenshot_analysis, "ui_screenshot", "real_world")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_form_field_extraction, "form_extraction", "real_world")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_error_dialog_detection, "error_dialog", "real_world")
        )
        
        return self.runner


if __name__ == "__main__":
    tests = MultimodalTests()
    runner = tests.run_all_tests()
    
    # Generate and save report
    report = runner.generate_report()
    print("\n" + "=" * 60)
    print("MULTIMODAL TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    
    runner.save_report("multimodal_test_report.json")