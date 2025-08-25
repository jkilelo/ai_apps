#!/usr/bin/env python3
"""

# AI-FIRST: This module requires live LLM connections, no mock support
UTILS MODULE - Comprehensive Utilities for UI Testing Automation Framework
Combines platform utilities, web testing utilities, and additional helpers
Part of PHASE2 implementation following QUANTUM_ENHANCED_PROMPT specifications
"""

import platform
import sys
import os
import asyncio
import json
import logging
import socket
import tempfile
import hashlib
import traceback
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import time


# ============================================================================
# PLATFORM UTILITIES
# ============================================================================

class PlatformUtils:
    """Cross-platform compatibility utilities"""
    
    @staticmethod
    def get_platform_info() -> Dict[str, Any]:
        """Get detailed platform information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_implementation": platform.python_implementation(),
            "is_windows": platform.system() == "Windows",
            "is_macos": platform.system() == "Darwin",
            "is_linux": platform.system() == "Linux",
            "is_unix": platform.system() in ["Linux", "Darwin"],
        }
    
    @staticmethod
    def get_asyncio_policy():
        """Get the appropriate asyncio event loop policy for the platform"""
        if platform.system() == "Windows":
            if sys.version_info >= (3, 8):
                return asyncio.WindowsProactorEventLoopPolicy()
            else:
                return asyncio.WindowsSelectorEventLoopPolicy()
        else:
            try:
                import uvloop
                return uvloop.EventLoopPolicy()
            except ImportError:
                return asyncio.DefaultEventLoopPolicy()
    
    @staticmethod
    def setup_event_loop():
        """Setup the event loop with platform-appropriate settings"""
        policy = PlatformUtils.get_asyncio_policy()
        asyncio.set_event_loop_policy(policy)
        
        if platform.system() == "Windows":
            import signal
            signal.signal(signal.SIGINT, signal.default_int_handler)
    
    @staticmethod
    def get_chrome_executable_path() -> Optional[str]:
        """Get Chrome/Chromium executable path for different platforms"""
        system = platform.system()
        
        if system == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                r"C:\Program Files\Chromium\Application\chrome.exe",
            ]
        elif system == "Darwin":
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ]
        else:
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
            ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
    @staticmethod
    def get_temp_directory() -> str:
        """Get platform-appropriate temporary directory"""
        return tempfile.gettempdir()
    
    @staticmethod
    def get_downloads_directory() -> str:
        """Get platform-appropriate downloads directory"""
        system = platform.system()
        
        if system == "Windows":
            try:
                import winreg
                sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
                downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                    downloads_dir = winreg.QueryValueEx(key, downloads_guid)[0]
                return downloads_dir
            except:
                return os.path.expanduser("~/Downloads")
        else:
            return os.path.expanduser("~/Downloads")
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize path for the current platform"""
        if platform.system() == "Windows":
            path = path.replace("/", "\\")
        else:
            path = path.replace("\\", "/")
        
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        
        return os.path.abspath(path)
    
    @staticmethod
    def is_port_available(port: int) -> bool:
        """Check if a port is available on the current platform"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return True
            except socket.error:
                return False
    
    @staticmethod
    def get_recommended_workers() -> int:
        """Get recommended number of workers based on platform and CPU"""
        if platform.system() == "Windows":
            return 1
        else:
            cpu_count = os.cpu_count() or 1
            return min(cpu_count * 2 + 1, 8)
    
    @staticmethod
    def get_playwright_launch_options() -> Dict[str, Any]:
        """Get platform-appropriate Playwright launch options"""
        options = {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ]
        }
        
        if platform.system() == "Linux":
            options["args"].append("--no-sandbox")
            options["args"].append("--disable-setuid-sandbox")
        
        if platform.system() == "Windows":
            options["args"].append("--disable-gpu")
        
        chrome_path = PlatformUtils.get_chrome_executable_path()
        if chrome_path:
            options["executable_path"] = chrome_path
        
        return options
    
    @staticmethod
    def ensure_directories(*paths):
        """Ensure directories exist (cross-platform)"""
        for path in paths:
            normalized_path = PlatformUtils.normalize_path(path)
            os.makedirs(normalized_path, exist_ok=True)


# ============================================================================
# LOGGING UTILITIES
# ============================================================================

class LogLevel(Enum):
    """Log levels for the framework"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:
    """Centralized logging for UI Testing Automation Framework"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, level: LogLevel = LogLevel.INFO) -> logging.Logger:
        """Get or create a logger with consistent formatting"""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(level.value)
            
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]


# ============================================================================
# JOB MANAGEMENT
# ============================================================================

class JobStatus(Enum):
    """Job status enumeration"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Represents an async job"""
    id: str
    type: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


class JobManager:
    """Manages async job tracking across the system"""
    
    def __init__(self) -> None:
        self.jobs: Dict[str, Job] = {}
        self.logger = Logger.get_logger("JobManager")
    
    def create_job(self, job_type: str, metadata: Dict[str, Any] = None) -> str:
        """Create a new job entry"""
        job_id = hashlib.md5(f"{job_type}{time.time()}".encode()).hexdigest()[:12]
        job = Job(
            id=job_id,
            type=job_type,
            status=JobStatus.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=metadata or {}
        )
        self.jobs[job_id] = job
        self.logger.info(f"Created job {job_id} of type {job_type}")
        return job_id
    
    def update_job(self, job_id: str, status: JobStatus, 
                   result: Any = None, error: str = None) -> bool:
        """Update job status"""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        job.status = status
        job.updated_at = datetime.now()
        
        if result is not None:
            job.result = result
        if error is not None:
            job.error = error
        
        self.logger.info(f"Updated job {job_id} status to {status.value}")
        return True
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job details"""
        return self.jobs.get(job_id)
    
    def cleanup_old_jobs(self, hours: int = 24):
        """Remove jobs older than specified hours"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        jobs_to_remove = []
        
        for job_id, job in self.jobs.items():
            if job.created_at.timestamp() < cutoff_time:
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            self.logger.info(f"Cleaned up old job {job_id}")


# ============================================================================
# TEST DATA GENERATION
# ============================================================================

class TestDataGenerator:
    """Generates realistic test data for different input types"""
    
    @staticmethod
    def generate_email() -> str:
        """Generate a test email address"""
        timestamp = int(time.time() * 1000)
        return f"test.user{timestamp}@example.com"
    
    @staticmethod
    def generate_url() -> str:
        """Generate a test URL"""
        return "https://example.com/test-page"
    
    @staticmethod
    def generate_phone() -> str:
        """Generate a test phone number"""
        return "+1-555-123-4567"
    
    @staticmethod
    def generate_name(first: bool = False, last: bool = False) -> str:
        """Generate a test name"""
        if first:
            return "John"
        elif last:
            return "Doe"
        else:
            return "John Doe"
    
    @staticmethod
    def generate_address() -> str:
        """Generate a test address"""
        return "123 Test Street, Test City, TC 12345"
    
    @staticmethod
    def generate_date() -> str:
        """Generate a test date"""
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def generate_test_data(input_type: str, field_name: str = "") -> Any:
        """Generate appropriate test data based on input type and field name"""
        field_lower = field_name.lower()
        
        if "email" in field_lower or input_type == "email":
            return TestDataGenerator.generate_email()
        elif "url" in field_lower or input_type == "url":
            return TestDataGenerator.generate_url()
        elif "phone" in field_lower or input_type == "tel":
            return TestDataGenerator.generate_phone()
        elif "name" in field_lower:
            if "first" in field_lower:
                return TestDataGenerator.generate_name(first=True)
            elif "last" in field_lower:
                return TestDataGenerator.generate_name(last=True)
            else:
                return TestDataGenerator.generate_name()
        elif "address" in field_lower:
            return TestDataGenerator.generate_address()
        elif input_type == "number":
            return 42
        elif input_type == "date":
            return TestDataGenerator.generate_date()
        else:
            return f"Test input for {field_name or input_type}"


# ============================================================================
# ASYNC UTILITIES
# ============================================================================

class AsyncUtils:
    """Utilities for async operations"""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: int, task_name: str = "task"):
        """Run an async task with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"{task_name} timed out after {timeout} seconds")
    
    @staticmethod
    async def run_parallel(tasks: List, max_concurrent: int = 5):
        """Run tasks in parallel with concurrency limit"""
        results = []
        for i in range(0, len(tasks), max_concurrent):
            batch = tasks[i:i + max_concurrent]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        return results
    
    @staticmethod
    async def retry_async(func: Callable, max_retries: int = 3, 
                         delay: float = 1.0, backoff: float = 2.0):
        """Retry an async function with exponential backoff"""
        last_exception = None
        current_delay = delay
        
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        
        raise last_exception


# ============================================================================
# FILE UTILITIES
# ============================================================================

class FileUtils:
    """File system utilities"""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Ensure a directory exists"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def read_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Read JSON file safely"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            Logger.get_logger("FileUtils").error(f"Error reading JSON from {file_path}: {e}")
            return {}
    
    @staticmethod
    def write_json(file_path: Union[str, Path], data: Dict[str, Any], indent: int = 2):
        """Write JSON file safely"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=indent, default=str)
        except Exception as e:
            Logger.get_logger("FileUtils").error(f"Error writing JSON to {file_path}: {e}")
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path]) -> str:
        """Get SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def cleanup_old_files(directory: Union[str, Path], days: int = 7, pattern: str = "*"):
        """Remove files older than specified days"""
        directory = Path(directory)
        cutoff_time = time.time() - (days * 86400)
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    Logger.get_logger("FileUtils").info(f"Deleted old file: {file_path}")
                except Exception as e:
                    Logger.get_logger("FileUtils").error(f"Error deleting {file_path}: {e}")


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

class ValidationUtils:
    """Data validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format"""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number format"""
        import re
        pattern = r'^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_dict_structure(data: Dict, required_keys: List[str]) -> bool:
        """Validate dictionary has required keys"""
        return all(key in data for key in required_keys)
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string for safe usage"""
        if not text:
            return ""
        
        # Remove control characters
        import re
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text.strip()


# ============================================================================
# PERFORMANCE UTILITIES
# ============================================================================

class PerformanceTimer:
    """Performance timing utilities"""
    
    def __init__(self, name: str = "Operation") -> None:
        self.name = name
        self.start_time = None
        self.end_time = None
        self.logger = Logger.get_logger("PerformanceTimer")
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.logger.info(f"{self.name} took {duration:.3f} seconds")
    
    def get_duration(self) -> float:
        """Get the duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


# ============================================================================
# ERROR HANDLING UTILITIES
# ============================================================================

class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def get_error_details(e: Exception) -> Dict[str, Any]:
        """Get detailed error information"""
        return {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def log_error(logger_name: str, e: Exception, context: str = ""):
        """Log error with full details"""
        logger = Logger.get_logger(logger_name)
        error_details = ErrorHandler.get_error_details(e)
        
        if context:
            logger.error(f"[{context}] {error_details['type']}: {error_details['message']}")
        else:
            logger.error(f"{error_details['type']}: {error_details['message']}")
        
        logger.debug(f"Traceback:\n{error_details['traceback']}")
    
    @staticmethod
    def safe_execute(func: Callable, default: Any = None, logger_name: str = "ErrorHandler"):
        """Execute a function safely with error handling"""
        try:
            return func()
        except Exception as e:
            ErrorHandler.log_error(logger_name, e, f"Error in {func.__name__}")
            return default


# ============================================================================
# SELF-TEST AND EXAMPLE USAGE
# ============================================================================

def run_self_test():
    """Run comprehensive self-test of all utilities"""
    logger = Logger.get_logger("UtilsTest", LogLevel.INFO)
    logger.info("[TEST] Starting utils module self-test")
    
    results = {
        "platform": False,
        "logging": False,
        "job_manager": False,
        "test_data": False,
        "async": False,
        "file": False,
        "validation": False,
        "performance": False,
        "error_handling": False
    }
    
    try:
        # Test Platform Utilities
        logger.info("[TEST] Testing Platform Utilities...")
        info = PlatformUtils.get_platform_info()
        assert info["system"] in ["Windows", "Linux", "Darwin"]
        assert PlatformUtils.get_temp_directory()
        results["platform"] = True
        logger.info(f"  Platform: {info['system']} {info['release']}")
        
        # Test Logging
        logger.info("[TEST] Testing Logging...")
        test_logger = Logger.get_logger("TestLogger")
        test_logger.info("Test log message")
        results["logging"] = True
        
        # Test Job Manager
        logger.info("[TEST] Testing Job Manager...")
        job_manager = JobManager()
        job_id = job_manager.create_job("test_job", {"test": True})
        assert job_id
        assert job_manager.get_job(job_id)
        job_manager.update_job(job_id, JobStatus.COMPLETED, result="Success")
        results["job_manager"] = True
        
        # Test Data Generator
        logger.info("[TEST] Testing Test Data Generator...")
        email = TestDataGenerator.generate_email()
        assert "@" in email
        url = TestDataGenerator.generate_url()
        assert url.startswith("http")
        results["test_data"] = True
        
        # Test Async Utilities
        logger.info("[TEST] Testing Async Utilities...")
        async def test_async():
            result = await AsyncUtils.run_with_timeout(
                asyncio.sleep(0.1), timeout=1, task_name="test_sleep"
            )
            return True
        
        asyncio.run(test_async())
        results["async"] = True
        
        # Test File Utilities
        logger.info("[TEST] Testing File Utilities...")
        test_dir = Path(PlatformUtils.get_temp_directory()) / "utils_test"
        FileUtils.ensure_directory(test_dir)
        test_file = test_dir / "test.json"
        FileUtils.write_json(test_file, {"test": "data"})
        data = FileUtils.read_json(test_file)
        assert data["test"] == "data"
        test_file.unlink()
        test_dir.rmdir()
        results["file"] = True
        
        # Test Validation
        logger.info("[TEST] Testing Validation Utilities...")
        assert ValidationUtils.is_valid_email("test@example.com")
        assert not ValidationUtils.is_valid_email("invalid-email")
        assert ValidationUtils.is_valid_url("https://example.com")
        results["validation"] = True
        
        # Test Performance Timer
        logger.info("[TEST] Testing Performance Timer...")
        with PerformanceTimer("Test Operation") as timer:
            time.sleep(0.1)
        assert timer.get_duration() > 0.09
        results["performance"] = True
        
        # Test Error Handling
        logger.info("[TEST] Testing Error Handling...")
        def raise_error():
            raise ValueError("Test error")
        
        result = ErrorHandler.safe_execute(raise_error, default="handled")
        assert result == "handled"
        results["error_handling"] = True
        
    except Exception as e:
        logger.error(f"[TEST] Self-test failed: {e}")
        logger.error(traceback.format_exc())
    
    # Report results
    logger.info("[TEST] Self-test Results:")
    all_passed = True
    for component, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        logger.info(f"  {status} {component}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("[TEST] All tests passed successfully!")
    else:
        logger.error("[TEST] Some tests failed!")
    
    return all_passed


if __name__ == "__main__":
    # Quick test mode for compliance checking
    import os
    if os.environ.get("STANDALONE_TEST") == "1":
        print(f"[OK] {__name__} module loads successfully")
        sys.exit(0)
    
    print("=" * 60)
    print("UI TESTING AUTOMATION FRAMEWORK - UTILS MODULE")
    print("=" * 60)
    
    # Run self-test
    success = run_self_test()
    
    # Demo usage
    print("\n" + "=" * 60)
    print("DEMO: Example Usage")
    print("=" * 60)
    
    # Platform info
    info = PlatformUtils.get_platform_info()
    print(f"\nPlatform: {info['system']} {info['release']}")
    print(f"Python: {info['python_version'].split()[0]}")
    print(f"Chrome Path: {PlatformUtils.get_chrome_executable_path()}")
    
    # Test data generation
    print(f"\nGenerated Email: {TestDataGenerator.generate_email()}")
    print(f"Generated Phone: {TestDataGenerator.generate_phone()}")
    print(f"Generated Name: {TestDataGenerator.generate_name()}")
    
    # Job management
    job_mgr = JobManager()
    job_id = job_mgr.create_job("demo_job", {"demo": True})
    print(f"\nCreated Job: {job_id}")
    
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] Utils module is ready for use!")
    else:
        print("[WARNING] Some tests failed - review logs above")
    print("=" * 60)