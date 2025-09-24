"""
Test script for ultimate_showcase_beautiful.py
"""
import asyncio
import os
import sys

# Set UTF-8 environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

from ultimate_showcase_beautiful import UltimateShowcaseBeautiful

async def main():
    """Run the beautiful showcase."""
    print("="*60)
    print("TESTING BEAUTIFUL SHOWCASE")
    print("="*60)

    url = "https://www.example.com"  # Use a simpler URL for testing
    print(f"Testing with URL: {url}")

    showcase = UltimateShowcaseBeautiful(url, headless=False)
    await showcase.run_beautiful_showcase()

if __name__ == "__main__":
    asyncio.run(main())