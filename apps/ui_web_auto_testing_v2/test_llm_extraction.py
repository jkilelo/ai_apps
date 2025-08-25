"""
Test to show the actual structure of elements extracted with LLM analysis
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from apps.ui_web_auto_testing_v2.element_extractor import extract_elements_from_url


async def main():
    """Show the actual structure with LLM analysis"""
    
    url = "https://quotes.toscrape.com/login"
    
    print("EXTRACTING ELEMENTS WITH LLM ANALYSIS")
    print("="*50)
    print(f"URL: {url}\n")
    
    # Extract with LLM analysis enabled
    print("Extracting and analyzing elements...")
    result = await extract_elements_from_url(
        url,
        headless=False,
        analyze=True  # Enable LLM analysis
    )
    
    # Show the complete structure
    print("\nCOMPLETE STRUCTURE WITH LLM ANALYSIS:")
    print("="*50)
    print(json.dumps(result, indent=2))
    
    # Save to file for review
    with open("llm_extraction_output.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\nOutput saved to: llm_extraction_output.json")


if __name__ == "__main__":
    asyncio.run(main())