#!/usr/bin/env python3
"""
Windows-compatible Enhanced E-commerce Research Example
Fixed for Windows console encoding issues
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger without emojis for Windows compatibility
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


class WindowsCompatibleEcommerceDemo:
    """Windows-compatible e-commerce research demo"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/enhanced_ecommerce_research")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"ecommerce_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def search_product(self, product_query: str) -> Dict[str, Any]:
        """Search for a product with live LLM integration"""
        logger.info(f"Searching Amazon for: {product_query}")
        
        browser = AIBrowser({"log_level": "INFO"})
        start_time = asyncio.get_event_loop().time()
        
        try:
            task = f"""
            Go to Amazon.com and search for '{product_query}'.
            Find the first 3-5 relevant products and extract:
            1. Product name and title
            2. Current price and any original/discounted price  
            3. Customer rating (stars) and number of reviews
            4. Availability status (in stock, out of stock, etc.)
            5. Brand and model information
            6. Key product specifications
            7. Product URL
            
            Be thorough and accurate. Handle any popups or region selections.
            Use systematic analysis to ensure complete information extraction.
            """
            
            config = TaskConfig(
                task=task,
                url="https://www.amazon.com",
                headless=True,  # Run headless to avoid GUI issues
                max_steps=15,
                timeout=90000,
                screenshot_on_error=True
            )
            
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "query": product_query,
                "status": result.get('status', 'unknown'),
                "summary": result.get('summary', 'No summary available'),
                "extracted_data": result.get('extracted_data', {}),
                "final_url": result.get('final_url', ''),
                "response_time_ms": response_time,
                "success": result.get('status') == 'completed'
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "query": product_query,
                "status": "failed",
                "error": str(e),
                "success": False
            }
        finally:
            await browser.cleanup()
    
    async def run_demo(self):
        """Run the Windows-compatible demo"""
        print("\n" + "="*60)
        print("AI-POWERED E-COMMERCE RESEARCH - Windows Compatible")
        print("="*60)
        print("This demo showcases real-world browser automation with live LLM calls")
        print("Demonstrates the AI Browser v2.0.0 capabilities with working examples")
        print()
        
        # Test product for demonstration
        product_query = "wireless bluetooth headphones under $100"
        print(f"Product Research Query: {product_query}")
        print("Running live LLM-powered browser automation...")
        print("This will take 2-3 minutes for comprehensive analysis...")
        print()
        
        # Run the search with real LLM calls
        result = await self.search_product(product_query)
        
        # Display results
        print("="*60)
        print("RESEARCH RESULTS")
        print("="*60)
        
        print(f"Query: {result['query']}")
        print(f"Status: {result['status']}")
        print(f"Response Time: {result.get('response_time_ms', 0):.0f}ms")
        print(f"Success: {result.get('success', False)}")
        print()
        
        if result.get('success'):
            print("EXTRACTED INFORMATION:")
            print("-" * 30)
            summary = result.get('summary', '')
            
            # Show first few lines of summary
            if summary:
                for line in summary.split('\n')[:10]:
                    if line.strip():
                        print(f"  {line.strip()}")
                print()
            
            # Show final URL visited
            if result.get('final_url'):
                print(f"Final URL: {result['final_url']}")
            
            print("SUCCESS: Live LLM integration with real browser automation working!")
            
        else:
            print("FAILED: Could not complete the research")
            if result.get('error'):
                print(f"Error: {result['error']}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"demo_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\nResults saved to: {results_file}")
        print("="*60)
        
        return result


async def main():
    """Main entry point"""
    try:
        demo = WindowsCompatibleEcommerceDemo()
        result = await demo.run_demo()
        
        if result.get('success'):
            print("\nDEMO COMPLETED SUCCESSFULLY!")
            print("The AI Browser v2.0.0 is working with live LLM integration!")
        else:
            print("\nDEMO ENCOUNTERED ISSUES:")
            print("Check the error details above and system configuration.")
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())