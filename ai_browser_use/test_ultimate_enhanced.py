"""
Test script for ultimate_showcase_enhanced.py
Runs without requiring stdin input.
"""
import asyncio
import sys
import os

# Force UTF-8 encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Import the showcase
from ultimate_showcase_enhanced import UltimateShowcaseEnhanced

async def main():
    """Run the showcase with a default URL."""
    print("="*60)
    print("🌟 TESTING ULTIMATE ENHANCED SHOWCASE")
    print("="*60)

    # Use a simple test URL
    url = "https://www.example.com"
    print(f"Testing with URL: {url}")

    showcase = UltimateShowcaseEnhanced(url, headless=False)
    await showcase.run_enhanced_showcase()

if __name__ == "__main__":
    asyncio.run(main())