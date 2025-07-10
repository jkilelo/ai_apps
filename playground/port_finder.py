#!/usr/bin/env python3
"""
Utility to find available free ports for testing
"""

import socket
import random
from typing import Optional, List
from contextlib import closing


def find_free_port(start: int = 8000, end: int = 9000, exclude: Optional[List[int]] = None) -> int:
    """
    Find a free port in the given range
    
    Args:
        start: Starting port number (inclusive)
        end: Ending port number (exclusive)
        exclude: List of ports to exclude from search
        
    Returns:
        An available port number
        
    Raises:
        RuntimeError: If no free port is found
    """
    exclude = exclude or []
    
    # Try random ports first for better distribution
    attempts = min(100, end - start)
    for _ in range(attempts):
        port = random.randint(start, end - 1)
        if port in exclude:
            continue
            
        if is_port_free(port):
            return port
    
    # If random didn't work, try sequential
    for port in range(start, end):
        if port in exclude:
            continue
            
        if is_port_free(port):
            return port
            
    raise RuntimeError(f"No free port found in range {start}-{end}")


def is_port_free(port: int, host: str = '127.0.0.1') -> bool:
    """
    Check if a port is free on the given host
    
    Args:
        port: Port number to check
        host: Host to check (default: localhost)
        
    Returns:
        True if port is free, False otherwise
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def find_multiple_free_ports(count: int, start: int = 8000, end: int = 9000) -> List[int]:
    """
    Find multiple free ports
    
    Args:
        count: Number of ports to find
        start: Starting port number
        end: Ending port number
        
    Returns:
        List of free port numbers
    """
    ports = []
    for _ in range(count):
        port = find_free_port(start, end, exclude=ports)
        ports.append(port)
    return ports


if __name__ == "__main__":
    # Test the utility
    print("Port Finder Utility Test")
    print("=" * 40)
    
    # Find single port
    port = find_free_port()
    print(f"Found free port: {port}")
    
    # Verify it's free
    print(f"Is port {port} free? {is_port_free(port)}")
    
    # Find multiple ports
    ports = find_multiple_free_ports(3)
    print(f"Found multiple free ports: {ports}")
    
    # Test specific range
    port = find_free_port(9500, 9600)
    print(f"Found free port in range 9500-9600: {port}")