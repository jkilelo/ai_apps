"""
Test Configuration and Utilities
QA Best Practices: Centralized configuration, reusable utilities
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Test configuration
TEST_CONFIG = {
    "timeout": 30,
    "retry_count": 3,
    "performance_threshold_ms": 5000,
    "providers_to_test": ["gemini", "openai", "anthropic"],
    "skip_expensive_tests": os.getenv("SKIP_EXPENSIVE_TESTS", "false").lower() == "true",
    "verbose": os.getenv("TEST_VERBOSE", "false").lower() == "true",
}

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Test results directory
TEST_RESULTS_DIR = Path(__file__).parent / "test_results"
TEST_RESULTS_DIR.mkdir(exist_ok=True)

# Sample test images
TEST_IMAGES = {
    "ui_screenshot": TEST_DATA_DIR / "ui_screenshot.png",
    "button_element": TEST_DATA_DIR / "button.png",
    "form_complex": TEST_DATA_DIR / "complex_form.png",
    "error_dialog": TEST_DATA_DIR / "error_dialog.png",
}


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    test_category: str
    status: TestStatus
    execution_time_ms: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "test_category": self.test_category,
            "status": self.status.value,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "metadata": self.metadata or {},
            "timestamp": datetime.now().isoformat()
        }


class TestRunner:
    """Test execution and reporting"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
    
    def run_test(self, test_func: Callable, test_name: str, category: str) -> TestResult:
        """Execute a single test with timing and error handling"""
        print(f"[TEST] {category}/{test_name}", end=" ... ", flush=True)
        
        start = time.perf_counter()
        try:
            test_func()
            elapsed = (time.perf_counter() - start) * 1000
            print(f"[PASS] {elapsed:.2f}ms")
            return TestResult(test_name, category, TestStatus.PASSED, elapsed)
        except AssertionError as e:
            elapsed = (time.perf_counter() - start) * 1000
            print(f"[FAIL] {str(e)[:50]}")
            return TestResult(test_name, category, TestStatus.FAILED, elapsed, str(e))
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            print(f"[ERROR] {str(e)[:50]}")
            return TestResult(test_name, category, TestStatus.ERROR, elapsed, str(e))
    
    async def run_async_test(self, test_func: Callable, test_name: str, category: str) -> TestResult:
        """Execute an async test"""
        print(f"[ASYNC TEST] {category}/{test_name}", end=" ... ", flush=True)
        
        start = time.perf_counter()
        try:
            await test_func()
            elapsed = (time.perf_counter() - start) * 1000
            print(f"[PASS] {elapsed:.2f}ms")
            return TestResult(test_name, category, TestStatus.PASSED, elapsed)
        except AssertionError as e:
            elapsed = (time.perf_counter() - start) * 1000
            print(f"[FAIL] {str(e)[:50]}")
            return TestResult(test_name, category, TestStatus.FAILED, elapsed, str(e))
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            print(f"[ERROR] {str(e)[:50]}")
            return TestResult(test_name, category, TestStatus.ERROR, elapsed, str(e))
    
    def add_result(self, result: TestResult):
        """Add test result"""
        self.results.append(result)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        
        avg_time = sum(r.execution_time_ms for r in self.results) / total if total > 0 else 0
        
        return {
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "pass_rate": (passed / total * 100) if total > 0 else 0,
                "average_time_ms": avg_time,
                "total_time_ms": sum(r.execution_time_ms for r in self.results),
            },
            "results": [r.to_dict() for r in self.results],
            "timestamp": datetime.now().isoformat(),
        }
    
    def save_report(self, filename: Optional[str] = None):
        """Save test report to file"""
        if not filename:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_path = TEST_RESULTS_DIR / filename
        with open(report_path, "w") as f:
            json.dump(self.generate_report(), f, indent=2)
        
        print(f"\n[REPORT] Saved to {report_path}")
        return report_path


def assert_response_valid(response: Any, min_length: int = 1):
    """Validate LLM response"""
    assert response is not None, "Response is None"
    assert hasattr(response, "content"), "Response missing content attribute"
    assert len(response.content) >= min_length, f"Response too short: {len(response.content)} chars"
    assert hasattr(response, "provider"), "Response missing provider"
    assert hasattr(response, "model"), "Response missing model"


def assert_streaming_valid(chunks: List[Any]):
    """Validate streaming chunks"""
    assert len(chunks) > 0, "No chunks received"
    assert all(hasattr(c, "content") for c in chunks), "Invalid chunk structure"
    assert any(c.is_final for c in chunks), "No final chunk received"
    
    # Verify chunk ordering
    indices = [c.index for c in chunks if hasattr(c, "index")]
    assert indices == sorted(indices), "Chunks out of order"


def assert_image_valid(image_content: Any):
    """Validate image content"""
    assert hasattr(image_content, "data"), "Image missing data"
    assert hasattr(image_content, "mime_type"), "Image missing mime_type"
    assert len(image_content.data) > 0, "Image data empty"
    
    # Validate base64
    import base64
    try:
        base64.b64decode(image_content.data)
    except Exception as e:
        raise AssertionError(f"Invalid base64 encoding: {e}")


def create_test_image(width: int = 100, height: int = 100, color: str = "red") -> bytes:
    """Create a test image for multimodal testing"""
    try:
        from PIL import Image, ImageDraw
        import io
        
        img = Image.new("RGB", (width, height), color)
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, width-10, height-10], outline="black", width=2)
        draw.text((width//2 - 20, height//2 - 5), "TEST", fill="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    except ImportError:
        # Return minimal PNG if PIL not available
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\xf8\xf3\xfe\xad\x00\x00\x00\x00IEND\xaeB`\x82'


def measure_latency(func: Callable) -> float:
    """Measure function execution latency in milliseconds"""
    start = time.perf_counter()
    func()
    return (time.perf_counter() - start) * 1000


async def measure_async_latency(func: Callable) -> float:
    """Measure async function execution latency"""
    start = time.perf_counter()
    await func()
    return (time.perf_counter() - start) * 1000


def validate_api_keys() -> Dict[str, bool]:
    """Check which API keys are available"""
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "gemini": bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")),
    }


def skip_if_no_api_key(provider: str):
    """Decorator to skip test if API key not available"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not validate_api_keys().get(provider):
                raise AssertionError(f"Skipped: No API key for {provider}")
            return func(*args, **kwargs)
        return wrapper
    return decorator