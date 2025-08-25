"""
Startup script for Web Automation Pipeline
Senior Integration Engineer Pattern: Proper Application Startup
"""

import uvicorn
import sys
from pathlib import Path
import asyncio
import signal
import logging
from typing import Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.web_automation.config import settings

# Configure logging based on settings
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

class ApplicationServer:
    """Application server with graceful shutdown"""
    
    def __init__(self):
        self.server: Optional[uvicorn.Server] = None
        self.should_exit = False
        
    async def startup(self):
        """Startup tasks"""
        logger.info("Starting Web Automation Pipeline...")
        settings.display_configuration()
        
        # Validate configuration
        if not settings.validate_configuration():
            logger.error("Configuration validation failed. Exiting...")
            sys.exit(1)
        
        # Additional startup tasks
        logger.info("Configuration validated")
        logger.info("Ready to accept connections")
        
    async def shutdown(self):
        """Cleanup tasks"""
        logger.info("Shutting down Web Automation Pipeline...")
        
        # Cleanup tasks here
        await asyncio.sleep(0.5)  # Allow time for cleanup
        
        logger.info("Shutdown complete")
        
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {sig}")
        self.should_exit = True
        if self.server:
            self.server.should_exit = True
            
    async def run(self):
        """Run the application server"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Startup
        await self.startup()
        
        # Configure uvicorn
        config = uvicorn.Config(
            app="backend.web_automation.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=settings.debug,
            use_colors=True,
            server_header=False,
            date_header=False
        )
        
        self.server = uvicorn.Server(config)
        
        # Run server
        try:
            await self.server.serve()
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            await self.shutdown()

def main():
    """Main entry point"""
    print("""
    ============================================================
            Web Automation Pipeline v2.0                      
            Senior Integration Engineer Edition               
    ============================================================
    """)
    
    # Create and run server
    server = ApplicationServer()
    
    # Run with asyncio
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()