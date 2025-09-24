"""
Test the ultra-premium showcase with exhaustive element detection
"""
import asyncio
import os
import sys

# Set UTF-8 environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

from ultimate_showcase_ultra_premium import UltimateShowcaseUltraPremium

async def main():
    """Run the ultra-premium showcase with exhaustive scrolling."""
    print("="*60)
    print("TESTING ULTRA PREMIUM SHOWCASE - EXHAUSTIVE DETECTION")
    print("="*60)

    # Test with uat.citi.com
    url = "https://uat.citi.com"
    print(f"Testing with URL: {url}")
    print("This will showcase:")
    print("  - EXHAUSTIVE element detection (scrolls entire page)")
    print("  - Quantum visual effects")
    print("  - Matrix rain background")
    print("  - AI-powered analysis panel")
    print("  - Neural network visualization")
    print("  - Holographic UI elements")
    print("  - Energy wave animations")
    print("  - Neon cyberpunk aesthetics")
    print("="*60)

    showcase = UltimateShowcaseUltraPremium(url, headless=False)
    await showcase.run_ultra_showcase()

if __name__ == "__main__":
    asyncio.run(main())