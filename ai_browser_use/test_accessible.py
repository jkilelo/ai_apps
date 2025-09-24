"""
Test script for ultimate_showcase_accessible.py with uat.citi.com
"""
import asyncio
import sys
import os

# Set UTF-8 environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

from ultimate_showcase_accessible import UltimateShowcaseAccessible

async def main():
    """Run the accessible showcase with uat.citi.com."""
    print("="*60)
    print("TESTING ACCESSIBLE SHOWCASE")
    print("="*60)

    url = "https://uat.citi.com"
    print(f"Testing with URL: {url}")

    showcase = UltimateShowcaseAccessible(url, headless=False)
    await showcase.run_accessible_showcase()

if __name__ == "__main__":
    asyncio.run(main())