#!/usr/bin/env python3
"""
Smart Shopping Assistant - Real-World Use Case

This demonstrates how unstructured WhatsApp conversations can be transformed
into actionable shopping workflows using AI-powered form chains.

Features:
- Natural language understanding of shopping items
- Smart categorization and suggestions
- Multi-channel integration (WhatsApp, SMS, Web)
- Real-time inventory checking
- Recipe suggestions based on ingredients
- Family preference learning
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import json

from html_v3_ai import (
    ConversationFormBridge, MockLLMProvider, ConversationContext,
    LLMProvider, ConversationIntent
)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from html_v3 import FormChainEngine, FormStep, FormStepProcessor


class ShoppingCategory(str, Enum):
    PRODUCE = "produce"
    DAIRY = "dairy"
    MEAT = "meat"
    PANTRY = "pantry"
    FROZEN = "frozen"
    BEVERAGES = "beverages"
    HOUSEHOLD = "household"
    PERSONAL_CARE = "personal_care"


class Store(str, Enum):
    WHOLE_FOODS = "whole_foods"
    TRADER_JOES = "trader_joes"
    SAFEWAY = "safeway"
    TARGET = "target"
    COSTCO = "costco"
    LOCAL_MARKET = "local_market"


class SmartShoppingLLM(MockLLMProvider):
    """Enhanced LLM provider for shopping assistant"""
    
    def __init__(self):
        super().__init__()
        # Simulated knowledge base
        self.item_categories = {
            "cabbage": ShoppingCategory.PRODUCE,
            "tomato paste": ShoppingCategory.PANTRY,
            "celery": ShoppingCategory.PRODUCE,
            "bell pepper": ShoppingCategory.PRODUCE,
            "yogurt": ShoppingCategory.DAIRY,
            "milk": ShoppingCategory.DAIRY,
            "onions": ShoppingCategory.PRODUCE,
            "garlic": ShoppingCategory.PRODUCE,
            "vegetable broth": ShoppingCategory.PANTRY,
            "chicken broth": ShoppingCategory.PANTRY,
            "olive oil": ShoppingCategory.PANTRY,
            "butter": ShoppingCategory.DAIRY,
            "salt": ShoppingCategory.PANTRY,
            "pepper": ShoppingCategory.PANTRY,
            "bread": ShoppingCategory.PANTRY,
            "eggs": ShoppingCategory.DAIRY,
            "cheese": ShoppingCategory.DAIRY
        }
        
        self.recipe_database = {
            "vegetable_soup": {
                "name": "Classic Vegetable Soup",
                "ingredients": [
                    "cabbage", "celery", "bell pepper", "onions", "garlic",
                    "tomato paste", "vegetable broth", "olive oil", "salt", "pepper"
                ],
                "time": "45 minutes",
                "servings": 6
            },
            "minestrone": {
                "name": "Hearty Minestrone",
                "ingredients": [
                    "cabbage", "celery", "tomato paste", "beans", "pasta",
                    "vegetable broth", "onions", "garlic", "olive oil"
                ],
                "time": "1 hour",
                "servings": 8
            }
        }
        
        self.family_preferences = {
            "dietary_restrictions": ["vegetarian"],
            "favorite_meals": ["soup", "salad", "pasta"],
            "dislikes": ["spicy food", "seafood"],
            "usual_stores": [Store.WHOLE_FOODS, Store.TRADER_JOES]
        }
    
    async def analyze_conversation(self, context: ConversationContext) -> Dict[str, Any]:
        """Enhanced conversation analysis with shopping intelligence"""
        
        # Get base analysis
        base_analysis = await super().analyze_conversation(context)
        
        # Enhance with shopping-specific insights
        entities = base_analysis["entities"]
        
        # Categorize items
        categorized_items = {}
        for item in entities.get("items", []):
            category = self.item_categories.get(item.lower(), ShoppingCategory.PANTRY)
            if category not in categorized_items:
                categorized_items[category] = []
            categorized_items[category].append(item)
        
        entities["categorized_items"] = categorized_items
        
        # Check for recipe matches
        possible_recipes = []
        item_set = set(item.lower() for item in entities.get("items", []))
        
        for recipe_id, recipe in self.recipe_database.items():
            match_score = len(item_set.intersection(recipe["ingredients"])) / len(recipe["ingredients"])
            if match_score > 0.5:  # More than 50% ingredients match
                possible_recipes.append({
                    "id": recipe_id,
                    "name": recipe["name"],
                    "match_score": match_score,
                    "missing_ingredients": list(set(recipe["ingredients"]) - item_set)
                })
        
        entities["possible_recipes"] = sorted(possible_recipes, key=lambda x: x["match_score"], reverse=True)
        
        # Add store recommendations
        entities["recommended_stores"] = self._recommend_stores(categorized_items)
        
        # Estimate total cost
        entities["estimated_cost"] = self._estimate_cost(entities.get("items", []))
        
        return {
            **base_analysis,
            "entities": entities,
            "insights": {
                "meal_planning": "Looks like you're making soup!",
                "missing_staples": self._check_missing_staples(entities),
                "bulk_buying_opportunities": self._find_bulk_opportunities(entities)
            }
        }
    
    def _recommend_stores(self, categorized_items: Dict[ShoppingCategory, List[str]]) -> List[Dict[str, Any]]:
        """Recommend best stores based on items"""
        
        recommendations = []
        
        # Check if mostly produce
        produce_count = len(categorized_items.get(ShoppingCategory.PRODUCE, []))
        total_count = sum(len(items) for items in categorized_items.values())
        
        if produce_count / total_count > 0.6:
            recommendations.append({
                "store": Store.LOCAL_MARKET,
                "reason": "Best prices and freshness for produce",
                "estimated_savings": "15-20%"
            })
        
        # Check for bulk items
        if total_count > 10:
            recommendations.append({
                "store": Store.COSTCO,
                "reason": "Bulk buying for large shopping list",
                "estimated_savings": "25-30%"
            })
        
        # Default recommendation
        recommendations.append({
            "store": Store.WHOLE_FOODS,
            "reason": "Quality ingredients for soup making",
            "estimated_savings": "0%"
        })
        
        return recommendations[:2]
    
    def _estimate_cost(self, items: List[str]) -> Dict[str, float]:
        """Estimate shopping cost"""
        
        # Simplified price estimation
        price_map = {
            "produce": 2.50,
            "dairy": 3.50,
            "pantry": 2.00,
            "meat": 8.00
        }
        
        total = 0
        for item in items:
            category = self.item_categories.get(item.lower(), ShoppingCategory.PANTRY)
            if category == ShoppingCategory.PRODUCE:
                total += price_map["produce"]
            elif category == ShoppingCategory.DAIRY:
                total += price_map["dairy"]
            else:
                total += price_map["pantry"]
        
        return {
            "low_estimate": total * 0.8,
            "high_estimate": total * 1.2,
            "average": total
        }
    
    def _check_missing_staples(self, entities: Dict[str, Any]) -> List[str]:
        """Check for commonly needed staples"""
        
        current_items = set(item.lower() for item in entities.get("items", []))
        
        # Common soup staples
        soup_staples = {"onions", "garlic", "salt", "pepper", "olive oil", "broth"}
        
        if entities.get("meal_type") == "soup":
            missing = list(soup_staples - current_items)
            return missing[:3]  # Return top 3 missing
        
        return []
    
    def _find_bulk_opportunities(self, entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Find items that could be bought in bulk"""
        
        bulk_items = []
        
        # Check for non-perishables
        pantry_items = entities.get("categorized_items", {}).get(ShoppingCategory.PANTRY, [])
        if pantry_items:
            bulk_items.append({
                "items": pantry_items,
                "suggestion": "Buy these in bulk for 20-30% savings",
                "storage_tip": "Store in airtight containers"
            })
        
        return bulk_items


class ShoppingWorkflowEngine:
    """Complete shopping workflow management"""
    
    def __init__(self):
        self.llm = SmartShoppingLLM()
        self.bridge = ConversationFormBridge(self.llm)
        self.active_lists: Dict[str, Dict[str, Any]] = {}
    
    async def create_shopping_workflow(
        self,
        user_id: str,
        conversation: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Create complete shopping workflow from conversation"""
        
        # Process conversation
        for msg in conversation:
            response = await self.bridge.process_message(
                user_id,
                msg["content"],
                datetime.now()
            )
        
        # Get context with all analysis
        context = self.bridge.get_context(user_id)
        
        # Create enhanced shopping list
        shopping_list = await self._create_enhanced_list(context)
        
        # Store active list
        self.active_lists[user_id] = shopping_list
        
        return {
            "shopping_list": shopping_list,
            "workflow_id": f"shop_{user_id}_{datetime.now().strftime('%Y%m%d%H%M')}",
            "next_steps": [
                "review_list",
                "check_inventory",
                "compare_prices",
                "place_order"
            ]
        }
    
    async def _create_enhanced_list(self, context: ConversationContext) -> Dict[str, Any]:
        """Create enhanced shopping list with categories and insights"""
        
        entities = context.entities
        
        return {
            "items_by_category": entities.get("categorized_items", {}),
            "total_items": len(entities.get("items", [])),
            "estimated_cost": entities.get("estimated_cost", {}),
            "recommended_stores": entities.get("recommended_stores", []),
            "possible_recipes": entities.get("possible_recipes", []),
            "missing_staples": self.llm._check_missing_staples(entities),
            "created_at": datetime.now().isoformat(),
            "family_preferences": self.llm.family_preferences
        }
    
    async def check_inventory(self, user_id: str) -> Dict[str, Any]:
        """Check home inventory against shopping list"""
        
        # Simulated home inventory
        home_inventory = {
            "salt": {"quantity": "plenty", "expires": None},
            "olive oil": {"quantity": "half bottle", "expires": "2024-06"},
            "garlic": {"quantity": "3 cloves", "expires": "2024-01-20"},
            "onions": {"quantity": "2", "expires": "2024-01-25"}
        }
        
        shopping_list = self.active_lists.get(user_id, {})
        all_items = []
        for items in shopping_list.get("items_by_category", {}).values():
            all_items.extend(items)
        
        # Check what we already have
        already_have = []
        need_soon = []
        
        for item in all_items:
            if item.lower() in home_inventory:
                inv = home_inventory[item.lower()]
                if inv["quantity"] == "plenty":
                    already_have.append(item)
                else:
                    need_soon.append({
                        "item": item,
                        "current": inv["quantity"],
                        "expires": inv["expires"]
                    })
        
        return {
            "already_have": already_have,
            "need_soon": need_soon,
            "definitely_need": [item for item in all_items if item.lower() not in home_inventory]
        }
    
    async def generate_meal_plan(self, user_id: str) -> Dict[str, Any]:
        """Generate meal plan based on shopping list"""
        
        shopping_list = self.active_lists.get(user_id, {})
        recipes = shopping_list.get("possible_recipes", [])
        
        meal_plan = {
            "monday": {
                "lunch": "Leftover soup",
                "dinner": recipes[0]["name"] if recipes else "Vegetable Stir-fry"
            },
            "tuesday": {
                "lunch": "Soup and salad",
                "dinner": "Pasta with vegetables"
            },
            "wednesday": {
                "lunch": "Leftover pasta",
                "dinner": "Grilled vegetables with rice"
            }
        }
        
        return {
            "meal_plan": meal_plan,
            "recipes_included": recipes[:2] if recipes else [],
            "prep_tips": [
                "Prep vegetables on Sunday for the week",
                "Make double batch of soup for leftovers",
                "Pre-cook grains for quick meals"
            ]
        }


async def demonstrate_shopping_workflow():
    """Full demonstration of the shopping assistant"""
    
    print("🛒 Smart Shopping Assistant Demo")
    print("="*60)
    
    # Mom's messages
    conversation = [
        {"content": "Cabbage, tomato paste, celery, red & green bell pepper"},
        {"content": "Anything else you want in the soup"},
        {"content": "Yogurt & milk please"}
    ]
    
    # Create workflow engine
    engine = ShoppingWorkflowEngine()
    
    # Process conversation
    print("\n1. Processing conversation...")
    workflow = await engine.create_shopping_workflow("mom", conversation)
    
    print(f"\n✅ Workflow created: {workflow['workflow_id']}")
    
    # Show shopping list insights
    shopping_list = workflow["shopping_list"]
    print("\n2. Shopping List Analysis:")
    print(f"   Total items: {shopping_list['total_items']}")
    print(f"   Estimated cost: ${shopping_list['estimated_cost'].get('average', 0):.2f}")
    
    print("\n   Items by category:")
    for category, items in shopping_list["items_by_category"].items():
        print(f"   - {category.value}: {', '.join(items)}")
    
    print("\n   Recommended stores:")
    for store in shopping_list["recommended_stores"][:2]:
        print(f"   - {store['store'].value}: {store['reason']}")
    
    print("\n   Possible recipes:")
    for recipe in shopping_list["possible_recipes"][:2]:
        print(f"   - {recipe['name']} ({recipe['match_score']*100:.0f}% match)")
        if recipe["missing_ingredients"]:
            print(f"     Missing: {', '.join(recipe['missing_ingredients'][:3])}")
    
    # Check inventory
    print("\n3. Checking home inventory...")
    inventory = await engine.check_inventory("mom")
    
    if inventory["already_have"]:
        print(f"   Already have: {', '.join(inventory['already_have'])}")
    if inventory["need_soon"]:
        print("   Running low on:")
        for item in inventory["need_soon"]:
            print(f"   - {item['item']}: {item['current']}")
    
    # Generate meal plan
    print("\n4. Generating meal plan...")
    meal_plan = await engine.generate_meal_plan("mom")
    
    print("   Meal suggestions:")
    for day, meals in list(meal_plan["meal_plan"].items())[:2]:
        print(f"   {day.capitalize()}:")
        print(f"   - Dinner: {meals['dinner']}")
    
    print("\n5. Next Actions:")
    print("   a) Review and edit list")
    print("   b) Compare prices across stores")
    print("   c) Schedule delivery or pickup")
    print("   d) Share list with family")
    
    # Save detailed report
    report = {
        "workflow": workflow,
        "inventory_check": inventory,
        "meal_plan": meal_plan,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("shopping_workflow_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\n📄 Full report saved to: shopping_workflow_report.json")


class ShoppingFormGenerator:
    """Generate interactive forms for shopping workflow"""
    
    @staticmethod
    def create_review_form(shopping_list: Dict[str, Any]) -> str:
        """Create an interactive review form for the shopping list"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Smart Shopping List Review</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f6fa;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }}
        
        .cost-estimate {{
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .category {{
            margin-bottom: 30px;
        }}
        
        .category-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .category-icon {{
            font-size: 24px;
            margin-right: 10px;
        }}
        
        .category-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            flex: 1;
        }}
        
        .item {{
            display: flex;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.2s;
        }}
        
        .item:hover {{
            background: #e9ecef;
            transform: translateX(5px);
        }}
        
        .item-checkbox {{
            margin-right: 15px;
            width: 20px;
            height: 20px;
        }}
        
        .item-name {{
            flex: 1;
            font-size: 16px;
        }}
        
        .item-quantity {{
            margin-left: 10px;
            padding: 4px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 60px;
            text-align: center;
        }}
        
        .suggestions {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        .recipe-card {{
            background: #d1f2eb;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        .store-recommendation {{
            display: flex;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        .store-logo {{
            font-size: 32px;
            margin-right: 15px;
        }}
        
        .actions {{
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }}
        
        .btn {{
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #5a67d8;
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: #e9ecef;
            color: #495057;
        }}
        
        @media (max-width: 600px) {{
            .actions {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛒 Your Smart Shopping List</h1>
            <div class="cost-estimate">
                <strong>Estimated Cost:</strong> ${shopping_list['estimated_cost']['low_estimate']:.2f} - ${shopping_list['estimated_cost']['high_estimate']:.2f}
            </div>
        </div>
        
        <div class="content">
"""
        
        # Add categories
        icons = {
            ShoppingCategory.PRODUCE: "🥬",
            ShoppingCategory.DAIRY: "🥛",
            ShoppingCategory.PANTRY: "🥫",
            ShoppingCategory.MEAT: "🥩",
            ShoppingCategory.FROZEN: "❄️",
            ShoppingCategory.BEVERAGES: "🥤"
        }
        
        for category, items in shopping_list.get("items_by_category", {}).items():
            if items:
                html += f"""
            <div class="category">
                <div class="category-header">
                    <span class="category-icon">{icons.get(category, "📦")}</span>
                    <span class="category-title">{category.value.replace('_', ' ').title()}</span>
                </div>
"""
                for item in items:
                    html += f"""
                <div class="item">
                    <input type="checkbox" class="item-checkbox" checked>
                    <span class="item-name">{item.title()}</span>
                    <input type="number" class="item-quantity" value="1" min="1">
                </div>
"""
                html += "            </div>\n"
        
        # Add suggestions
        if shopping_list.get("missing_staples"):
            html += """
            <div class="suggestions">
                <h3>🤔 Don't forget these staples:</h3>
"""
            for item in shopping_list["missing_staples"]:
                html += f'                <div class="item"><input type="checkbox" class="item-checkbox"><span class="item-name">{item.title()}</span></div>\n'
            html += "            </div>\n"
        
        # Add recipes
        if shopping_list.get("possible_recipes"):
            html += """
            <h3>👨‍🍳 Recipe Suggestions:</h3>
"""
            for recipe in shopping_list["possible_recipes"][:2]:
                html += f"""
            <div class="recipe-card">
                <strong>{recipe['name']}</strong><br>
                Match: {recipe['match_score']*100:.0f}%<br>
                {f"Missing: {', '.join(recipe['missing_ingredients'][:3])}" if recipe['missing_ingredients'] else "You have all ingredients!"}
            </div>
"""
        
        # Add store recommendations
        html += """
            <h3>🏪 Recommended Stores:</h3>
"""
        store_icons = {
            Store.WHOLE_FOODS: "🌿",
            Store.TRADER_JOES: "🌺",
            Store.COSTCO: "📦",
            Store.LOCAL_MARKET: "🏪"
        }
        
        for store in shopping_list.get("recommended_stores", [])[:2]:
            html += f"""
            <div class="store-recommendation">
                <span class="store-logo">{store_icons.get(store['store'], '🏪')}</span>
                <div>
                    <strong>{store['store'].value.replace('_', ' ').title()}</strong><br>
                    <small>{store['reason']}</small>
                </div>
            </div>
"""
        
        # Add actions
        html += """
            <div class="actions">
                <button class="btn btn-secondary" onclick="shareList()">📤 Share List</button>
                <button class="btn btn-primary" onclick="proceedToOrder()">🚀 Order Now</button>
            </div>
        </div>
    </div>
    
    <script>
        function shareList() {
            if (navigator.share) {
                navigator.share({
                    title: 'Shopping List',
                    text: 'Check out my smart shopping list!',
                    url: window.location.href
                });
            } else {
                alert('Sharing not supported on this device');
            }
        }
        
        function proceedToOrder() {
            alert('Proceeding to store selection and ordering...');
            // In real app, would proceed to next step
        }
        
        // Save changes to localStorage
        document.querySelectorAll('.item-checkbox, .item-quantity').forEach(element => {
            element.addEventListener('change', saveList);
        });
        
        function saveList() {
            const items = [];
            document.querySelectorAll('.item').forEach(item => {
                const checkbox = item.querySelector('.item-checkbox');
                if (checkbox.checked) {
                    items.push({
                        name: item.querySelector('.item-name').textContent,
                        quantity: item.querySelector('.item-quantity')?.value || 1
                    });
                }
            });
            localStorage.setItem('shopping_list', JSON.stringify(items));
        }
    </script>
</body>
</html>
"""
        
        return html


if __name__ == "__main__":
    # Run shopping workflow demo
    asyncio.run(demonstrate_shopping_workflow())
    
    # Generate interactive form
    print("\n\n🎨 Generating interactive shopping form...")
    
    # Create sample shopping list
    sample_list = {
        "items_by_category": {
            ShoppingCategory.PRODUCE: ["cabbage", "celery", "bell pepper"],
            ShoppingCategory.DAIRY: ["yogurt", "milk"],
            ShoppingCategory.PANTRY: ["tomato paste"]
        },
        "estimated_cost": {"low_estimate": 18.50, "high_estimate": 25.00},
        "missing_staples": ["onions", "garlic", "olive oil"],
        "possible_recipes": [
            {"name": "Vegetable Soup", "match_score": 0.7, "missing_ingredients": ["onions", "garlic"]},
            {"name": "Minestrone", "match_score": 0.6, "missing_ingredients": ["beans", "pasta"]}
        ],
        "recommended_stores": [
            {"store": Store.LOCAL_MARKET, "reason": "Best produce prices"},
            {"store": Store.WHOLE_FOODS, "reason": "Quality ingredients"}
        ]
    }
    
    form_html = ShoppingFormGenerator.create_review_form(sample_list)
    
    with open("shopping_list_review.html", "w") as f:
        f.write(form_html)
    
    print("✅ Interactive form saved to: shopping_list_review.html")