#!/usr/bin/env python3
"""
Real-World Real Estate Market Research Automation

This example demonstrates autonomous real estate market analysis:
- Search property listing sites (Zillow, Realtor.com, Redfin)
- Extract property details, prices, and market data
- Analyze market trends and pricing patterns
- Generate investment insights and recommendations
- Track property value changes over time
- Compare neighborhoods and market segments
- Create comprehensive market reports

REQUIREMENTS:
- At least one LLM API key (OpenAI recommended for market analysis)
- Working internet connection
- AI Browser v2.0.0 system components

USAGE:
    python examples/real_world_real_estate_research.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re
from statistics import mean, median

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


@dataclass
class PropertyListing:
    """Structured property listing data"""
    address: str
    city: str
    state: str
    zip_code: str
    price: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    lot_size: Optional[str] = None
    property_type: str = "Single Family"  # Single Family, Condo, Townhouse, etc.
    year_built: Optional[int] = None
    days_on_market: Optional[int] = None
    price_per_sqft: Optional[float] = None
    hoa_fees: Optional[int] = None
    property_tax: Optional[int] = None
    listing_url: str = ""
    source: str = ""
    listing_agent: Optional[str] = None
    listing_date: Optional[str] = None
    last_sold_price: Optional[int] = None
    last_sold_date: Optional[str] = None
    zestimate: Optional[int] = None  # Zillow estimate
    neighborhood: Optional[str] = None
    school_rating: Optional[int] = None
    walkability_score: Optional[int] = None
    features: List[str] = None
    description: str = ""
    extracted_at: str = ""
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if not self.extracted_at:
            self.extracted_at = datetime.now().isoformat()
        
        # Calculate price per sqft if not provided
        if self.price and self.square_feet and not self.price_per_sqft:
            self.price_per_sqft = round(self.price / self.square_feet, 2)


@dataclass
class MarketAnalysis:
    """Market analysis results for an area"""
    location: str
    median_price: float
    average_price: float
    price_range: Dict[str, int]  # min, max
    median_sqft: Optional[float] = None
    median_price_per_sqft: Optional[float] = None
    median_days_on_market: Optional[float] = None
    property_type_distribution: Dict[str, int] = None
    price_trends: Optional[str] = None
    market_insights: str = ""
    total_properties_analyzed: int = 0
    analysis_date: str = ""
    
    def __post_init__(self):
        if self.property_type_distribution is None:
            self.property_type_distribution = {}
        if not self.analysis_date:
            self.analysis_date = datetime.now().isoformat()


class RealEstateAnalyzer:
    """AI-powered real estate market research and analysis"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/real_estate_research")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"real_estate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def search_zillow_listings(self, location: str, max_listings: int = 10) -> List[PropertyListing]:
        """Search property listings on Zillow"""
        logger.info(f"[HOME] Searching Zillow for properties in: {location}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Construct Zillow search URL
        search_url = f"https://www.zillow.com/homes/{location.replace(' ', '-').replace(',', '')}_rb/"
        
        task = f"""
        Go to Zillow and search for properties in '{location}'.
        Find {max_listings} property listings and extract for each:
        
        1. Full property address
        2. Listing price
        3. Number of bedrooms and bathrooms
        4. Square footage
        5. Lot size if available
        6. Property type (house, condo, townhouse)
        7. Year built
        8. Days on market
        9. Price per square foot
        10. HOA fees if applicable
        11. Property taxes
        12. Zestimate value
        13. Listing agent name
        14. Property features and amenities
        15. Direct listing URL
        
        Handle any location prompts or registration requests by dismissing them.
        Focus on active listings (for sale properties).
        Extract complete and accurate data for market analysis.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=True,
            max_steps=20,
            timeout=120000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Parse Zillow listings
            properties = await self._parse_property_listings(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Zillow',
                location
            )
            
            logger.info(f"[SUCCESS] Found {len(properties)} Zillow listings")
            return properties
            
        except Exception as e:
            logger.error(f"[ERROR] Zillow search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def search_realtor_listings(self, location: str, max_listings: int = 10) -> List[PropertyListing]:
        """Search property listings on Realtor.com"""
        logger.info(f"[OFFICE] Searching Realtor.com for properties in: {location}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        search_url = f"https://www.realtor.com/realestateandhomes-search/{location.replace(' ', '-').replace(',', '')}"
        
        task = f"""
        Go to Realtor.com and search for properties in '{location}'.
        Extract data from {max_listings} property listings:
        
        1. Property address and location details
        2. Listed price
        3. Bedrooms, bathrooms, square footage
        4. Lot size and property details
        5. Property type and style
        6. Year built and age
        7. Time on market
        8. Price per square foot
        9. Monthly costs (taxes, HOA)
        10. Listing agent information
        11. Property description and features
        12. School ratings if shown
        13. Neighborhood information
        14. Direct property URL
        
        Look for MLS listings and detailed property information.
        Handle any user interface prompts appropriately.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=True,
            max_steps=20,
            timeout=120000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            properties = await self._parse_property_listings(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Realtor.com',
                location
            )
            
            logger.info(f"[SUCCESS] Found {len(properties)} Realtor.com listings")
            return properties
            
        except Exception as e:
            logger.error(f"[ERROR] Realtor.com search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def search_redfin_listings(self, location: str, max_listings: int = 10) -> List[PropertyListing]:
        """Search property listings on Redfin"""
        logger.info(f"[NEIGHBORHOOD] Searching Redfin for properties in: {location}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        search_url = f"https://www.redfin.com/city/{location.replace(' ', '-').replace(',', '')}"
        
        task = f"""
        Go to Redfin and search for properties in '{location}'.
        Extract information from {max_listings} listings:
        
        1. Full address and location
        2. Current listing price
        3. Bedroom and bathroom count
        4. Total square footage
        5. Lot size and details
        6. Property type
        7. Construction year
        8. Days on Redfin/market
        9. Price per square foot
        10. Property taxes and fees
        11. Last sold price and date
        12. Redfin Estimate if available
        13. Walkability and transit scores
        14. Property features and upgrades
        15. Listing details URL
        
        Redfin often has detailed market data - extract comprehensively.
        Look for historical pricing and market trends.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=True,
            max_steps=20,
            timeout=120000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            properties = await self._parse_property_listings(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Redfin',
                location
            )
            
            logger.info(f"[SUCCESS] Found {len(properties)} Redfin listings")
            return properties
            
        except Exception as e:
            logger.error(f"[ERROR] Redfin search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def _parse_property_listings(self, summary: str, extracted_data: dict, source: str, location: str) -> List[PropertyListing]:
        """Parse property listings from AI extraction"""
        browser = AIBrowser({"log_level": "INFO"})
        
        parsing_task = f"""
        Parse these property listings from {source} and structure the data:
        
        Raw Data: {summary}
        Additional Data: {json.dumps(extracted_data, default=str)}
        
        Extract individual property listings with:
        1. Complete address (street, city, state, zip)
        2. Listing price (as integer)
        3. Bedrooms (as integer)
        4. Bathrooms (as decimal)
        5. Square footage (as integer)
        6. Property type
        7. Year built
        8. Days on market
        9. Any additional property details
        
        Format as structured data for each property found.
        Be thorough and accurate with numeric data.
        """
        
        config = TaskConfig(
            task=parsing_task,
            url="https://www.example.com",
            headless=True,
            max_steps=5,
            timeout=60000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            parsed_summary = result.get('summary', '')
            properties = []
            
            # Split content into property listings
            property_sections = self._split_property_content(parsed_summary)
            
            for i, section in enumerate(property_sections[:10]):  # Limit to 10 properties
                property_obj = await self._create_property_object(section, source, location, i+1)
                if property_obj and property_obj.price and property_obj.price > 10000:  # Valid listing
                    properties.append(property_obj)
            
            return properties
            
        except Exception as e:
            logger.error(f"Failed to parse property listings: {e}")
            return []
        finally:
            await browser.cleanup()
    
    def _split_property_content(self, content: str) -> List[str]:
        """Split content into individual property listings"""
        # Strategy 1: Numbered properties
        if re.search(r'\n\d+\.', content):
            sections = re.split(r'\n(?=\d+\.)', content)
            return [s.strip() for s in sections if len(s.strip()) > 50]
        
        # Strategy 2: Property indicators
        property_indicators = ['Property:', 'Address:', 'Price:', '$']
        for indicator in property_indicators:
            if indicator in content:
                sections = content.split('\n\n')
                return [s.strip() for s in sections if indicator in s and len(s.strip()) > 50]
        
        # Strategy 3: Double newlines
        sections = content.split('\n\n')
        return [s.strip() for s in sections if len(s.strip()) > 60]
    
    async def _create_property_object(self, property_text: str, source: str, location: str, prop_num: int) -> Optional[PropertyListing]:
        """Create structured property object from text"""
        try:
            # Parse location components
            location_parts = location.split(',')
            default_city = location_parts[0].strip() if location_parts else "Unknown"
            default_state = location_parts[1].strip() if len(location_parts) > 1 else "Unknown"
            
            # Extract address
            address = "Unknown Address"
            address_patterns = [
                r'Address:\s*([^\n]+)',
                r'Property:\s*([^\n]+)',
                r'(\d+\s+[^\n,]+(?:St|Ave|Rd|Dr|Ln|Blvd|Way|Ct)[^\n,]*)'
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, property_text, re.IGNORECASE)
                if match:
                    address = match.group(1).strip()
                    break
            
            # Extract price
            price = None
            price_patterns = [
                r'Price:\s*\$?(\d{1,3}(?:,\d{3})*)',
                r'\$(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3}(?:,\d{3})*)\s*dollars?'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, property_text, re.IGNORECASE)
                if match:
                    try:
                        price = int(match.group(1).replace(',', ''))
                        break
                    except ValueError:
                        continue
            
            # Extract bedrooms
            bedrooms = None
            bed_patterns = [
                r'(\d+)\s*bed(?:room)?s?',
                r'Bedroom[s]?:\s*(\d+)',
                r'BR:\s*(\d+)'
            ]
            
            for pattern in bed_patterns:
                match = re.search(pattern, property_text, re.IGNORECASE)
                if match:
                    try:
                        bedrooms = int(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Extract bathrooms
            bathrooms = None
            bath_patterns = [
                r'(\d+(?:\.\d+)?)\s*bath(?:room)?s?',
                r'Bathroom[s]?:\s*(\d+(?:\.\d+)?)',
                r'BA:\s*(\d+(?:\.\d+)?)'
            ]
            
            for pattern in bath_patterns:
                match = re.search(pattern, property_text, re.IGNORECASE)
                if match:
                    try:
                        bathrooms = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Extract square footage
            square_feet = None
            sqft_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft\.?|sqft|square feet)',
                r'Square (?:feet|footage):\s*(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3}(?:,\d{3})*)\s*SF'
            ]
            
            for pattern in sqft_patterns:
                match = re.search(pattern, property_text, re.IGNORECASE)
                if match:
                    try:
                        square_feet = int(match.group(1).replace(',', ''))
                        break
                    except ValueError:
                        continue
            
            # Extract property type
            property_type = "Single Family"
            type_patterns = [
                r'Type:\s*([^\n]+)',
                r'Property Type:\s*([^\n]+)',
                r'(Condo|Townhouse|Single Family|Multi-Family|Apartment)'
            ]
            
            for pattern in type_patterns:
                match = re.search(pattern, property_text, re.IGNORECASE)
                if match:
                    property_type = match.group(1).strip()
                    break
            
            # Extract year built
            year_built = None
            year_patterns = [
                r'Built:?\s*(\d{4})',
                r'Year Built:?\s*(\d{4})',
                r'(\d{4})\s*built'
            ]
            
            for pattern in year_patterns:
                match = re.search(pattern, property_text, re.IGNORECASE)
                if match:
                    try:
                        year = int(match.group(1))
                        if 1800 <= year <= datetime.now().year:
                            year_built = year
                            break
                    except ValueError:
                        continue
            
            # Extract days on market
            days_on_market = None
            dom_patterns = [
                r'(\d+)\s*days? on market',
                r'DOM:?\s*(\d+)',
                r'Listed (\d+) days ago'
            ]
            
            for pattern in dom_patterns:
                match = re.search(pattern, property_text, re.IGNORECASE)
                if match:
                    try:
                        days_on_market = int(match.group(1))
                        break
                    except ValueError:
                        continue
            
            return PropertyListing(
                address=address,
                city=default_city,
                state=default_state,
                zip_code="",  # Would need more sophisticated parsing
                price=price,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                square_feet=square_feet,
                property_type=property_type,
                year_built=year_built,
                days_on_market=days_on_market,
                listing_url=f"{source.lower().replace('.', '')}/listing/{prop_num}",
                source=source,
                description=property_text[:300]  # First 300 chars
            )
            
        except Exception as e:
            logger.error(f"Failed to create property object: {e}")
            return None
    
    def _calculate_market_statistics(self, properties: List[PropertyListing]) -> MarketAnalysis:
        """Calculate market statistics from property listings"""
        if not properties:
            return MarketAnalysis(location="Unknown", median_price=0, average_price=0, price_range={"min": 0, "max": 0})
        
        # Filter valid properties with prices
        valid_properties = [p for p in properties if p.price and p.price > 0]
        
        if not valid_properties:
            return MarketAnalysis(location="Unknown", median_price=0, average_price=0, price_range={"min": 0, "max": 0})
        
        # Price statistics
        prices = [p.price for p in valid_properties]
        median_price = median(prices)
        average_price = mean(prices)
        price_range = {"min": min(prices), "max": max(prices)}
        
        # Square footage statistics
        sqft_properties = [p for p in valid_properties if p.square_feet and p.square_feet > 0]
        median_sqft = median([p.square_feet for p in sqft_properties]) if sqft_properties else None
        
        # Price per sqft statistics
        price_per_sqft_values = [p.price_per_sqft for p in valid_properties if p.price_per_sqft]
        median_price_per_sqft = median(price_per_sqft_values) if price_per_sqft_values else None
        
        # Days on market statistics
        dom_properties = [p for p in valid_properties if p.days_on_market]
        median_days_on_market = median([p.days_on_market for p in dom_properties]) if dom_properties else None
        
        # Property type distribution
        property_type_dist = {}
        for prop in valid_properties:
            prop_type = prop.property_type or "Unknown"
            property_type_dist[prop_type] = property_type_dist.get(prop_type, 0) + 1
        
        # Determine location from first property
        location = f"{valid_properties[0].city}, {valid_properties[0].state}" if valid_properties else "Unknown"
        
        return MarketAnalysis(
            location=location,
            median_price=median_price,
            average_price=average_price,
            price_range=price_range,
            median_sqft=median_sqft,
            median_price_per_sqft=median_price_per_sqft,
            median_days_on_market=median_days_on_market,
            property_type_distribution=property_type_dist,
            total_properties_analyzed=len(valid_properties)
        )
    
    async def generate_market_insights(self, properties: List[PropertyListing], market_stats: MarketAnalysis) -> Dict[str, Any]:
        """Generate AI-powered market insights and recommendations"""
        logger.info("[STATS] Generating market insights and investment analysis...")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Prepare market data for AI analysis
        market_data = {
            "location": market_stats.location,
            "total_properties": market_stats.total_properties_analyzed,
            "median_price": market_stats.median_price,
            "average_price": market_stats.average_price,
            "price_range": market_stats.price_range,
            "median_sqft": market_stats.median_sqft,
            "median_price_per_sqft": market_stats.median_price_per_sqft,
            "median_days_on_market": market_stats.median_days_on_market,
            "property_types": market_stats.property_type_distribution
        }
        
        # Sample properties for detailed analysis
        sample_properties = [
            {
                "address": p.address,
                "price": p.price,
                "bedrooms": p.bedrooms,
                "bathrooms": p.bathrooms,
                "sqft": p.square_feet,
                "price_per_sqft": p.price_per_sqft,
                "year_built": p.year_built,
                "days_on_market": p.days_on_market,
                "property_type": p.property_type
            }
            for p in properties[:5] if p.price  # Top 5 with prices
        ]
        
        insights_task = f"""
        Analyze this real estate market data and provide comprehensive insights:
        
        Market Statistics: {json.dumps(market_data, default=str, indent=2)}
        Sample Properties: {json.dumps(sample_properties, default=str, indent=2)}
        
        Provide detailed analysis including:
        1. Market Overview - current state and key characteristics
        2. Price Analysis - affordability, trends, value assessment
        3. Property Type Insights - what's available and popular
        4. Investment Potential - opportunities and risks
        5. Market Velocity - how quickly properties sell
        6. Comparative Analysis - vs regional/national averages
        7. Buyer/Investor Recommendations - actionable advice
        8. Market Outlook - future predictions and factors to watch
        
        Format as a comprehensive real estate market report suitable for investors or homebuyers.
        Include specific metrics and data-driven recommendations.
        """
        
        config = TaskConfig(
            task=insights_task,
            url="https://www.example.com",
            headless=True,
            max_steps=8,
            timeout=90000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            insights = {
                "ai_analysis": result.get('summary', ''),
                "market_insights": result.get('extracted_data', {}),
                "key_metrics": market_data,
                "investment_score": self._calculate_investment_score(market_stats),
                "market_trends": self._identify_market_trends(properties),
                "recommendations": self._extract_recommendations(result.get('summary', '')),
                "generated_at": datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate market insights: {e}")
            return {"error": str(e)}
        finally:
            await browser.cleanup()
    
    def _calculate_investment_score(self, market_stats: MarketAnalysis) -> Dict[str, Any]:
        """Calculate investment attractiveness score"""
        score = 50  # Base score
        factors = []
        
        # Price per sqft factor
        if market_stats.median_price_per_sqft:
            if market_stats.median_price_per_sqft < 150:
                score += 10
                factors.append("Affordable price per sqft")
            elif market_stats.median_price_per_sqft > 300:
                score -= 5
                factors.append("High price per sqft")
        
        # Days on market factor
        if market_stats.median_days_on_market:
            if market_stats.median_days_on_market < 30:
                score += 15
                factors.append("Fast-moving market")
            elif market_stats.median_days_on_market > 90:
                score -= 10
                factors.append("Slow market velocity")
        
        # Property type diversity
        if len(market_stats.property_type_distribution) > 2:
            score += 5
            factors.append("Diverse property types available")
        
        # Market size
        if market_stats.total_properties_analyzed > 5:
            score += 5
            factors.append("Good market liquidity")
        
        investment_score = max(0, min(100, score))  # Clamp to 0-100
        
        return {
            "score": investment_score,
            "rating": "Excellent" if investment_score >= 80 else 
                     "Good" if investment_score >= 65 else
                     "Fair" if investment_score >= 50 else "Poor",
            "factors": factors
        }
    
    def _identify_market_trends(self, properties: List[PropertyListing]) -> Dict[str, Any]:
        """Identify key market trends from property data"""
        trends = {}
        
        # Age of inventory trend
        properties_with_year = [p for p in properties if p.year_built]
        if properties_with_year:
            current_year = datetime.now().year
            avg_age = current_year - mean([p.year_built for p in properties_with_year])
            trends["average_property_age"] = round(avg_age, 1)
            
            if avg_age < 10:
                trends["inventory_age_trend"] = "New construction market"
            elif avg_age > 40:
                trends["inventory_age_trend"] = "Mature/established market"
            else:
                trends["inventory_age_trend"] = "Mixed age inventory"
        
        # Price distribution
        priced_properties = [p for p in properties if p.price]
        if priced_properties:
            prices = [p.price for p in priced_properties]
            q1 = sorted(prices)[len(prices)//4]
            q3 = sorted(prices)[3*len(prices)//4]
            trends["price_quartiles"] = {"Q1": q1, "Q3": q3, "range": q3-q1}
        
        return trends
    
    def _extract_recommendations(self, ai_text: str) -> List[str]:
        """Extract recommendations from AI analysis"""
        recommendations = []
        
        # Look for recommendation patterns
        rec_patterns = [
            r'recommend(?:ation)?[s]?:\s*([^\n.]+)',
            r'suggest[s]?:\s*([^\n.]+)',
            r'advice:\s*([^\n.]+)',
            r'should\s+([^\n.]+)'
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, ai_text, re.IGNORECASE)
            recommendations.extend([rec.strip() for rec in matches])
        
        return recommendations[:5]  # Top 5 recommendations
    
    async def comprehensive_market_research(self, location: str) -> Dict[str, Any]:
        """Run comprehensive real estate market research"""
        logger.info(f"[NEIGHBORHOOD] Starting comprehensive real estate research for: {location}")
        
        all_properties = []
        source_results = {}
        
        # Search multiple platforms
        search_tasks = [
            ("Zillow", self.search_zillow_listings(location, 8)),
            ("Realtor.com", self.search_realtor_listings(location, 8)),
            ("Redfin", self.search_redfin_listings(location, 8))
        ]
        
        for source_name, task in search_tasks:
            try:
                properties = await task
                all_properties.extend(properties)
                source_results[source_name] = len(properties)
                logger.info(f"[SUCCESS] {source_name}: {len(properties)} properties")
                
                # Small delay between sources
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"[ERROR] {source_name} search failed: {e}")
                source_results[source_name] = 0
        
        # Remove duplicates based on address similarity
        unique_properties = self._deduplicate_properties(all_properties)
        
        # Calculate market statistics
        market_analysis = self._calculate_market_statistics(unique_properties)
        
        # Generate AI insights
        ai_insights = await self.generate_market_insights(unique_properties, market_analysis)
        
        # Compile comprehensive results
        research_results = {
            "location": location,
            "research_timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "source_results": source_results,
            "total_properties_found": len(all_properties),
            "unique_properties": len(unique_properties),
            "market_analysis": asdict(market_analysis),
            "ai_insights": ai_insights,
            "property_listings": [asdict(p) for p in unique_properties],
            "research_summary": self._create_research_summary(market_analysis, ai_insights, source_results)
        }
        
        # Save results
        await self._save_research_results(research_results)
        
        return research_results
    
    def _deduplicate_properties(self, properties: List[PropertyListing]) -> List[PropertyListing]:
        """Remove duplicate properties based on address similarity"""
        unique_properties = []
        seen_addresses = set()
        
        for prop in properties:
            # Normalize address for comparison
            normalized_addr = re.sub(r'[^\w\s]', '', prop.address.lower()).strip()
            addr_words = set(normalized_addr.split())
            
            # Check for duplicates
            is_duplicate = False
            for seen_addr in seen_addresses:
                seen_words = set(seen_addr.split())
                if addr_words and seen_words:
                    overlap = len(addr_words.intersection(seen_words))
                    similarity = overlap / min(len(addr_words), len(seen_words))
                    
                    if similarity > 0.8:  # 80% word overlap
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_properties.append(prop)
                seen_addresses.add(normalized_addr)
        
        return unique_properties
    
    def _create_research_summary(self, market_analysis: MarketAnalysis, ai_insights: Dict[str, Any], source_results: Dict[str, int]) -> str:
        """Create executive summary of research findings"""
        summary_lines = [
            f"Real Estate Market Research Summary for {market_analysis.location}",
            f"Analysis Date: {market_analysis.analysis_date}",
            f"Properties Analyzed: {market_analysis.total_properties_analyzed}",
            f"",
            f"Key Market Metrics:",
            f"- Median Price: ${market_analysis.median_price:,.0f}",
            f"- Average Price: ${market_analysis.average_price:,.0f}",
            f"- Price Range: ${market_analysis.price_range['min']:,.0f} - ${market_analysis.price_range['max']:,.0f}"
        ]
        
        if market_analysis.median_price_per_sqft:
            summary_lines.append(f"- Median Price/SqFt: ${market_analysis.median_price_per_sqft:.0f}")
        
        if market_analysis.median_days_on_market:
            summary_lines.append(f"- Median Days on Market: {market_analysis.median_days_on_market:.0f}")
        
        if ai_insights.get("investment_score"):
            score = ai_insights["investment_score"]
            summary_lines.extend([
                f"",
                f"Investment Score: {score['score']}/100 ({score['rating']})"
            ])
        
        return "\n".join(summary_lines)
    
    async def _save_research_results(self, results: Dict[str, Any]):
        """Save real estate research results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"real_estate_research_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        
        # Save executive report
        report_file = self.results_dir / f"real_estate_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("REAL ESTATE MARKET RESEARCH REPORT\n")
            f.write("="*50 + "\n\n")
            f.write(results['research_summary'])
            f.write("\n\n")
            
            # Source breakdown
            f.write("DATA SOURCES:\n")
            f.write("-" * 20 + "\n")
            for source, count in results['source_results'].items():
                f.write(f"{source}: {count} properties\n")
            f.write("\n")
            
            # Market analysis
            market = results['market_analysis']
            f.write("MARKET ANALYSIS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Property Type Distribution:\n")
            for prop_type, count in market.get('property_type_distribution', {}).items():
                f.write(f"  {prop_type}: {count} properties\n")
            f.write("\n")
            
            # Top properties
            f.write("SAMPLE PROPERTY LISTINGS:\n")
            f.write("-" * 30 + "\n")
            for i, prop in enumerate(results['property_listings'][:5], 1):
                f.write(f"{i}. {prop['address']}\n")
                f.write(f"   Price: ${prop['price']:,} | {prop['bedrooms']}BR/{prop['bathrooms']}BA\n")
                if prop['square_feet']:
                    f.write(f"   Size: {prop['square_feet']:,} sqft")
                    if prop['price_per_sqft']:
                        f.write(f" (${prop['price_per_sqft']:.0f}/sqft)")
                    f.write("\n")
                f.write(f"   Source: {prop['source']}\n\n")
            
            # AI insights preview
            if results['ai_insights'].get('ai_analysis'):
                f.write("AI MARKET INSIGHTS:\n")
                f.write("-" * 20 + "\n")
                analysis = results['ai_insights']['ai_analysis'][:1000]
                f.write(analysis)
                f.write("...\n")
        
        logger.info(f"[FILE] Research results saved to: {json_file}")
        logger.info(f"[FILE] Executive report saved to: {report_file}")


async def demo_real_estate_research():
    """Demonstrate real estate research capabilities"""
    print("\n" + "="*70)
    print("[NEIGHBORHOOD] AI-POWERED REAL ESTATE MARKET RESEARCH")
    print("="*70)
    print("This demo analyzes real estate markets using AI reasoning and")
    print("real browser automation across multiple property sites.\n")
    
    analyzer = RealEstateAnalyzer()
    
    # Example locations for research
    sample_locations = [
        "Austin, TX",
        "Seattle, WA", 
        "Denver, CO",
        "Atlanta, GA",
        "Phoenix, AZ"
    ]
    
    print("Select a location to research:")
    for i, location in enumerate(sample_locations, 1):
        print(f"{i}. {location}")
    print(f"{len(sample_locations) + 1}. Custom location")
    
    try:
        choice = input(f"\nEnter choice (1-{len(sample_locations) + 1}): ").strip()
        
        if choice == str(len(sample_locations) + 1):
            location = input("Enter city, state: ").strip()
            if not location:
                location = sample_locations[0]  # Default
        else:
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(sample_locations):
                    location = sample_locations[choice_idx]
                else:
                    location = sample_locations[0]  # Default
            except ValueError:
                location = sample_locations[0]  # Default
        
        print(f"\n[HOME] Researching real estate market in: {location}")
        print("[SEARCH] Sources: Zillow, Realtor.com, Redfin")
        print("[TIME]  This may take 8-12 minutes to analyze all sources...\n")
        
        # Run comprehensive research
        results = await analyzer.comprehensive_market_research(location)
        
        if "error" in results:
            print(f"[ERROR] Research failed: {results['error']}")
            return
        
        # Display results
        print("\n" + "="*50)
        print("[STATS] REAL ESTATE MARKET ANALYSIS")
        print("="*50)
        
        print(f"Location: {results['location']}")
        print(f"Properties Found: {results['total_properties_found']}")
        print(f"Unique Properties: {results['unique_properties']}")
        
        # Source breakdown
        print(f"\n[OFFICE] SOURCE BREAKDOWN:")
        print("-" * 25)
        for source, count in results['source_results'].items():
            print(f"{source}: {count} properties")
        
        # Market statistics
        market = results['market_analysis']
        print(f"\n[MONEY] MARKET STATISTICS:")
        print("-" * 25)
        print(f"Median Price: ${market['median_price']:,.0f}")
        print(f"Average Price: ${market['average_price']:,.0f}")
        print(f"Price Range: ${market['price_range']['min']:,.0f} - ${market['price_range']['max']:,.0f}")
        
        if market.get('median_price_per_sqft'):
            print(f"Median $/SqFt: ${market['median_price_per_sqft']:.0f}")
        
        if market.get('median_days_on_market'):
            print(f"Median Days on Market: {market['median_days_on_market']:.0f}")
        
        # Property type distribution
        if market.get('property_type_distribution'):
            print(f"\n[NEIGHBORHOOD] PROPERTY TYPES:")
            print("-" * 25)
            for prop_type, count in market['property_type_distribution'].items():
                percentage = (count / market['total_properties_analyzed']) * 100
                print(f"{prop_type}: {count} ({percentage:.1f}%)")
        
        # Investment analysis
        if results['ai_insights'].get('investment_score'):
            score_data = results['ai_insights']['investment_score']
            print(f"\n[STAR] INVESTMENT ANALYSIS:")
            print("-" * 25)
            print(f"Investment Score: {score_data['score']}/100 ({score_data['rating']})")
            if score_data.get('factors'):
                print("Key Factors:")
                for factor in score_data['factors'][:3]:
                    print(f"  * {factor}")
        
        # Sample properties
        print(f"\n[HOME] SAMPLE PROPERTIES:")
        print("-" * 25)
        for i, prop in enumerate(results['property_listings'][:3], 1):
            print(f"\n{i}. {prop['address']}")
            print(f"   [MONEY] ${prop['price']:,}")
            if prop['bedrooms'] and prop['bathrooms']:
                print(f"   [BED] {prop['bedrooms']}BR / {prop['bathrooms']}BA")
            if prop['square_feet']:
                print(f"   [SIZE] {prop['square_feet']:,} sqft")
                if prop['price_per_sqft']:
                    print(f"   [DOLLAR] ${prop['price_per_sqft']:.0f}/sqft")
            print(f"   [OFFICE] Source: {prop['source']}")
        
        # AI insights preview
        if results['ai_insights'].get('ai_analysis'):
            print(f"\n[AI] AI MARKET INSIGHTS:")
            print("-" * 30)
            analysis = results['ai_insights']['ai_analysis']
            # Show first few sentences
            sentences = analysis.split('.')[:3]
            for sentence in sentences:
                if sentence.strip():
                    print(f"  {sentence.strip()}.")
            if len(analysis.split('.')) > 3:
                print("  ... (see full analysis in output files)")
        
        print(f"\n[STATS] Detailed analysis saved to: examples/outputs/real_estate_research/")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[ERROR] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")


def main():
    """Main entry point"""
    try:
        asyncio.run(demo_real_estate_research())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")


if __name__ == "__main__":
    main()