#!/usr/bin/env python3
"""
Simple Example: Restaurant Order Form Chain

This example clearly demonstrates how form chains work by building
a restaurant ordering system where each step's output affects the next step.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date, time
from enum import Enum
from pydantic import BaseModel, Field
import random

from html_v3 import (
    FormChainEngine, FormStep, FormStepProcessor, FormFieldSpec,
    FieldType, create_form_chain
)


# Step 1: Select Restaurant and Check Availability
class RestaurantSelectionRequest(BaseModel):
    """User selects a restaurant and party size"""
    location: str = Field(..., description="Your delivery address or zip code")
    party_size: int = Field(2, ge=1, le=20, description="Number of people")
    cuisine_preference: str = Field(..., description="Type of cuisine (Italian, Chinese, etc.)")
    
    
class RestaurantSelectionResponse(BaseModel):
    """System returns available restaurants with their menus"""
    selected_location: str
    available_restaurants: List[Dict[str, Any]]  # name, cuisine, rating, delivery_time
    recommended_restaurant: str
    menu_categories: List[str]  # Will be used in next step


# Step 2: Build Your Order
class OrderBuildRequest(BaseModel):
    """User builds their order from the menu"""
    restaurant_name: str  # Pre-filled from previous step
    
    # These fields will be dynamically generated based on menu
    appetizers: List[str] = Field(default_factory=list, description="Select appetizers")
    main_courses: List[str] = Field(default_factory=list, description="Select main courses")
    beverages: List[str] = Field(default_factory=list, description="Select beverages")
    
    special_instructions: Optional[str] = Field(None, description="Any special dietary requirements or instructions")
    

class OrderBuildResponse(BaseModel):
    """System calculates order details and suggests add-ons"""
    order_items: List[Dict[str, Any]]  # item, price, quantity
    subtotal: float
    estimated_prep_time: int  # minutes
    suggested_addons: List[str]
    available_discounts: List[Dict[str, Any]]  # code, description, amount


# Step 3: Checkout and Delivery
class CheckoutRequest(BaseModel):
    """User completes the order"""
    # Order details from previous step
    subtotal: float
    
    # Delivery details
    delivery_address: str = Field(..., description="Full delivery address")
    delivery_time: str = Field(..., description="ASAP or scheduled time")
    
    # Payment
    payment_method: str = Field(..., description="Credit Card, PayPal, Cash")
    tip_percentage: int = Field(15, ge=0, le=50, description="Tip percentage")
    
    # Optional
    discount_code: Optional[str] = Field(None, description="Enter discount code if you have one")
    save_order_as_favorite: bool = Field(False, description="Save this order for quick reorder")


class CheckoutResponse(BaseModel):
    """Order confirmation"""
    order_id: str
    total_amount: float
    delivery_estimate: datetime
    order_status: str
    tracking_url: str
    confirmation_message: str


# Processors with actual logic
class RestaurantProcessor(FormStepProcessor):
    """Find restaurants based on location and preferences"""
    
    async def process(self, input_data: RestaurantSelectionRequest, chain_context: Dict[str, Any]) -> RestaurantSelectionResponse:
        # Simulate restaurant search
        restaurants = [
            {
                "name": "Luigi's Italian Kitchen",
                "cuisine": "Italian",
                "rating": 4.5,
                "delivery_time": "30-45 min",
                "menu_categories": ["Appetizers", "Pasta", "Pizza", "Beverages", "Desserts"]
            },
            {
                "name": "Dragon Palace",
                "cuisine": "Chinese",
                "rating": 4.3,
                "delivery_time": "25-40 min",
                "menu_categories": ["Starters", "Soups", "Main Dishes", "Rice & Noodles", "Beverages"]
            },
            {
                "name": "Burger Barn",
                "cuisine": "American",
                "rating": 4.7,
                "delivery_time": "20-30 min",
                "menu_categories": ["Starters", "Burgers", "Sandwiches", "Sides", "Beverages", "Shakes"]
            }
        ]
        
        # Filter by cuisine preference
        if "italian" in input_data.cuisine_preference.lower():
            restaurants = [r for r in restaurants if "Italian" in r["cuisine"]]
        elif "chinese" in input_data.cuisine_preference.lower():
            restaurants = [r for r in restaurants if "Chinese" in r["cuisine"]]
        
        # Pick the top restaurant
        recommended = restaurants[0] if restaurants else {
            "name": "Local Favorites",
            "menu_categories": ["Appetizers", "Main Courses", "Beverages"]
        }
        
        return RestaurantSelectionResponse(
            selected_location=input_data.location,
            available_restaurants=restaurants[:3],
            recommended_restaurant=recommended["name"],
            menu_categories=recommended.get("menu_categories", [])
        )


class OrderProcessor(FormStepProcessor):
    """Process the order and calculate totals"""
    
    async def process(self, input_data: OrderBuildRequest, chain_context: Dict[str, Any]) -> OrderBuildResponse:
        # Create order items with prices
        order_items = []
        
        # Simulated menu prices
        menu_prices = {
            "appetizers": {"Garlic Bread": 6.99, "Bruschetta": 8.99, "Caesar Salad": 7.99},
            "main_courses": {"Margherita Pizza": 14.99, "Spaghetti Carbonara": 16.99, "Chicken Parmigiana": 18.99},
            "beverages": {"Soda": 2.99, "Juice": 3.99, "Wine": 8.99}
        }
        
        # Add selected items
        for app in input_data.appetizers:
            if app in menu_prices["appetizers"]:
                order_items.append({"item": app, "price": menu_prices["appetizers"][app], "quantity": 1})
        
        for main in input_data.main_courses:
            price = random.uniform(12, 25)  # Simulate price
            order_items.append({"item": main, "price": round(price, 2), "quantity": 1})
        
        for bev in input_data.beverages:
            price = random.uniform(2, 8)  # Simulate price
            order_items.append({"item": bev, "price": round(price, 2), "quantity": 1})
        
        # Calculate subtotal
        subtotal = sum(item["price"] * item["quantity"] for item in order_items)
        
        # Estimate prep time based on number of items
        prep_time = 20 + (len(order_items) * 5)
        
        # Suggest add-ons
        suggested_addons = []
        if not any("Dessert" in item["item"] for item in order_items):
            suggested_addons.append("Tiramisu - $6.99")
        if len(input_data.beverages) == 0:
            suggested_addons.append("House Wine - $8.99")
        
        # Available discounts
        discounts = []
        if subtotal > 30:
            discounts.append({"code": "SAVE10", "description": "10% off orders over $30", "amount": 0.10})
        if len(order_items) >= 4:
            discounts.append({"code": "FEAST15", "description": "15% off 4+ items", "amount": 0.15})
        
        return OrderBuildResponse(
            order_items=order_items,
            subtotal=round(subtotal, 2),
            estimated_prep_time=prep_time,
            suggested_addons=suggested_addons,
            available_discounts=discounts
        )


class CheckoutProcessor(FormStepProcessor):
    """Complete the order and process payment"""
    
    async def process(self, input_data: CheckoutRequest, chain_context: Dict[str, Any]) -> CheckoutResponse:
        # Calculate final total
        subtotal = input_data.subtotal
        
        # Apply discount if provided
        discount_amount = 0
        if input_data.discount_code:
            # Get discounts from previous step
            prev_response = chain_context.get("step_2_response", {})
            available_discounts = prev_response.get("available_discounts", [])
            
            for discount in available_discounts:
                if discount["code"] == input_data.discount_code:
                    discount_amount = subtotal * discount["amount"]
                    break
        
        # Calculate tip
        tip_amount = subtotal * (input_data.tip_percentage / 100)
        
        # Total
        total = subtotal - discount_amount + tip_amount + 3.99  # delivery fee
        
        # Generate order ID
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Estimate delivery time
        prep_time = chain_context.get("step_2_response", {}).get("estimated_prep_time", 30)
        delivery_estimate = datetime.now().replace(
            minute=(datetime.now().minute + prep_time + 15) % 60
        )
        
        return CheckoutResponse(
            order_id=order_id,
            total_amount=round(total, 2),
            delivery_estimate=delivery_estimate,
            order_status="confirmed",
            tracking_url=f"/track/{order_id}",
            confirmation_message=f"Your order has been confirmed! Total: ${total:.2f}. Estimated delivery: {delivery_estimate.strftime('%I:%M %p')}"
        )


def create_restaurant_order_chain() -> FormChainEngine:
    """Create a simple restaurant ordering chain"""
    
    # Dynamic field injection for menu items
    def inject_menu_fields(response: RestaurantSelectionResponse) -> List[FormFieldSpec]:
        """Generate menu selection fields based on restaurant"""
        
        fields = []
        
        # Create menu items based on restaurant
        if "Italian" in response.recommended_restaurant:
            menu_items = {
                "appetizers": ["Garlic Bread", "Bruschetta", "Caprese Salad", "Calamari"],
                "main_courses": ["Margherita Pizza", "Pepperoni Pizza", "Spaghetti Carbonara", "Lasagna", "Chicken Parmigiana"],
                "beverages": ["Soda", "Sparkling Water", "House Wine", "Espresso"]
            }
        elif "Chinese" in response.recommended_restaurant:
            menu_items = {
                "appetizers": ["Spring Rolls", "Dumplings", "Hot & Sour Soup"],
                "main_courses": ["Kung Pao Chicken", "Sweet & Sour Pork", "Beef Broccoli", "Fried Rice"],
                "beverages": ["Tea", "Soda", "Fresh Juice"]
            }
        else:
            menu_items = {
                "appetizers": ["Onion Rings", "Mozzarella Sticks", "Wings"],
                "main_courses": ["Classic Burger", "BBQ Burger", "Grilled Chicken Sandwich"],
                "beverages": ["Soda", "Milkshake", "Iced Tea"]
            }
        
        # Create checkbox fields for each category
        for category, items in menu_items.items():
            for item in items:
                fields.append(
                    FormFieldSpec(
                        name=f"{category}_{item.replace(' ', '_').lower()}",
                        field_type=FieldType.CHECKBOX,
                        label=f"{item}",
                        help_text=f"Add {item} to your order",
                        default=False
                    )
                )
        
        return fields
    
    # Dynamic discount code field
    def inject_checkout_fields(response: OrderBuildResponse) -> List[FormFieldSpec]:
        """Add discount options to checkout"""
        
        fields = []
        
        if response.available_discounts:
            # Create a select field with available discounts
            discount_options = [{"value": "", "label": "No discount"}]
            for discount in response.available_discounts:
                discount_options.append({
                    "value": discount["code"],
                    "label": f"{discount['code']} - {discount['description']}"
                })
            
            fields.append(
                FormFieldSpec(
                    name="available_discounts_info",
                    field_type=FieldType.SELECT,
                    label="Available Discounts",
                    options=discount_options,
                    help_text="Select a discount code to apply",
                    required=False
                )
            )
        
        return fields
    
    steps = [
        FormStep(
            id="step_1",
            title="Find Restaurants",
            description="Tell us where you are and what you're craving",
            request_model=RestaurantSelectionRequest,
            response_model=RestaurantSelectionResponse,
            processor=RestaurantProcessor(),
            is_entry_point=True,
            next_step_id="step_2"
        ),
        FormStep(
            id="step_2",
            title="Build Your Order",
            description="Select items from the menu",
            request_model=OrderBuildRequest,
            response_model=OrderBuildResponse,
            processor=OrderProcessor(),
            next_step_id="step_3",
            inject_fields=inject_menu_fields
        ),
        FormStep(
            id="step_3",
            title="Checkout",
            description="Complete your order and arrange delivery",
            request_model=CheckoutRequest,
            response_model=CheckoutResponse,
            processor=CheckoutProcessor(),
            is_exit_point=True,
            inject_fields=inject_checkout_fields
        )
    ]
    
    return FormChainEngine(
        chain_id="restaurant_order",
        title="🍕 Restaurant Order System",
        description="Order food from local restaurants with our smart ordering system",
        steps=steps,
        theme="modern"
    )


# Quick test script
if __name__ == "__main__":
    import asyncio
    
    async def test_chain():
        print("Testing Restaurant Order Chain")
        print("=" * 50)
        
        # Create the chain
        chain = create_restaurant_order_chain()
        
        # Generate entry form
        entry_form = chain.generate_form_html("step_1")
        
        # Save to file
        with open("/var/www/ai_apps/playground/restaurant_order_example.html", "w") as f:
            f.write(entry_form)
        
        print("✅ Restaurant order form saved to restaurant_order_example.html")
        print("\nThis example demonstrates:")
        print("- Dynamic menu generation based on restaurant selection")
        print("- Order calculation with pricing")
        print("- Discount code injection based on order value")
        print("- Complete order flow from restaurant selection to checkout")
    
    asyncio.run(test_chain())