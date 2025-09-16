#!/usr/bin/env python3
"""
Real-World E-commerce Product Research Automation

This example demonstrates autonomous e-commerce research capabilities:
- Search multiple shopping sites (Amazon, Best Buy, Newegg)
- Compare product prices and specifications
- Extract detailed product information
- Generate comprehensive comparison reports
- Handle dynamic pricing and availability
- Use stealth to avoid detection
- Store results in memory for analysis

REQUIREMENTS:
- At least one LLM API key (OpenAI recommended)
- Working internet connection
- AI Browser v2.0.0 system components

USAGE:
    python examples/real_world_ecommerce_research.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


@dataclass
class ProductResult:
    """Structured product information"""
    name: str
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    discount: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    availability: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    specifications: Dict[str, str] = None
    url: str = ""
    source: str = ""
    extracted_at: str = ""
    
    def __post_init__(self):
        if self.specifications is None:
            self.specifications = {}
        if not self.extracted_at:
            self.extracted_at = datetime.now().isoformat()


class EcommerceResearchAgent:
    """AI-powered e-commerce research automation"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/ecommerce_research")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"ecommerce_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def search_amazon_product(self, product_query: str) -> ProductResult:
        """Search and extract product from Amazon"""
        logger.info(f"[SHOP] Searching Amazon for: {product_query}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        task = f"""
        Go to Amazon.com and search for '{product_query}'.
        Find the first relevant product and extract:
        1. Product name and title
        2. Current price and any original/discounted price
        3. Customer rating (stars) and number of reviews
        4. Availability status (in stock, out of stock, etc.)
        5. Brand and model information
        6. Key product specifications
        7. Product URL
        
        Be thorough and accurate. Handle any popups or region selections.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.amazon.com",
            headless=True,
            max_steps=15,
            timeout=90000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Extract structured data from LLM response
            extracted_data = result.get('extracted_data', {})
            summary = result.get('summary', '')
            
            # Parse the information using AI
            parse_task = f"""
            From this Amazon search result, extract product information:
            
            Summary: {summary}
            Data: {json.dumps(extracted_data, indent=2)}
            
            Extract and format as JSON:
            {{
                "name": "product name",
                "price": "current price as decimal",
                "original_price": "original price if discounted",
                "discount": "discount percentage or amount",
                "rating": "rating as decimal (1-5)",
                "reviews_count": "number of reviews as integer", 
                "availability": "availability status",
                "brand": "brand name",
                "model": "model number/name",
                "specifications": {{"key": "value"}},
                "url": "product URL"
            }}
            """
            
            # Get parsed information
            parse_config = TaskConfig(
                task=parse_task,
                url=result.get('final_url', 'https://www.amazon.com'),
                headless=True,
                max_steps=3,
                timeout=30000
            )
            
            await browser.initialize(parse_config)
            parse_result = await browser.execute_task(parse_config)
            
            # Create structured result
            product_info = self._parse_product_info(
                parse_result.get('summary', ''),
                parse_result.get('extracted_data', {}),
                'Amazon',
                result.get('final_url', '')
            )
            
            logger.info(f"[OK] Amazon product found: {product_info.name}")
            return product_info
            
        except Exception as e:
            logger.error(f"[ERROR] Amazon search failed: {e}")
            return ProductResult(
                name=f"Search failed for: {product_query}",
                source="Amazon",
                url="",
                availability="Error occurred"
            )
        finally:
            await browser.cleanup()
    
    async def search_bestbuy_product(self, product_query: str) -> ProductResult:
        """Search and extract product from Best Buy"""
        logger.info(f"[STORE] Searching Best Buy for: {product_query}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        task = f"""
        Go to BestBuy.com and search for '{product_query}'.
        Find the first relevant product and extract:
        1. Product name and full title
        2. Current price and any sale/member price
        3. Customer rating and review count
        4. Stock status and availability
        5. Brand and model information
        6. Key specifications and features
        7. Product page URL
        
        Handle any location popups or membership prompts.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.bestbuy.com",
            headless=True,
            max_steps=15,
            timeout=90000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Parse Best Buy specific information
            product_info = self._parse_product_info(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Best Buy',
                result.get('final_url', '')
            )
            
            logger.info(f"[OK] Best Buy product found: {product_info.name}")
            return product_info
            
        except Exception as e:
            logger.error(f"[ERROR] Best Buy search failed: {e}")
            return ProductResult(
                name=f"Search failed for: {product_query}",
                source="Best Buy",
                url="",
                availability="Error occurred"
            )
        finally:
            await browser.cleanup()
    
    async def search_newegg_product(self, product_query: str) -> ProductResult:
        """Search and extract product from Newegg"""
        logger.info(f"[TECH] Searching Newegg for: {product_query}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        task = f"""
        Go to Newegg.com and search for '{product_query}'.
        Find the first relevant product and extract:
        1. Product name and specifications
        2. Current price and any promotional pricing
        3. Customer ratings and review count
        4. Stock status and shipping info
        5. Brand and model details
        6. Technical specifications
        7. Product page URL
        
        Focus on technical details for electronic products.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.newegg.com",
            headless=True,
            max_steps=15,
            timeout=90000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Parse Newegg specific information
            product_info = self._parse_product_info(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Newegg',
                result.get('final_url', '')
            )
            
            logger.info(f"[OK] Newegg product found: {product_info.name}")
            return product_info
            
        except Exception as e:
            logger.error(f"[ERROR] Newegg search failed: {e}")
            return ProductResult(
                name=f"Search failed for: {product_query}",
                source="Newegg",
                url="",
                availability="Error occurred"
            )
        finally:
            await browser.cleanup()
    
    def _parse_product_info(self, summary: str, extracted_data: dict, source: str, url: str) -> ProductResult:
        """Parse product information from AI response"""
        # Try to extract price
        price = None
        original_price = None
        
        # Look for price patterns in summary
        price_patterns = [
            r'\$(\d+(?:,\d{3})*\.?\d{0,2})',
            r'(\d+(?:,\d{3})*\.?\d{0,2})\s*dollar',
            r'price[:\s]+\$?(\d+(?:,\d{3})*\.?\d{0,2})'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, summary.lower())
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    price = Decimal(price_str)
                    break
                except:
                    continue
        
        # Extract rating
        rating = None
        rating_match = re.search(r'(\d+\.?\d*)\s*(?:star|out of 5)', summary.lower())
        if rating_match:
            try:
                rating = float(rating_match.group(1))
            except:
                pass
        
        # Extract review count
        reviews_count = None
        review_patterns = [
            r'(\d+(?:,\d{3})*)\s*reviews?',
            r'(\d+(?:,\d{3})*)\s*customer',
            r'rated by (\d+(?:,\d{3})*)'
        ]
        
        for pattern in review_patterns:
            match = re.search(pattern, summary.lower())
            if match:
                try:
                    reviews_count = int(match.group(1).replace(',', ''))
                    break
                except:
                    continue
        
        # Extract product name (first meaningful line usually)
        lines = summary.split('\n')
        name = "Unknown Product"
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not line.lower().startswith(('price', 'cost', '$', 'rating')):
                name = line
                break
        
        return ProductResult(
            name=name,
            price=price,
            original_price=original_price,
            rating=rating,
            reviews_count=reviews_count,
            availability="Available" if price else "Unknown",
            source=source,
            url=url,
            specifications=extracted_data if isinstance(extracted_data, dict) else {}
        )
    
    async def compare_products(self, products: List[ProductResult]) -> Dict[str, Any]:
        """Generate comprehensive product comparison using AI"""
        logger.info("[ANALYSIS] Generating product comparison analysis...")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Prepare product data for AI analysis
        products_data = []
        for product in products:
            if product.name != "Unknown Product" and not product.name.startswith("Search failed"):
                products_data.append(asdict(product))
        
        if not products_data:
            return {"error": "No valid products found for comparison"}
        
        task = f"""
        Analyze these e-commerce product listings and provide a comprehensive comparison:
        
        {json.dumps(products_data, indent=2, default=str)}
        
        Provide analysis including:
        1. Price comparison - identify best value, lowest price, highest price
        2. Rating and review analysis - which has best customer satisfaction
        3. Availability and stock status summary
        4. Feature and specification comparison
        5. Recommendation based on different criteria (budget, quality, features)
        6. Market insights and pricing trends
        7. Potential savings and deals identified
        
        Format as a detailed report with clear sections and recommendations.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.example.com",  # Static page for analysis
            headless=True,
            max_steps=5,
            timeout=60000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Extract the analysis
            analysis = {
                "total_products_analyzed": len(products_data),
                "analysis_summary": result.get('summary', ''),
                "detailed_comparison": result.get('extracted_data', {}),
                "generated_at": datetime.now().isoformat(),
                "products_included": [p['name'] for p in products_data]
            }
            
            # Add price statistics
            prices = [float(p['price']) for p in products_data if p.get('price') and p['price'] is not None]
            if prices:
                analysis["price_statistics"] = {
                    "lowest_price": min(prices),
                    "highest_price": max(prices),
                    "average_price": sum(prices) / len(prices),
                    "price_range": max(prices) - min(prices)
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"[ERROR] Comparison analysis failed: {e}")
            return {"error": str(e)}
        finally:
            await browser.cleanup()
    
    async def research_product_category(self, product_query: str) -> Dict[str, Any]:
        """Comprehensive research across multiple e-commerce sites"""
        logger.info(f"[SEARCH] Starting comprehensive research for: {product_query}")
        
        # Search all platforms concurrently for better performance
        search_tasks = [
            self.search_amazon_product(product_query),
            self.search_bestbuy_product(product_query),
            self.search_newegg_product(product_query)
        ]
        
        # Execute searches with timeout protection
        try:
            products = await asyncio.wait_for(
                asyncio.gather(*search_tasks, return_exceptions=True),
                timeout=300  # 5 minute total timeout
            )
            
            # Filter out exceptions
            valid_products = []
            for product in products:
                if isinstance(product, ProductResult):
                    valid_products.append(product)
                elif isinstance(product, Exception):
                    logger.error(f"Search error: {product}")
            
            logger.info(f"[OK] Found {len(valid_products)} products across platforms")
            
            # Generate comparison analysis
            comparison = await self.compare_products(valid_products)
            
            # Compile comprehensive results
            research_results = {
                "query": product_query,
                "search_timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "products_found": [asdict(p) for p in valid_products],
                "comparison_analysis": comparison,
                "platforms_searched": ["Amazon", "Best Buy", "Newegg"],
                "success_rate": len(valid_products) / 3,
                "recommendations": self._generate_recommendations(valid_products)
            }
            
            # Save results
            await self._save_research_results(research_results)
            
            return research_results
            
        except asyncio.TimeoutError:
            logger.error("[ERROR] Research timed out after 5 minutes")
            return {"error": "Research timed out", "query": product_query}
        except Exception as e:
            logger.error(f"[ERROR] Research failed: {e}")
            return {"error": str(e), "query": product_query}
    
    def _generate_recommendations(self, products: List[ProductResult]) -> Dict[str, Any]:
        """Generate buying recommendations"""
        recommendations = {
            "best_value": None,
            "lowest_price": None,
            "highest_rated": None,
            "most_reviewed": None
        }
        
        valid_products = [p for p in products 
                         if p.name != "Unknown Product" and not p.name.startswith("Search failed")]
        
        if not valid_products:
            return recommendations
        
        # Find best value (price vs rating)
        value_scores = []
        for product in valid_products:
            if product.price and product.rating:
                value_score = float(product.rating) / float(product.price) * 100
                value_scores.append((value_score, product))
        
        if value_scores:
            recommendations["best_value"] = asdict(max(value_scores, key=lambda x: x[0])[1])
        
        # Find lowest price
        priced_products = [p for p in valid_products if p.price]
        if priced_products:
            recommendations["lowest_price"] = asdict(min(priced_products, key=lambda x: x.price))
        
        # Find highest rated
        rated_products = [p for p in valid_products if p.rating]
        if rated_products:
            recommendations["highest_rated"] = asdict(max(rated_products, key=lambda x: x.rating))
        
        # Find most reviewed
        reviewed_products = [p for p in valid_products if p.reviews_count]
        if reviewed_products:
            recommendations["most_reviewed"] = asdict(max(reviewed_products, key=lambda x: x.reviews_count))
        
        return recommendations
    
    async def _save_research_results(self, results: Dict[str, Any]):
        """Save research results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = self.results_dir / f"ecommerce_research_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        
        # Save human-readable report
        report_file = self.results_dir / f"ecommerce_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"E-COMMERCE RESEARCH REPORT\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"Product Query: {results['query']}\n")
            f.write(f"Research Date: {results['search_timestamp']}\n")
            f.write(f"Success Rate: {results['success_rate']:.1%}\n\n")
            
            f.write(f"PRODUCTS FOUND:\n")
            f.write(f"-" * 30 + "\n")
            for product in results['products_found']:
                f.write(f"\nProduct: {product['name']}\n")
                f.write(f"Source: {product['source']}\n")
                if product['price']:
                    f.write(f"Price: ${product['price']}\n")
                if product['rating']:
                    f.write(f"Rating: {product['rating']}/5\n")
                if product['reviews_count']:
                    f.write(f"Reviews: {product['reviews_count']}\n")
                f.write(f"Available: {product['availability']}\n")
                f.write(f"URL: {product['url']}\n")
            
            if results['comparison_analysis'].get('analysis_summary'):
                f.write(f"\nCOMPARISON ANALYSIS:\n")
                f.write(f"-" * 30 + "\n")
                f.write(results['comparison_analysis']['analysis_summary'])
        
        logger.info(f"[FILE] Research saved to: {json_file}")
        logger.info(f"[FILE] Report saved to: {report_file}")


async def demo_ecommerce_research():
    """Demonstrate e-commerce research capabilities"""
    print("\n" + "="*70)
    print("[SHOP] AI-POWERED E-COMMERCE RESEARCH DEMONSTRATION")
    print("="*70)
    print("This demo will search multiple shopping sites and compare products")
    print("using AI reasoning and real browser automation.\n")
    
    agent = EcommerceResearchAgent()
    
    # Example products to research
    research_queries = [
        "wireless bluetooth headphones",
        "gaming mechanical keyboard",
        "4K webcam for streaming"
    ]
    
    print("Select a product category to research:")
    for i, query in enumerate(research_queries, 1):
        print(f"{i}. {query.title()}")
    print(f"{len(research_queries) + 1}. Custom product search")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == str(len(research_queries) + 1):
            query = input("Enter product to research: ").strip()
            if not query:
                query = research_queries[0]  # Default fallback
        else:
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(research_queries):
                    query = research_queries[choice_idx]
                else:
                    query = research_queries[0]  # Default fallback
            except ValueError:
                query = research_queries[0]  # Default fallback
        
        print(f"\n[SEARCH] Researching: {query}")
        print("This may take 3-5 minutes as we search multiple sites...\n")
        
        # Run the research
        results = await agent.research_product_category(query)
        
        # Display results
        if "error" in results:
            print(f"[ERROR] Research failed: {results['error']}")
            return
        
        print("\n" + "="*50)
        print("[RESULTS] RESEARCH RESULTS SUMMARY")
        print("="*50)
        
        print(f"Query: {results['query']}")
        print(f"Products Found: {len(results['products_found'])}")
        print(f"Success Rate: {results['success_rate']:.1%}")
        print(f"Platforms Searched: {', '.join(results['platforms_searched'])}")
        
        # Show product summary
        print(f"\n[PRODUCTS] PRODUCTS FOUND:")
        print("-" * 30)
        for product in results['products_found']:
            print(f"\n* {product['name']}")
            print(f"  Source: {product['source']}")
            if product['price']:
                print(f"  Price: ${product['price']}")
            if product['rating']:
                print(f"  Rating: {product['rating']}/5")
            if product['reviews_count']:
                print(f"  Reviews: {product['reviews_count']:,}")
            print(f"  Status: {product['availability']}")
        
        # Show price comparison if available
        if results['comparison_analysis'].get('price_statistics'):
            stats = results['comparison_analysis']['price_statistics']
            print(f"\n[PRICE] PRICE ANALYSIS:")
            print("-" * 30)
            print(f"Lowest Price: ${stats['lowest_price']:.2f}")
            print(f"Highest Price: ${stats['highest_price']:.2f}")
            print(f"Average Price: ${stats['average_price']:.2f}")
            print(f"Price Range: ${stats['price_range']:.2f}")
        
        # Show recommendations
        recommendations = results.get('recommendations', {})
        if any(recommendations.values()):
            print(f"\n[RECOMMEND] RECOMMENDATIONS:")
            print("-" * 30)
            if recommendations.get('best_value'):
                print(f"Best Value: {recommendations['best_value']['name']}")
            if recommendations.get('lowest_price'):
                print(f"Lowest Price: {recommendations['lowest_price']['name']}")
            if recommendations.get('highest_rated'):
                print(f"Highest Rated: {recommendations['highest_rated']['name']}")
        
        # Show AI analysis summary
        if results['comparison_analysis'].get('analysis_summary'):
            print(f"\n[AI] AI ANALYSIS:")
            print("-" * 30)
            analysis = results['comparison_analysis']['analysis_summary']
            # Show first few lines of analysis
            for line in analysis.split('\n')[:5]:
                if line.strip():
                    print(f"  {line.strip()}")
            if len(analysis.split('\n')) > 5:
                print("  ... (see full report in output files)")
        
        print(f"\n[REPORT] Detailed results saved to: examples/outputs/ecommerce_research/")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[ERROR] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")


def main():
    """Main entry point"""
    try:
        asyncio.run(demo_ecommerce_research())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")


if __name__ == "__main__":
    main()