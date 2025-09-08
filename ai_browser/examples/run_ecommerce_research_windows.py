#!/usr/bin/env python3
"""
Windows-compatible Real-World E-commerce Research Example
Fixed for Windows console encoding and optimized for demonstration
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger without emojis for Windows compatibility
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


class WindowsCompatibleEcommerceDemo:
    """Windows-compatible e-commerce research demo with live LLM integration"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/ecommerce_research")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"ecommerce_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def search_product_comparison(self, product_query: str) -> Dict[str, Any]:
        """Search for products with comparison across multiple sites"""
        logger.info(f"Starting multi-platform product search for: {product_query}")
        
        # For this demo, we'll focus on one platform but with thorough analysis
        browser = AIBrowser({"log_level": "INFO"})
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Enhanced task with comparison focus
            task = f"""
            Conduct comprehensive e-commerce research for '{product_query}':
            
            STEP 1: Go to Amazon.com and search for '{product_query}'
            STEP 2: Find the top 5-7 relevant products and systematically extract:
               - Complete product name and model
               - Current price and any discounts/original pricing
               - Customer ratings (stars out of 5) and total review count
               - Availability and shipping information
               - Brand, manufacturer, and key specifications
               - Product URLs for reference
            
            STEP 3: Analyze and compare the products found:
               - Identify price ranges and best value options
               - Compare features and specifications
               - Note highly-rated vs budget options
               - Highlight any standout deals or recommendations
            
            Be thorough and systematic. Handle popups, cookies, and regional settings.
            Focus on extracting actionable comparison data for informed purchasing decisions.
            """
            
            config = TaskConfig(
                task=task,
                url="https://www.amazon.com",
                headless=True,
                max_steps=20,  # More steps for comprehensive comparison
                timeout=150000,  # Extended timeout for thorough research
                screenshot_on_error=True
            )
            
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Parse the results for structured output
            analysis = self.extract_product_insights(result.get('summary', ''), product_query)
            
            return {
                "product_query": product_query,
                "status": result.get('status', 'unknown'),
                "summary": result.get('summary', 'No summary available'),
                "extracted_data": result.get('extracted_data', {}),
                "final_url": result.get('final_url', ''),
                "response_time_ms": response_time,
                "success": result.get('status') == 'completed',
                "product_analysis": analysis,
                "platforms_searched": ["Amazon"],
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"E-commerce search failed: {e}")
            return {
                "product_query": product_query,
                "status": "failed",
                "error": str(e),
                "success": False
            }
        finally:
            await browser.cleanup()
    
    def extract_product_insights(self, summary: str, original_query: str) -> Dict[str, Any]:
        """Extract structured product insights from search results"""
        if not summary:
            return {"error": "No summary to analyze"}
        
        insights = {
            "original_query": original_query,
            "products_identified": [],
            "price_analysis": {},
            "feature_comparison": {},
            "recommendations": {}
        }
        
        lines = summary.split('\n')
        current_product = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for product names (typically longer descriptive lines)
            if len(line) > 30 and not line.startswith(('Price', 'Rating', 'Available', '$')):
                if current_product:
                    insights["products_identified"].append(current_product)
                current_product = {"name": line[:100], "details": []}
            
            # Extract pricing information
            price_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', line)
            if price_match and current_product:
                current_product["price"] = price_match.group(1)
            
            # Extract ratings
            rating_match = re.search(r'(\d+(?:\.\d)?)\s*(?:star|out of 5|rating)', line.lower())
            if rating_match and current_product:
                current_product["rating"] = rating_match.group(1)
            
            # Extract review counts
            review_match = re.search(r'(\d+(?:,\d{3})*)\s*(?:review|customer)', line.lower())
            if review_match and current_product:
                current_product["reviews"] = review_match.group(1)
            
            # Add details to current product
            if current_product and len(line) > 10:
                current_product["details"].append(line[:150])
        
        # Add the last product if exists
        if current_product:
            insights["products_identified"].append(current_product)
        
        # Analyze prices if we found any
        prices = []
        for product in insights["products_identified"]:
            if "price" in product:
                try:
                    price_val = float(product["price"].replace(',', ''))
                    prices.append(price_val)
                except:
                    pass
        
        if prices:
            insights["price_analysis"] = {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "price_range": max(prices) - min(prices),
                "total_products_with_prices": len(prices)
            }
        
        # Generate simple recommendations
        insights["recommendations"] = {
            "total_products_found": len(insights["products_identified"]),
            "search_effectiveness": "good" if len(insights["products_identified"]) >= 3 else "limited",
            "data_completeness": "partial" if prices else "limited"
        }
        
        return insights
    
    async def run_demo(self):
        """Run the comprehensive e-commerce research demo"""
        print("\n" + "="*75)
        print("AI-POWERED E-COMMERCE RESEARCH - Real-World Product Comparison")
        print("="*75)
        print("This demo showcases comprehensive product research with live LLM integration")
        print("Demonstrates real-world browser automation for e-commerce analysis")
        print()
        
        # Product categories for demonstration
        product_categories = [
            "wireless bluetooth earbuds under $50",
            "gaming mouse RGB mechanical switches",
            "USB-C portable charger power bank",
            "wireless phone charger pad fast charging",
            "bluetooth keyboard mechanical compact"
        ]
        
        print("Select a product category for comprehensive research:")
        for i, category in enumerate(product_categories, 1):
            print(f"{i}. {category.title()}")
        print(f"{len(product_categories) + 1}. Custom product search")
        
        try:
            choice = input(f"\nEnter choice (1-{len(product_categories) + 1}): ").strip()
            
            if choice == str(len(product_categories) + 1):
                product_query = input("Enter product to research: ").strip()
                if not product_query:
                    product_query = product_categories[0]  # Default
            else:
                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(product_categories):
                        product_query = product_categories[choice_idx]
                    else:
                        product_query = product_categories[0]  # Default
                except ValueError:
                    product_query = product_categories[0]  # Default
            
            print(f"\nProduct Research: {product_query}")
            print("Running comprehensive e-commerce analysis with AI...")
            print("This will take 4-5 minutes for thorough multi-product comparison...")
            print()
            
            # Run the comprehensive product research
            result = await self.search_product_comparison(product_query)
            
            # Display detailed results
            print("="*75)
            print("E-COMMERCE RESEARCH RESULTS")
            print("="*75)
            
            print(f"Product Query: {result['product_query']}")
            print(f"Status: {result['status']}")
            print(f"Response Time: {result.get('response_time_ms', 0):.0f}ms")
            print(f"Success: {result.get('success', False)}")
            print(f"Platforms Searched: {', '.join(result.get('platforms_searched', []))}")
            print()
            
            if result.get('success'):
                print("COMPREHENSIVE PRODUCT ANALYSIS:")
                print("-" * 45)
                
                # Show summary preview
                summary = result.get('summary', '')
                if summary:
                    print("Research Summary (Preview):")
                    for line in summary.split('\n')[:15]:
                        if line.strip() and len(line.strip()) > 10:
                            print(f"  {line.strip()}")
                    print()
                
                # Show structured analysis if available
                analysis = result.get('product_analysis', {})
                if analysis and not analysis.get('error'):
                    products = analysis.get('products_identified', [])
                    if products:
                        print(f"PRODUCTS IDENTIFIED: {len(products)}")
                        print("-" * 30)
                        for i, product in enumerate(products[:5], 1):  # Show first 5
                            print(f"{i}. {product.get('name', 'Unknown Product')}")
                            if product.get('price'):
                                print(f"   Price: ${product['price']}")
                            if product.get('rating'):
                                print(f"   Rating: {product['rating']}/5")
                            if product.get('reviews'):
                                print(f"   Reviews: {product['reviews']}")
                        print()
                    
                    # Show price analysis
                    price_analysis = analysis.get('price_analysis', {})
                    if price_analysis:
                        print("PRICE ANALYSIS:")
                        print("-" * 20)
                        print(f"  Price Range: ${price_analysis.get('min_price', 'N/A')} - ${price_analysis.get('max_price', 'N/A')}")
                        print(f"  Average Price: ${price_analysis.get('avg_price', 0):.2f}")
                        print(f"  Products with Pricing: {price_analysis.get('total_products_with_prices', 0)}")
                        print()
                
                # Show final research URL
                if result.get('final_url'):
                    print(f"Research conducted at: {result['final_url']}")
                
                print("SUCCESS: Comprehensive e-commerce research completed!")
                print("Live LLM integration with detailed product analysis working!")
                
            else:
                print("FAILED: Could not complete the e-commerce research")
                if result.get('error'):
                    print(f"Error: {result['error']}")
            
            # Save comprehensive results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.results_dir / f"ecommerce_research_{timestamp}.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"\nComprehensive results saved to: {results_file}")
            print("="*75)
            
            return result
            
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
            return None
        except Exception as e:
            print(f"\nDemo failed: {e}")
            import traceback
            traceback.print_exc()
            return None


async def main():
    """Main entry point for e-commerce research demo"""
    try:
        demo = WindowsCompatibleEcommerceDemo()
        result = await demo.run_demo()
        
        if result and result.get('success'):
            print("\nE-COMMERCE RESEARCH DEMO COMPLETED SUCCESSFULLY!")
            print("The AI Browser v2.0.0 successfully conducted comprehensive product research!")
        else:
            print("\nE-COMMERCE RESEARCH DEMO ENCOUNTERED ISSUES:")
            print("Check the error details above and system configuration.")
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())