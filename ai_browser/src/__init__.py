"""AI-First Browser Automation Framework"""

__version__ = "2.0.0"
__author__ = "AI Browser Team"

# Optional imports - main.py can be run directly
try:
    from .main import AIBrowser
    __all__ = ["AIBrowser"]
except ImportError:
    # Allow module to be imported even if main.py has issues
    __all__ = []