"""
Test the beautiful showcase with a site that has more elements
"""
import asyncio
import os
import sys

# Set UTF-8 environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

from ultimate_showcase_beautiful import UltimateShowcaseBeautiful

async def main():
    """Run the beautiful showcase with uat.citi.com."""
    print("="*60)
    print("TESTING BEAUTIFUL SHOWCASE - FULL SITE")
    print("="*60)

    # Test with uat.citi.com as requested
    url = "https://uat.citi.com"
    print(f"Testing with URL: {url}")
    print("This will showcase:")
    print("  - Premium glassmorphism effects")
    print("  - Aurora gradient animations")
    print("  - Floating particles")
    print("  - Multi-layer shadows")
    print("  - Elegant micro-interactions")
    print("="*60)

    showcase = UltimateShowcaseBeautiful(url, headless=False)
    await showcase.run_beautiful_showcase()

if __name__ == "__main__":
    asyncio.run(main())