"""
Asyncio Helper for Python 3.13+ Compatibility
==============================================
Handles event loop configuration for Python 3.13+ on Windows
where ProactorEventLoop is required for subprocess operations.
"""

import sys
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def setup_asyncio_policy():
    """
    Setup the correct asyncio event loop policy for the current platform.
    This is especially important for Python 3.13+ on Windows.
    """
    if sys.platform == 'win32':
        # Windows requires special handling
        if sys.version_info >= (3, 13):
            # Python 3.13+ on Windows needs ProactorEventLoop for subprocesses
            try:
                loop = asyncio.get_running_loop()
                if not isinstance(loop, asyncio.ProactorEventLoop):
                    logger.warning("Current loop is not ProactorEventLoop, setting policy")
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            except RuntimeError:
                # No running loop, set the policy for future loops
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                logger.info("Set Windows ProactorEventLoop policy for Python 3.13+")
        elif sys.version_info >= (3, 8):
            # Python 3.8-3.12 on Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            logger.info("Set Windows ProactorEventLoop policy")
    else:
        # Unix-like systems
        try:
            # Try to use uvloop for better performance
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("Using uvloop for better performance")
        except ImportError:
            # Use default policy
            pass


def get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """
    Get the current event loop or create a new one with the correct policy.
    
    Returns:
        The event loop configured for the current platform
    """
    try:
        loop = asyncio.get_running_loop()
        
        # On Windows with Python 3.13+, verify it's the right type
        if sys.platform == 'win32' and sys.version_info >= (3, 13):
            if not isinstance(loop, asyncio.ProactorEventLoop):
                logger.warning("Current loop is not ProactorEventLoop, creating new one")
                raise RuntimeError("Need ProactorEventLoop")
        
        return loop
    except RuntimeError:
        # No running loop, create one with correct policy
        setup_asyncio_policy()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.info(f"Created new event loop: {type(loop).__name__}")
        return loop


def run_async(coro):
    """
    Run an async coroutine with proper event loop configuration.
    
    Args:
        coro: The coroutine to run
        
    Returns:
        The result of the coroutine
    """
    # Setup policy first
    setup_asyncio_policy()
    
    # Use asyncio.run which handles loop creation and cleanup
    return asyncio.run(coro)


# Auto-configure on import
setup_asyncio_policy()