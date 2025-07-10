#!/usr/bin/env python3
"""
AI-Powered Travel Planning Assistant

Transforms casual travel conversations into comprehensive itineraries
with dynamic form flows that adapt based on preferences and context.

Features:
- Natural language destination and preference extraction
- Budget-aware recommendations
- Dynamic activity suggestions based on traveler profile
- Real-time availability checking
- Multi-destination trip planning
- Group travel coordination
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field, create_model
import json
import random

from html_v3_ai import (
    LLMProvider, ConversationContext, ConversationIntent,
    AIFormChainGenerator
)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from html_v3 import FormChainEngine, FormStep, FormStepProcessor, FormFieldSpec, FieldType


class TravelStyle(str, Enum):
    LUXURY = "luxury"
    COMFORT = "comfort"
    BUDGET = "budget"
    BACKPACKER = "backpacker"
    BUSINESS = "business"


class ActivityType(str, Enum):
    CULTURAL = "cultural"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    CULINARY = "culinary"
    SHOPPING = "shopping"
    NIGHTLIFE = "nightlife"
    NATURE = "nature"
    FAMILY = "family"


class TravelAIProvider(LLMProvider):
    """Travel-specific AI provider for trip planning"""
    
    def __init__(self):
        self.destination_db = {
            "paris": {
                "country": "France",
                "attractions": ["Eiffel Tower", "Louvre", "Notre-Dame", "Versailles"],
                "best_months": ["April", "May", "September", "October"],
                "avg_daily_cost": {"luxury": 300, "comfort": 150, "budget": 80},
                "languages": ["French"],
                "visa_required": False,  # for US citizens
                "activities": {
                    ActivityType.CULTURAL: ["Museums", "Historic sites", "Art galleries"],
                    ActivityType.CULINARY: ["Michelin restaurants", "Wine tasting", "Cooking classes"],
                    ActivityType.SHOPPING: ["Champs-Élysées", "Le Marais", "Galleries Lafayette"]
                }
            },
            "tokyo": {
                "country": "Japan",
                "attractions": ["Mount Fuji", "Sensoji Temple", "Shibuya", "Tsukiji Market"],
                "best_months": ["March", "April", "October", "November"],
                "avg_daily_cost": {"luxury": 350, "comfort": 180, "budget": 100},
                "languages": ["Japanese"],
                "visa_required": False,
                "activities": {
                    ActivityType.CULTURAL: ["Temples", "Traditional tea ceremony", "Sumo wrestling"],
                    ActivityType.CULINARY: ["Sushi making", "Ramen tours", "Izakaya hopping"],
                    ActivityType.ADVENTURE: ["Mount Fuji climbing", "Robot restaurant", "Go-karting"]
                }
            },
            "bali": {
                "country": "Indonesia",
                "attractions": ["Temples", "Rice terraces", "Beaches", "Ubud"],
                "best_months": ["April", "May", "June", "September"],
                "avg_daily_cost": {"luxury": 200, "comfort": 80, "budget": 40},
                "languages": ["Indonesian", "English"],
                "visa_required": True,
                "activities": {
                    ActivityType.RELAXATION: ["Spa", "Yoga retreats", "Beach clubs"],
                    ActivityType.ADVENTURE: ["Surfing", "Volcano trekking", "Diving"],
                    ActivityType.CULTURAL: ["Temple tours", "Traditional dance", "Art villages"]
                }
            }
        }
        
        self.travel_tips = {
            "packing": {
                "tropical": ["Sunscreen", "Light clothing", "Insect repellent", "Swimwear"],
                "city": ["Comfortable walking shoes", "Day pack", "Power adapter", "City map"],
                "adventure": ["Hiking boots", "First aid kit", "Water bottle", "Quick-dry clothes"]
            },
            "budget_savers": [
                "Book flights 6-8 weeks in advance",
                "Stay in neighborhoods outside city center",
                "Use public transportation",
                "Eat where locals eat",
                "Free walking tours"
            ]
        }
    
    async def analyze_conversation(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze travel conversation for destinations and preferences"""
        
        messages_text = " ".join([m["content"].lower() for m in context.messages])
        
        # Extract destinations
        destinations = []
        for dest, info in self.destination_db.items():
            if dest in messages_text or info["country"].lower() in messages_text:
                destinations.append(dest)
        
        # Extract travel dates
        import re
        
        # Look for month mentions
        months = ["january", "february", "march", "april", "may", "june",
                  "july", "august", "september", "october", "november", "december"]
        mentioned_months = [m for m in months if m in messages_text]
        
        # Extract budget indicators
        budget_level = TravelStyle.COMFORT  # default
        if any(word in messages_text for word in ["luxury", "splurge", "high-end"]):
            budget_level = TravelStyle.LUXURY
        elif any(word in messages_text for word in ["budget", "cheap", "affordable"]):
            budget_level = TravelStyle.BUDGET
        elif any(word in messages_text for word in ["backpack", "hostel"]):
            budget_level = TravelStyle.BACKPACKER
        
        # Extract activity preferences
        activities = []
        activity_keywords = {
            ActivityType.CULTURAL: ["museum", "history", "culture", "temple"],
            ActivityType.ADVENTURE: ["hiking", "climbing", "adventure", "extreme"],
            ActivityType.RELAXATION: ["relax", "spa", "beach", "resort"],
            ActivityType.CULINARY: ["food", "restaurant", "cooking", "wine"],
            ActivityType.NATURE: ["nature", "park", "mountain", "wildlife"]
        }
        
        for activity, keywords in activity_keywords.items():
            if any(keyword in messages_text for keyword in keywords):
                activities.append(activity)
        
        # Extract group info
        group_size = 1
        if "family" in messages_text:
            group_size = 4
        elif "couple" in messages_text or "partner" in messages_text:
            group_size = 2
        elif "friends" in messages_text:
            group_size = 3
        
        # Duration
        duration_match = re.search(r'(\d+)\s*(days?|weeks?)', messages_text)
        duration = 7  # default
        if duration_match:
            num = int(duration_match.group(1))
            unit = duration_match.group(2)
            duration = num if "day" in unit else num * 7
        
        return {
            "intent": ConversationIntent.BOOKING,
            "entities": {
                "destinations": destinations,
                "travel_months": mentioned_months,
                "budget_level": budget_level,
                "activities": activities,
                "group_size": group_size,
                "duration_days": duration,
                "special_interests": self._extract_special_interests(messages_text)
            },
            "confidence": 0.85,
            "suggestions": self._generate_suggestions(destinations, activities, budget_level)
        }
    
    async def generate_form_schema(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate travel planning form based on conversation"""
        
        analysis = await self.analyze_conversation(context)
        entities = analysis["entities"]
        
        fields = []
        
        # Destination selection
        if not entities["destinations"]:
            fields.append({
                "name": "destination_search",
                "type": "autocomplete",
                "label": "Where would you like to go?",
                "placeholder": "Search destinations...",
                "options": list(self.destination_db.keys()),
                "required": True
            })
        else:
            # Confirm destinations
            fields.append({
                "name": "confirmed_destinations",
                "type": "checkbox_group",
                "label": "Confirm your destinations",
                "options": [{"value": d, "label": d.title()} for d in entities["destinations"]],
                "default": entities["destinations"],
                "required": True
            })
        
        # Travel dates
        fields.extend([
            {
                "name": "departure_date",
                "type": "date",
                "label": "Departure date",
                "min": date.today().isoformat(),
                "max": (date.today() + timedelta(days=365)).isoformat(),
                "required": True
            },
            {
                "name": "return_date",
                "type": "date",
                "label": "Return date",
                "min": date.today().isoformat(),
                "required": True
            }
        ])
        
        # Travelers
        fields.extend([
            {
                "name": "num_adults",
                "type": "number",
                "label": "Number of adults",
                "min": 1,
                "max": 10,
                "default": entities["group_size"],
                "required": True
            },
            {
                "name": "num_children",
                "type": "number",
                "label": "Number of children",
                "min": 0,
                "max": 10,
                "default": 0,
                "required": False
            }
        ])
        
        # Budget
        fields.append({
            "name": "budget_per_person",
            "type": "range",
            "label": "Budget per person (excluding flights)",
            "min": 500,
            "max": 10000,
            "step": 100,
            "default": self._estimate_budget(entities),
            "help_text": f"Estimated for {entities['duration_days']} days"
        })
        
        # Activities
        if entities["destinations"]:
            # Get activities for selected destinations
            all_activities = set()
            for dest in entities["destinations"]:
                if dest in self.destination_db:
                    for activities in self.destination_db[dest]["activities"].values():
                        all_activities.update(activities)
            
            fields.append({
                "name": "preferred_activities",
                "type": "checkbox_group",
                "label": "What would you like to do?",
                "options": sorted(list(all_activities)),
                "help_text": "Select all that interest you"
            })
        
        # Special requirements
        fields.extend([
            {
                "name": "accommodation_type",
                "type": "select",
                "label": "Preferred accommodation",
                "options": ["Hotel", "Resort", "Airbnb", "Hostel", "Villa"],
                "default": self._get_default_accommodation(entities["budget_level"])
            },
            {
                "name": "dietary_restrictions",
                "type": "checkbox_group",
                "label": "Dietary restrictions",
                "options": ["Vegetarian", "Vegan", "Gluten-free", "Halal", "Kosher", "None"],
                "required": False
            },
            {
                "name": "special_requests",
                "type": "textarea",
                "label": "Any special requests or must-sees?",
                "placeholder": "Anniversary trip, specific attractions, accessibility needs...",
                "required": False
            }
        ])
        
        return {
            "title": "Let's Plan Your Perfect Trip!",
            "description": f"Based on our conversation, I've prepared a trip plan for you",
            "fields": fields,
            "suggestions": analysis["suggestions"]
        }
    
    async def process_response(self, user_input: str, context: ConversationContext) -> Dict[str, Any]:
        """Process user response and update travel context"""
        
        context.messages.append({"role": "user", "content": user_input})
        
        # Re-analyze with new input
        new_analysis = await self.analyze_conversation(context)
        
        # Check for changes in preferences
        changes = []
        if context.entities:
            old_destinations = set(context.entities.get("destinations", []))
            new_destinations = set(new_analysis["entities"]["destinations"])
            if old_destinations != new_destinations:
                changes.append("destinations")
        
        context.entities = new_analysis["entities"]
        
        return {
            "updated_context": context,
            "changes_detected": changes,
            "new_suggestions": new_analysis["suggestions"]
        }
    
    def _extract_special_interests(self, text: str) -> List[str]:
        """Extract special travel interests"""
        
        interests = []
        
        interest_keywords = {
            "photography": ["photo", "instagram", "scenic"],
            "honeymoon": ["honeymoon", "romantic", "couple"],
            "family": ["kids", "family", "children"],
            "solo": ["solo", "alone", "myself"],
            "eco": ["sustainable", "eco", "green"],
            "luxury": ["luxury", "premium", "exclusive"]
        }
        
        for interest, keywords in interest_keywords.items():
            if any(keyword in text for keyword in keywords):
                interests.append(interest)
        
        return interests
    
    def _generate_suggestions(
        self,
        destinations: List[str],
        activities: List[ActivityType],
        budget: TravelStyle
    ) -> List[Dict[str, str]]:
        """Generate travel suggestions"""
        
        suggestions = []
        
        # Destination suggestions
        if not destinations:
            if ActivityType.RELAXATION in activities:
                suggestions.append({
                    "type": "destination",
                    "title": "Consider Bali",
                    "reason": "Perfect for relaxation with world-class spas and beaches"
                })
            elif ActivityType.CULTURAL in activities:
                suggestions.append({
                    "type": "destination",
                    "title": "Consider Kyoto",
                    "reason": "Rich cultural heritage with temples and traditional experiences"
                })
        
        # Activity suggestions based on destination
        for dest in destinations:
            if dest in self.destination_db:
                dest_info = self.destination_db[dest]
                
                # Best time to visit
                suggestions.append({
                    "type": "timing",
                    "title": f"Best time for {dest.title()}",
                    "reason": f"Consider visiting in {', '.join(dest_info['best_months'][:2])}"
                })
                
                # Budget tip
                daily_cost = dest_info["avg_daily_cost"].get(budget.value, 100)
                suggestions.append({
                    "type": "budget",
                    "title": "Budget estimate",
                    "reason": f"Plan for ~${daily_cost}/day per person in {dest.title()}"
                })
        
        # General tips
        if budget == TravelStyle.BUDGET:
            suggestions.extend([
                {
                    "type": "savings",
                    "title": "Save on accommodation",
                    "reason": "Consider hostels or Airbnb outside city center"
                },
                {
                    "type": "savings",
                    "title": "Free activities",
                    "reason": "Many cities offer free walking tours and museum days"
                }
            ])
        
        return suggestions[:5]  # Top 5 suggestions
    
    def _estimate_budget(self, entities: Dict[str, Any]) -> int:
        """Estimate total budget based on preferences"""
        
        daily_cost = {
            TravelStyle.LUXURY: 250,
            TravelStyle.COMFORT: 150,
            TravelStyle.BUDGET: 80,
            TravelStyle.BACKPACKER: 50
        }
        
        base_daily = daily_cost.get(entities["budget_level"], 100)
        total = base_daily * entities["duration_days"]
        
        # Adjust for destinations
        if "paris" in entities["destinations"] or "tokyo" in entities["destinations"]:
            total *= 1.2  # 20% more expensive
        
        return int(total)
    
    def _get_default_accommodation(self, budget_level: TravelStyle) -> str:
        """Get default accommodation type based on budget"""
        
        accommodation_map = {
            TravelStyle.LUXURY: "Hotel",
            TravelStyle.COMFORT: "Hotel",
            TravelStyle.BUDGET: "Airbnb",
            TravelStyle.BACKPACKER: "Hostel",
            TravelStyle.BUSINESS: "Hotel"
        }
        
        return accommodation_map.get(budget_level, "Hotel")


class TravelItineraryGenerator:
    """Generate complete travel itineraries"""
    
    def __init__(self, ai_provider: TravelAIProvider):
        self.ai_provider = ai_provider
    
    async def generate_itinerary(
        self,
        destinations: List[str],
        dates: Tuple[date, date],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate day-by-day itinerary"""
        
        departure_date, return_date = dates
        num_days = (return_date - departure_date).days + 1
        
        itinerary = {
            "trip_summary": {
                "destinations": destinations,
                "duration": f"{num_days} days",
                "travelers": preferences.get("num_adults", 1) + preferences.get("num_children", 0),
                "total_budget": preferences.get("budget_per_person", 1000) * preferences.get("num_adults", 1)
            },
            "daily_plans": [],
            "packing_list": self._generate_packing_list(destinations, preferences),
            "important_info": self._get_important_info(destinations)
        }
        
        # Generate daily plans
        for day_num in range(num_days):
            current_date = departure_date + timedelta(days=day_num)
            
            if day_num == 0:
                # Arrival day
                daily_plan = {
                    "day": day_num + 1,
                    "date": current_date.isoformat(),
                    "title": "Arrival Day",
                    "activities": [
                        {"time": "Morning", "activity": "Depart from home"},
                        {"time": "Afternoon", "activity": f"Arrive in {destinations[0].title()}"},
                        {"time": "Evening", "activity": "Check-in and local dinner"}
                    ]
                }
            elif day_num == num_days - 1:
                # Departure day
                daily_plan = {
                    "day": day_num + 1,
                    "date": current_date.isoformat(),
                    "title": "Departure Day",
                    "activities": [
                        {"time": "Morning", "activity": "Check-out and last-minute shopping"},
                        {"time": "Afternoon", "activity": "Depart for airport"},
                        {"time": "Evening", "activity": "Flight home"}
                    ]
                }
            else:
                # Regular day
                daily_plan = await self._generate_daily_activities(
                    destinations[0],  # Simplify to first destination
                    day_num + 1,
                    current_date,
                    preferences
                )
            
            itinerary["daily_plans"].append(daily_plan)
        
        return itinerary
    
    async def _generate_daily_activities(
        self,
        destination: str,
        day_num: int,
        date: date,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate activities for a single day"""
        
        dest_info = self.ai_provider.destination_db.get(destination, {})
        attractions = dest_info.get("attractions", [])
        
        # Rotate through attractions
        daily_attractions = attractions[(day_num - 2) % len(attractions):] + attractions[:(day_num - 2) % len(attractions)]
        
        activities = [
            {"time": "Morning", "activity": f"Visit {daily_attractions[0] if daily_attractions else 'Local market'}"},
            {"time": "Lunch", "activity": "Local cuisine experience"},
            {"time": "Afternoon", "activity": f"Explore {daily_attractions[1] if len(daily_attractions) > 1 else 'City center'}"},
            {"time": "Evening", "activity": "Dinner and evening entertainment"}
        ]
        
        return {
            "day": day_num,
            "date": date.isoformat(),
            "title": f"Exploring {destination.title()}",
            "activities": activities,
            "notes": "Times are flexible - adjust based on your pace!"
        }
    
    def _generate_packing_list(self, destinations: List[str], preferences: Dict[str, Any]) -> List[str]:
        """Generate packing list based on destinations"""
        
        packing_list = [
            "Passport and travel documents",
            "Travel insurance info",
            "Phone charger and adapter",
            "Medications",
            "Comfortable walking shoes"
        ]
        
        # Add destination-specific items
        for dest in destinations:
            if dest == "bali":
                packing_list.extend(["Sunscreen SPF 50+", "Mosquito repellent", "Light cotton clothes"])
            elif dest == "paris":
                packing_list.extend(["Dress clothes for nice restaurants", "Comfortable flats", "Light jacket"])
            elif dest == "tokyo":
                packing_list.extend(["JR Pass", "Portable WiFi", "Cash (many places cash-only)"])
        
        return list(set(packing_list))  # Remove duplicates
    
    def _get_important_info(self, destinations: List[str]) -> List[Dict[str, str]]:
        """Get important travel information"""
        
        info = []
        
        for dest in destinations:
            dest_info = self.ai_provider.destination_db.get(dest, {})
            
            if dest_info.get("visa_required"):
                info.append({
                    "type": "visa",
                    "title": f"Visa required for {dest.title()}",
                    "details": "Check embassy website for requirements"
                })
            
            info.append({
                "type": "language",
                "title": f"Language in {dest.title()}",
                "details": f"Primary: {', '.join(dest_info.get('languages', ['Local language']))}"
            })
        
        return info


async def demonstrate_travel_planner():
    """Demonstrate the AI-powered travel planner"""
    
    print("✈️ AI-Powered Travel Planning Assistant")
    print("="*60)
    
    # Example conversations
    conversations = [
        {
            "user": "travel_enthusiast",
            "messages": [
                "I want to visit Paris and maybe Tokyo next spring",
                "Looking for a mix of culture and food experiences",
                "Probably 2 weeks total, comfortable budget but not luxury"
            ]
        },
        {
            "user": "family_traveler",
            "messages": [
                "Planning a family trip to Bali with 2 kids",
                "Want to relax but also some activities for the children",
                "Thinking July or August, about 10 days"
            ]
        }
    ]
    
    ai_provider = TravelAIProvider()
    
    for conv in conversations:
        print(f"\n🧳 Travel Planning for: {conv['user']}")
        print("-" * 40)
        
        # Create context
        context = ConversationContext(messages=[
            {"role": "user", "content": msg} for msg in conv["messages"]
        ])
        
        # Analyze conversation
        analysis = await ai_provider.analyze_conversation(context)
        
        print("\n📊 Conversation Analysis:")
        print(f"   Destinations: {', '.join(analysis['entities']['destinations']) or 'Not specified'}")
        print(f"   Duration: {analysis['entities']['duration_days']} days")
        print(f"   Budget level: {analysis['entities']['budget_level'].value}")
        print(f"   Group size: {analysis['entities']['group_size']} travelers")
        print(f"   Activities: {', '.join([a.value for a in analysis['entities']['activities']])}")
        
        print("\n💡 AI Suggestions:")
        for suggestion in analysis["suggestions"][:3]:
            print(f"   - {suggestion['title']}: {suggestion['reason']}")
        
        # Generate form schema
        schema = await ai_provider.generate_form_schema(context)
        
        print(f"\n📝 Generated form with {len(schema['fields'])} fields")
        print("   Key fields:")
        for field in schema["fields"][:5]:
            print(f"   - {field['label']} ({field['type']})")
        
        # Simulate form completion and itinerary generation
        if analysis['entities']['destinations']:
            print("\n🗓️ Sample Itinerary Generation:")
            
            generator = TravelItineraryGenerator(ai_provider)
            
            # Mock dates
            departure = date.today() + timedelta(days=90)
            return_date = departure + timedelta(days=analysis['entities']['duration_days'] - 1)
            
            itinerary = await generator.generate_itinerary(
                analysis['entities']['destinations'],
                (departure, return_date),
                {
                    "num_adults": analysis['entities']['group_size'],
                    "budget_per_person": 2000,
                    "preferred_activities": analysis['entities']['activities']
                }
            )
            
            print(f"   Generated {len(itinerary['daily_plans'])} day itinerary")
            print("\n   First 3 days:")
            for day in itinerary["daily_plans"][:3]:
                print(f"   Day {day['day']} - {day['title']}")
                for activity in day["activities"][:2]:
                    print(f"     • {activity['time']}: {activity['activity']}")
    
    print("\n" + "="*60)
    print("🌟 Travel Planning Assistant Features:")
    print("- Natural language destination extraction")
    print("- Budget-aware recommendations")
    print("- Dynamic activity suggestions")
    print("- Day-by-day itinerary generation")
    print("- Packing lists and travel tips")
    print("- Multi-destination support")


class TravelPlannerUI:
    """Generate beautiful UI for travel planning"""
    
    @staticmethod
    def create_itinerary_view(itinerary: Dict[str, Any]) -> str:
        """Create HTML view of the itinerary"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Your Travel Itinerary</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            background: #f5f6fa;
            color: #2c3e50;
        }}
        
        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        
        .hero h1 {{
            margin: 0 0 20px 0;
            font-size: 36px;
            font-weight: 300;
        }}
        
        .trip-summary {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 12px;
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .container {{
            max-width: 1000px;
            margin: -40px auto 40px;
            padding: 0 20px;
        }}
        
        .timeline {{
            position: relative;
            padding: 20px 0;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 50px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #e0e0e0;
        }}
        
        .day-card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0 20px 80px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            position: relative;
            transition: transform 0.3s;
        }}
        
        .day-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }}
        
        .day-number {{
            position: absolute;
            left: -80px;
            top: 30px;
            width: 60px;
            height: 60px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
        }}
        
        .day-header {{
            margin-bottom: 20px;
        }}
        
        .day-title {{
            font-size: 24px;
            font-weight: 600;
            color: #2c3e50;
            margin: 0 0 5px 0;
        }}
        
        .day-date {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        
        .activities {{
            margin: 20px 0;
        }}
        
        .activity {{
            display: flex;
            align-items: flex-start;
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: background 0.2s;
        }}
        
        .activity:hover {{
            background: #e9ecef;
        }}
        
        .activity-time {{
            font-weight: 600;
            color: #667eea;
            min-width: 100px;
            margin-right: 20px;
        }}
        
        .activity-desc {{
            flex: 1;
        }}
        
        .info-section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .info-section h2 {{
            margin: 0 0 20px 0;
            color: #2c3e50;
        }}
        
        .packing-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
        }}
        
        .packing-item {{
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
            display: flex;
            align-items: center;
        }}
        
        .packing-item::before {{
            content: '✓';
            color: #27ae60;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        @media (max-width: 768px) {{
            .timeline::before {{
                left: 20px;
            }}
            
            .day-card {{
                margin-left: 50px;
            }}
            
            .day-number {{
                left: -50px;
                width: 40px;
                height: 40px;
                font-size: 18px;
            }}
        }}
    </style>
</head>
<body>
    <div class="hero">
        <h1>✈️ Your Travel Itinerary</h1>
        <div class="trip-summary">
            <p><strong>Destinations:</strong> {', '.join(itinerary['trip_summary']['destinations'])}</p>
            <p><strong>Duration:</strong> {itinerary['trip_summary']['duration']}</p>
            <p><strong>Travelers:</strong> {itinerary['trip_summary']['travelers']} people</p>
        </div>
    </div>
    
    <div class="container">
        <div class="timeline">
"""
        
        # Add daily plans
        for day in itinerary["daily_plans"]:
            html += f"""
            <div class="day-card">
                <div class="day-number">{day['day']}</div>
                <div class="day-header">
                    <h3 class="day-title">{day['title']}</h3>
                    <div class="day-date">{day['date']}</div>
                </div>
                <div class="activities">
"""
            
            for activity in day["activities"]:
                html += f"""
                    <div class="activity">
                        <div class="activity-time">{activity['time']}</div>
                        <div class="activity-desc">{activity['activity']}</div>
                    </div>
"""
            
            html += """
                </div>
            </div>
"""
        
        # Add packing list
        html += """
        </div>
        
        <div class="info-section">
            <h2>📋 Packing List</h2>
            <div class="packing-list">
"""
        
        for item in itinerary["packing_list"]:
            html += f'                <div class="packing-item">{item}</div>\n'
        
        html += """
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        return html


if __name__ == "__main__":
    # Run demo
    asyncio.run(demonstrate_travel_planner())
    
    # Generate sample itinerary UI
    print("\n\n🎨 Generating sample itinerary UI...")
    
    sample_itinerary = {
        "trip_summary": {
            "destinations": ["Paris", "Tokyo"],
            "duration": "14 days",
            "travelers": 2,
            "total_budget": 4000
        },
        "daily_plans": [
            {
                "day": 1,
                "date": "2024-05-01",
                "title": "Arrival in Paris",
                "activities": [
                    {"time": "Morning", "activity": "Depart from home"},
                    {"time": "Afternoon", "activity": "Arrive at Charles de Gaulle Airport"},
                    {"time": "Evening", "activity": "Check-in at Hotel du Louvre"}
                ]
            },
            {
                "day": 2,
                "date": "2024-05-02",
                "title": "Exploring Paris",
                "activities": [
                    {"time": "Morning", "activity": "Visit the Eiffel Tower"},
                    {"time": "Lunch", "activity": "Café de Flore"},
                    {"time": "Afternoon", "activity": "Louvre Museum"},
                    {"time": "Evening", "activity": "Seine River Cruise"}
                ]
            }
        ],
        "packing_list": [
            "Passport and travel documents",
            "Comfortable walking shoes",
            "Phone charger and adapter",
            "Light jacket",
            "Camera"
        ]
    }
    
    ui_html = TravelPlannerUI.create_itinerary_view(sample_itinerary)
    
    with open("travel_itinerary.html", "w") as f:
        f.write(ui_html)
    
    print("✅ Sample itinerary saved to: travel_itinerary.html")