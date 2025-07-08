"""
Platform utilities for cross-platform compatibility
"""

import platform
import sys
import os
import asyncio
from typing import Dict, Any, Optional


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


def get_asyncio_policy():
    """Get the appropriate asyncio event loop policy for the platform"""
    if platform.system() == "Windows":
        # Windows requires special handling for asyncio
        # ProactorEventLoop is the default on Windows for Python 3.8+
        if sys.version_info >= (3, 8):
            return asyncio.WindowsProactorEventLoopPolicy()
        else:
            return asyncio.WindowsSelectorEventLoopPolicy()
    else:
        # Try to use uvloop on Unix systems for better performance
        try:
            import uvloop
            return uvloop.EventLoopPolicy()
        except ImportError:
            # Fall back to default policy
            return asyncio.DefaultEventLoopPolicy()


def setup_event_loop():
    """Setup the event loop with platform-appropriate settings"""
    policy = get_asyncio_policy()
    asyncio.set_event_loop_policy(policy)
    
    if platform.system() == "Windows":
        # Windows-specific: Set up proper signal handling
        # This helps with graceful shutdown
        import signal
        signal.signal(signal.SIGINT, signal.default_int_handler)


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
    elif system == "Darwin":  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    else:  # Linux
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


def get_temp_directory() -> str:
    """Get platform-appropriate temporary directory"""
    import tempfile
    return tempfile.gettempdir()


def get_downloads_directory() -> str:
    """Get platform-appropriate downloads directory"""
    system = platform.system()
    
    if system == "Windows":
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            downloads_dir = winreg.QueryValueEx(key, downloads_guid)[0]
        return downloads_dir
    else:
        # Unix-like systems
        return os.path.expanduser("~/Downloads")


def normalize_path(path: str) -> str:
    """Normalize path for the current platform"""
    # Convert forward slashes to backslashes on Windows
    if platform.system() == "Windows":
        path = path.replace("/", "\\")
    else:
        path = path.replace("\\", "/")
    
    # Expand user directory and environment variables
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    
    # Get absolute path
    return os.path.abspath(path)


def get_process_manager_command() -> str:
    """Get the appropriate process manager command for the platform"""
    system = platform.system()
    
    if system == "Windows":
        return "tasklist"
    elif system == "Darwin":
        return "ps aux"
    else:  # Linux
        return "ps aux"


def is_port_available(port: int) -> bool:
    """Check if a port is available on the current platform"""
    import socket
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("", port))
            return True
        except socket.error:
            return False


def get_recommended_workers() -> int:
    """Get recommended number of workers based on platform and CPU"""
    if platform.system() == "Windows":
        # Windows has issues with multiple workers in some ASGI servers
        return 1
    else:
        # Unix-like systems can handle multiple workers well
        cpu_count = os.cpu_count() or 1
        # Use (CPU cores * 2) + 1 as a general rule
        return min(cpu_count * 2 + 1, 8)  # Cap at 8 workers


# Platform-specific imports helper
def import_platform_specific():
    """Import platform-specific modules safely"""
    modules = {}
    
    if platform.system() != "Windows":
        try:
            import uvloop
            modules["uvloop"] = uvloop
        except ImportError:
            pass
    
    return modules


# Playwright platform-specific settings
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
        # Linux often needs --no-sandbox in containers
        options["args"].append("--no-sandbox")
        options["args"].append("--disable-setuid-sandbox")
    
    if platform.system() == "Windows":
        # Windows-specific options
        options["args"].append("--disable-gpu")
    
    # Use system Chrome if available
    chrome_path = get_chrome_executable_path()
    if chrome_path:
        options["executable_path"] = chrome_path
    
    return options


def ensure_directories(*paths):
    """Ensure directories exist (cross-platform)"""
    for path in paths:
        normalized_path = normalize_path(path)
        os.makedirs(normalized_path, exist_ok=True)


if __name__ == "__main__":
    # Test platform detection
    info = get_platform_info()
    print("Platform Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print(f"\nChrome executable: {get_chrome_executable_path()}")
    print(f"Temp directory: {get_temp_directory()}")
    print(f"Downloads directory: {get_downloads_directory()}")
    print(f"Recommended workers: {get_recommended_workers()}")
    print(f"Port 8080 available: {is_port_available(8080)}")