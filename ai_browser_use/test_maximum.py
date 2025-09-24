"""
Test the ultimate maximum element detection system
"""
import asyncio
import os
import sys

# Set UTF-8 environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

from ultimate_showcase_maximum import UltimateShowcaseMaximum

async def main():
    """Run the maximum detection showcase."""
    print("="*80)
    print("TESTING MAXIMUM ELEMENT DETECTION SYSTEM")
    print("="*80)

    # Test with uat.citi.com
    url = "https://uat.citi.com"
    print(f"Testing with URL: {url}")
    print("This will deploy ALL advanced detection strategies:")
    print("  [+] Advanced micro-scrolling detection")
    print("  [+] Shadow DOM penetration")
    print("  [+] Interaction-triggered discovery")
    print("  [+] Accessibility tree analysis")
    print("  [+] Frame/iframe scanning")
    print("  [+] Multi-viewport testing")
    print("  [+] Dynamic content monitoring")
    print("  [+] Event listener detection")
    print("  [+] Mutation observer tracking")
    print("  [+] Revolutionary visual effects")
    print("="*80)

    showcase = UltimateShowcaseMaximum(url, headless=False)
    await showcase.run_maximum_showcase()

if __name__ == "__main__":
    asyncio.run(main())