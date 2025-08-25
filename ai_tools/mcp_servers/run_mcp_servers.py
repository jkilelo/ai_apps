#!/usr/bin/env python3
"""
MCP Server Runner
Run MCP servers individually or all together
"""

import sys
import asyncio
import argparse
from pathlib import Path
import signal
import logging

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_signal_handlers(servers):
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(sig, frame):
        logger.info("\nShutting down servers...")
        for server in servers:
            try:
                server.shutdown()
            except:
                pass
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def run_chunk_server():
    """Run the Chunk Server."""
    from chunk_server_fixed import ChunkServer
    logger.info("Starting Chunk Server...")
    server = ChunkServer()
    logger.info("Chunk Server is ready!")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Chunk Server shutting down...")


async def run_index_server():
    """Run the Index Server."""
    from index_server_fixed import IndexServer
    logger.info("Starting Index Server...")
    server = IndexServer()
    logger.info("Index Server is ready!")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Index Server shutting down...")


async def run_vector_server():
    """Run the Vector Server."""
    from vector_server_fixed import VectorServer
    logger.info("Starting Vector Server...")
    server = VectorServer()
    logger.info("Vector Server is ready!")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Vector Server shutting down...")


async def run_edit_server():
    """Run the Edit Server."""
    from edit_server_fixed import EditServer
    logger.info("Starting Edit Server...")
    server = EditServer()
    logger.info("Edit Server is ready!")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Edit Server shutting down...")


async def run_all_servers():
    """Run all servers concurrently."""
    logger.info("Starting all MCP servers...")
    
    # Import all servers
    from chunk_server_fixed import ChunkServer
    from index_server_fixed import IndexServer
    from vector_server_fixed import VectorServer
    from edit_server_fixed import EditServer
    
    # Initialize servers
    servers = []
    try:
        chunk_server = ChunkServer()
        servers.append(chunk_server)
        logger.info("✓ Chunk Server initialized")
        
        index_server = IndexServer()
        servers.append(index_server)
        logger.info("✓ Index Server initialized")
        
        vector_server = VectorServer()
        servers.append(vector_server)
        logger.info("✓ Vector Server initialized")
        
        edit_server = EditServer()
        servers.append(edit_server)
        logger.info("✓ Edit Server initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize servers: {e}")
        return
    
    # Setup signal handlers
    setup_signal_handlers(servers)
    
    logger.info("\n" + "="*60)
    logger.info("All MCP servers are running!")
    logger.info("Press Ctrl+C to stop all servers")
    logger.info("="*60 + "\n")
    
    # Keep servers running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down all servers...")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run MCP Servers')
    parser.add_argument(
        'server',
        choices=['chunk', 'index', 'vector', 'edit', 'all'],
        help='Server to run (or "all" for all servers)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Suppress MCP SDK warnings
    import warnings
    warnings.filterwarnings("ignore", message="MCP SDK not installed")
    
    # Map server names to functions
    server_map = {
        'chunk': run_chunk_server,
        'index': run_index_server,
        'vector': run_vector_server,
        'edit': run_edit_server,
        'all': run_all_servers
    }
    
    # Run selected server(s)
    try:
        asyncio.run(server_map[args.server]())
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if running without arguments - show help
    if len(sys.argv) == 1:
        print("MCP Server Runner")
        print("="*60)
        print("\nUsage:")
        print("  python run_mcp_servers.py <server>")
        print("\nAvailable servers:")
        print("  chunk  - Code chunking and analysis")
        print("  index  - Code indexing and search")
        print("  vector - Vector storage and similarity search")
        print("  edit   - Code editing and refactoring")
        print("  all    - Run all servers")
        print("\nExample:")
        print("  python run_mcp_servers.py all")
        print("  python run_mcp_servers.py chunk --debug")
        sys.exit(0)
    
    main()