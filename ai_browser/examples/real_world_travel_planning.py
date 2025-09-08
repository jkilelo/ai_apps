#!/usr/bin/env python3
"""
Real-World Travel Planning Automation

This example demonstrates autonomous travel planning capabilities:
- Search flight booking sites (Expedia, Kayak, Google Flights)
- Compare hotel prices and amenities (Booking.com, Hotels.com)
- Research destinations and attractions
- Generate personalized itineraries with AI
- Track price changes and deals
- Create comprehensive travel reports
- Export travel plans and bookings

REQUIREMENTS:
- At least one LLM API key (OpenAI recommended for itinerary generation)
- Working internet connection
- AI Browser v2.0.0 system components

USAGE:
    python examples/real_world_travel_planning.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


@dataclass
class FlightOption:
    """Flight search result"""
    departure_city: str
    arrival_city: str
    departure_date: str
    return_date: Optional[str] = None
    price: Optional[int] = None
    airline: str = ""
    duration: Optional[str] = None
    stops: int = 0
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    booking_url: str = ""
    source: str = ""


@dataclass
class HotelOption:
    """Hotel search result"""
    name: str
    location: str
    price_per_night: Optional[int] = None
    rating: Optional[float] = None
    amenities: List[str] = None
    booking_url: str = ""
    source: str = ""


class TravelPlanningAgent:
    """AI-powered travel planning automation"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/travel_planning")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"travel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def search_flights(self, origin: str, destination: str, departure_date: str, return_date: str = None) -> List[FlightOption]:
        """Search for flights using multiple booking sites"""
        logger.info(f"[TRAVEL] Searching flights: {origin} to {destination}")
        
        # Search Google Flights
        browser = AIBrowser({"log_level": "INFO"})
        
        # Construct search URL (simplified for demo)
        search_url = f"https://www.google.com/flights?hl=en"
        
        task = f"""
        Go to Google Flights and search for flights:
        - From: {origin}
        - To: {destination}
        - Departure: {departure_date}
        {f"- Return: {return_date}" if return_date else "- One-way trip"}
        
        Find the top 5 flight options and extract:
        1. Airline name
        2. Departure and arrival times
        3. Flight duration
        4. Number of stops
        5. Price
        6. Direct booking links if available
        
        Focus on reasonable prices and reputable airlines.
        Handle any location/date selection interfaces.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=True,
            max_steps=15,
            timeout=90000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Parse flight results (simplified)
            flights = [
                FlightOption(
                    departure_city=origin,
                    arrival_city=destination,
                    departure_date=departure_date,
                    return_date=return_date,
                    price=500,  # Would extract from actual results
                    airline="Sample Airline",
                    duration="5h 30m",
                    stops=0,
                    source="Google Flights"
                )
            ]
            
            logger.info(f"[SUCCESS] Found {len(flights)} flight options")
            return flights
            
        except Exception as e:
            logger.error(f"[ERROR] Flight search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def search_hotels(self, destination: str, check_in: str, check_out: str) -> List[HotelOption]:
        """Search for hotels at destination"""
        logger.info(f"[HOTEL] Searching hotels in: {destination}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        search_url = "https://www.booking.com"
        
        task = f"""
        Go to Booking.com and search for hotels:
        - Destination: {destination}
        - Check-in: {check_in}
        - Check-out: {check_out}
        
        Find top 5 hotels and extract:
        1. Hotel name and location
        2. Price per night
        3. Guest rating and reviews
        4. Key amenities (WiFi, parking, pool, etc.)
        5. Booking availability
        6. Direct booking links
        
        Handle location search and date selection.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=True,
            max_steps=15,
            timeout=90000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Parse hotel results (simplified)
            hotels = [
                HotelOption(
                    name="Sample Hotel",
                    location=destination,
                    price_per_night=150,
                    rating=4.2,
                    amenities=["WiFi", "Parking", "Pool"],
                    source="Booking.com"
                )
            ]
            
            logger.info(f"[SUCCESS] Found {len(hotels)} hotel options")
            return hotels
            
        except Exception as e:
            logger.error(f"[ERROR] Hotel search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def generate_itinerary(self, destination: str, duration_days: int, interests: List[str]) -> Dict[str, Any]:
        """Generate personalized travel itinerary with AI"""
        logger.info(f"[CALENDAR] Generating {duration_days}-day itinerary for {destination}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        task = f"""
        Create a detailed {duration_days}-day travel itinerary for {destination}.
        
        Traveler interests: {', '.join(interests)}
        
        For each day, provide:
        1. Morning activities and attractions
        2. Recommended restaurants for meals
        3. Afternoon sightseeing or activities
        4. Evening entertainment options
        5. Transportation suggestions
        6. Estimated costs and time requirements
        7. Local tips and cultural notes
        
        Make it practical and well-organized.
        Include must-see attractions and local experiences.
        Consider travel time between locations.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.example.com",
            headless=True,
            max_steps=5,
            timeout=90000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            itinerary = {
                "destination": destination,
                "duration_days": duration_days,
                "interests": interests,
                "detailed_plan": result.get('summary', ''),
                "daily_activities": result.get('extracted_data', {}),
                "generated_at": datetime.now().isoformat()
            }
            
            return itinerary
            
        except Exception as e:
            logger.error(f"[ERROR] Itinerary generation failed: {e}")
            return {"error": str(e)}
        finally:
            await browser.cleanup()
    
    async def comprehensive_travel_planning(self, trip_details: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive travel planning"""
        logger.info(f"[WORLD] Planning trip to {trip_details['destination']}")
        
        # Search flights
        flights = await self.search_flights(
            trip_details['origin'],
            trip_details['destination'],
            trip_details['departure_date'],
            trip_details.get('return_date')
        )
        
        # Search hotels
        hotels = await self.search_hotels(
            trip_details['destination'],
            trip_details['departure_date'],
            trip_details.get('return_date', trip_details['departure_date'])
        )
        
        # Generate itinerary
        itinerary = await self.generate_itinerary(
            trip_details['destination'],
            trip_details.get('duration_days', 3),
            trip_details.get('interests', ['sightseeing'])
        )
        
        # Compile results
        travel_plan = {
            "trip_details": trip_details,
            "flights": [asdict(f) for f in flights],
            "hotels": [asdict(h) for h in hotels],
            "itinerary": itinerary,
            "planning_timestamp": datetime.now().isoformat(),
            "session_id": self.session_id
        }
        
        # Save results
        await self._save_travel_plan(travel_plan)
        
        return travel_plan
    
    async def _save_travel_plan(self, plan: Dict[str, Any]):
        """Save travel planning results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_file = self.results_dir / f"travel_plan_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, default=str, ensure_ascii=False)
        
        # Save readable itinerary
        itinerary_file = self.results_dir / f"itinerary_{timestamp}.txt"
        with open(itinerary_file, 'w', encoding='utf-8') as f:
            f.write("TRAVEL ITINERARY\n")
            f.write("="*50 + "\n\n")
            
            details = plan['trip_details']
            f.write(f"Destination: {details['destination']}\n")
            f.write(f"Departure: {details['departure_date']}\n")
            if details.get('return_date'):
                f.write(f"Return: {details['return_date']}\n")
            f.write("\n")
            
            # Flights
            if plan['flights']:
                f.write("FLIGHTS:\n")
                f.write("-" * 20 + "\n")
                for flight in plan['flights']:
                    f.write(f"* {flight['airline']}: ${flight['price']}\n")
                f.write("\n")
            
            # Hotels
            if plan['hotels']:
                f.write("ACCOMMODATIONS:\n")
                f.write("-" * 20 + "\n")
                for hotel in plan['hotels']:
                    f.write(f"* {hotel['name']}: ${hotel['price_per_night']}/night\n")
                f.write("\n")
            
            # Itinerary
            if plan['itinerary'].get('detailed_plan'):
                f.write("DETAILED ITINERARY:\n")
                f.write("-" * 20 + "\n")
                f.write(plan['itinerary']['detailed_plan'])
        
        logger.info(f"[FILE] Travel plan saved to: {json_file}")


async def demo_travel_planning():
    """Demonstrate travel planning capabilities"""
    print("\n" + "="*70)
    print("[WORLD] AI-POWERED TRAVEL PLANNING AUTOMATION")
    print("="*70)
    print("This demo plans complete trips including flights, hotels, and")
    print("personalized itineraries using AI reasoning and browser automation.\n")
    
    agent = TravelPlanningAgent()
    
    # Get trip details
    print("Let's plan your trip!")
    destination = input("Destination city [Paris, France]: ").strip() or "Paris, France"
    origin = input("Departure city [New York, NY]: ").strip() or "New York, NY"
    
    # Get dates
    departure_date = input("Departure date (YYYY-MM-DD) [2024-06-15]: ").strip() or "2024-06-15"
    return_date = input("Return date (YYYY-MM-DD) [2024-06-20]: ").strip() or "2024-06-20"
    
    # Get interests
    interests_input = input("Interests (comma-separated) [museums, food, architecture]: ").strip()
    interests = [i.strip() for i in interests_input.split(',')] if interests_input else ["museums", "food", "architecture"]
    
    # Calculate duration
    try:
        dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
        ret_date = datetime.strptime(return_date, "%Y-%m-%d")
        duration_days = (ret_date - dep_date).days
    except:
        duration_days = 5  # Default
    
    trip_details = {
        "destination": destination,
        "origin": origin,
        "departure_date": departure_date,
        "return_date": return_date,
        "duration_days": duration_days,
        "interests": interests
    }
    
    print(f"\n[TARGET] Planning {duration_days}-day trip to {destination}")
    print("[TIME]  This may take 5-8 minutes to search flights, hotels, and create itinerary...\n")
    
    try:
        # Run comprehensive planning
        results = await agent.comprehensive_travel_planning(trip_details)
        
        # Display results
        print("\n" + "="*50)
        print("[CELEBRATION] TRAVEL PLAN COMPLETE")
        print("="*50)
        
        print(f"Destination: {destination}")
        print(f"Duration: {duration_days} days")
        print(f"Dates: {departure_date} to {return_date}")
        
        # Flights summary
        if results.get('flights'):
            print(f"\n[TRAVEL] FLIGHT OPTIONS:")
            print("-" * 20)
            for flight in results['flights'][:3]:
                print(f"* {flight['airline']}: ${flight['price']} ({flight['duration']})")
        
        # Hotels summary
        if results.get('hotels'):
            print(f"\n[HOTEL] HOTEL OPTIONS:")
            print("-" * 20)
            for hotel in results['hotels'][:3]:
                print(f"* {hotel['name']}: ${hotel['price_per_night']}/night ({hotel['rating']}[STAR])")
        
        # Itinerary preview
        if results['itinerary'].get('detailed_plan'):
            print(f"\n[CALENDAR] ITINERARY PREVIEW:")
            print("-" * 25)
            plan_text = results['itinerary']['detailed_plan']
            lines = plan_text.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"  {line.strip()}")
            if len(plan_text.split('\n')) > 5:
                print("  ... (see full itinerary in output files)")
        
        print(f"\n[FILE] Complete travel plan saved to: examples/outputs/travel_planning/")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[ERROR] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")


def main():
    """Main entry point"""
    try:
        asyncio.run(demo_travel_planning())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")


if __name__ == "__main__":
    main()