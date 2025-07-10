#!/usr/bin/env python3
"""
HTML v3 AI Integration Layer - Augmenting Form Chains with LLM Intelligence

This module transforms html_v3 into an AI-powered dynamic user interaction platform
by integrating with modern LLMs (ChatGPT, Gemini, Claude) to:

1. Convert unstructured conversations into structured form chains
2. Dynamically generate and adapt forms based on AI analysis
3. Maintain conversation context across multi-step workflows
4. Execute real-world actions based on natural language inputs

The shopping example: Converting mom's WhatsApp messages into actionable workflows
"""

import json
import re
from typing import Dict, List, Any, Optional, Union, Type, Tuple
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from pydantic import BaseModel, Field, create_model

# Import the core html_v3 engine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from html_v3 import (
    FormChainEngine, FormStep, FormStepProcessor, FormFieldSpec,
    FieldType, create_form_chain
)

# LLM provider configuration
@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str  # "openai", "anthropic", "google"
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000


class ConversationIntent(Enum):
    """Types of intents extracted from conversations"""
    SHOPPING = "shopping"
    INQUIRY = "inquiry"
    BOOKING = "booking"
    SUPPORT = "support"
    MEDICAL = "medical"
    FINANCIAL = "financial"
    EDUCATIONAL = "educational"
    GENERAL = "general"


@dataclass
class ConversationContext:
    """Maintains context across conversation turns"""
    messages: List[Dict[str, str]]
    intent: Optional[ConversationIntent] = None
    entities: Dict[str, Any] = None
    current_step: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}
        if self.metadata is None:
            self.metadata = {}


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def analyze_conversation(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze conversation and extract structured data"""
        pass
    
    @abstractmethod
    async def generate_form_schema(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate form schema based on conversation"""
        pass
    
    @abstractmethod
    async def process_response(self, user_input: str, context: ConversationContext) -> Dict[str, Any]:
        """Process user response and update context"""
        pass


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for demonstration"""
    
    async def analyze_conversation(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze conversation patterns"""
        
        # Analyze the shopping example
        messages_text = " ".join([m["content"] for m in context.messages])
        
        # Extract entities using simple patterns (in production, use actual LLM)
        entities = {
            "items": [],
            "categories": [],
            "preferences": [],
            "urgency": "normal"
        }
        
        # Extract food items
        food_patterns = [
            r'\b(cabbage|tomato paste|celery|bell pepper|yogurt|milk)\b',
            r'\b(red|green)\s+bell pepper\b',
            r'\byog?h?urt\b'  # Handle spelling variations
        ]
        
        for pattern in food_patterns:
            matches = re.findall(pattern, messages_text.lower())
            entities["items"].extend(matches)
        
        # Detect intent
        if any(word in messages_text.lower() for word in ["soup", "recipe", "cooking"]):
            entities["categories"].append("ingredients")
            entities["meal_type"] = "soup"
        
        # Check for questions
        if "anything else" in messages_text.lower():
            entities["is_open_ended"] = True
        
        return {
            "intent": ConversationIntent.SHOPPING,
            "entities": entities,
            "confidence": 0.95,
            "suggested_actions": ["create_shopping_list", "suggest_recipes", "check_inventory"]
        }
    
    async def generate_form_schema(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate dynamic form schema based on conversation"""
        
        analysis = await self.analyze_conversation(context)
        entities = analysis["entities"]
        
        # Create form fields based on extracted entities
        fields = []
        
        # Add existing items as pre-filled fields
        if entities.get("items"):
            fields.append({
                "name": "shopping_items",
                "type": "array",
                "label": "Shopping List Items",
                "default": list(set(entities["items"])),  # Remove duplicates
                "help_text": "Items mentioned in the conversation"
            })
        
        # Add category-specific fields
        if "soup" in entities.get("meal_type", ""):
            fields.extend([
                {
                    "name": "soup_type",
                    "type": "select",
                    "label": "What type of soup are you making?",
                    "options": ["vegetable", "chicken", "beef", "seafood", "other"],
                    "required": False
                },
                {
                    "name": "servings",
                    "type": "number",
                    "label": "How many servings?",
                    "default": 4,
                    "min": 1,
                    "max": 20
                }
            ])
        
        # Add open-ended field if conversation suggests it
        if entities.get("is_open_ended"):
            fields.append({
                "name": "additional_items",
                "type": "textarea",
                "label": "Anything else you'd like to add?",
                "placeholder": "Enter any additional items or preferences...",
                "required": False
            })
        
        # Add smart suggestions
        fields.append({
            "name": "suggested_items",
            "type": "checkbox_group",
            "label": "You might also need:",
            "options": self._get_smart_suggestions(entities),
            "required": False
        })
        
        return {
            "title": "Smart Shopping Assistant",
            "description": "Based on your conversation, here's your shopping list",
            "fields": fields,
            "actions": ["save_list", "order_online", "share_list", "get_recipes"]
        }
    
    async def process_response(self, user_input: str, context: ConversationContext) -> Dict[str, Any]:
        """Process user response and update context"""
        
        # Add response to context
        context.messages.append({"role": "user", "content": user_input})
        
        # Extract new items from response
        new_items = re.findall(r'\b\w+\b', user_input.lower())
        
        # Update entities
        if context.entities is None:
            context.entities = {}
        
        current_items = context.entities.get("items", [])
        current_items.extend(new_items)
        context.entities["items"] = list(set(current_items))
        
        return {
            "updated_context": context,
            "suggested_next_action": "update_form",
            "confidence": 0.9
        }
    
    def _get_smart_suggestions(self, entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get smart item suggestions based on context"""
        
        suggestions = []
        
        # If making soup, suggest common soup ingredients
        if entities.get("meal_type") == "soup":
            soup_items = [
                {"value": "onions", "label": "Onions"},
                {"value": "garlic", "label": "Garlic"},
                {"value": "vegetable_broth", "label": "Vegetable Broth"},
                {"value": "salt", "label": "Salt"},
                {"value": "black_pepper", "label": "Black Pepper"},
                {"value": "olive_oil", "label": "Olive Oil"}
            ]
            
            # Only suggest items not already in the list
            current_items = [item.lower() for item in entities.get("items", [])]
            suggestions = [
                item for item in soup_items 
                if item["value"] not in current_items
            ]
        
        return suggestions[:6]  # Limit to 6 suggestions


class AIFormChainGenerator:
    """Generates form chains from conversations using AI"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    async def create_form_chain_from_conversation(
        self,
        conversation: List[Dict[str, str]],
        chain_id: str,
        title: str
    ) -> FormChainEngine:
        """Create a complete form chain from a conversation"""
        
        # Create conversation context
        context = ConversationContext(messages=conversation)
        
        # Analyze conversation
        analysis = await self.llm_provider.analyze_conversation(context)
        context.intent = analysis["intent"]
        context.entities = analysis["entities"]
        
        # Generate form schema
        schema = await self.llm_provider.generate_form_schema(context)
        
        # Create form steps based on schema
        steps = await self._create_form_steps(schema, context)
        
        # Create and return form chain
        return FormChainEngine(
            chain_id=chain_id,
            title=title,
            description=schema.get("description", "AI-generated form"),
            steps=steps,
            theme="modern"
        )
    
    async def _create_form_steps(
        self,
        schema: Dict[str, Any],
        context: ConversationContext
    ) -> List[FormStep]:
        """Create form steps from schema"""
        
        steps = []
        
        # Create dynamic Pydantic models for each step
        # Step 1: Initial data collection
        step1_fields = {}
        for field in schema["fields"]:
            field_type = self._get_python_type(field["type"])
            default = field.get("default", ...)
            
            if field.get("required", True):
                step1_fields[field["name"]] = (field_type, Field(default, description=field.get("help_text", "")))
            else:
                step1_fields[field["name"]] = (Optional[field_type], Field(default, description=field.get("help_text", "")))
        
        # Create request model dynamically
        Step1Request = create_model("Step1Request", **step1_fields)
        Step1Response = create_model(
            "Step1Response",
            items_confirmed=(List[str], Field(...)),
            next_action=(str, Field(...))
        )
        
        # Create processor
        processor = ShoppingListProcessor(self.llm_provider, context)
        
        steps.append(
            FormStep(
                id="collect_items",
                title="Review Your Shopping List",
                description=schema["description"],
                request_model=Step1Request,
                response_model=Step1Response,
                processor=processor,
                is_entry_point=True,
                next_step_id="confirm_action"
            )
        )
        
        # Step 2: Action selection
        ActionRequest = create_model(
            "ActionRequest",
            action=(str, Field(..., description="What would you like to do?")),
            delivery_preference=(Optional[str], Field(None)),
            share_with=(Optional[str], Field(None))
        )
        
        ActionResponse = create_model(
            "ActionResponse",
            success=(bool, Field(...)),
            message=(str, Field(...)),
            order_id=(Optional[str], Field(None))
        )
        
        steps.append(
            FormStep(
                id="confirm_action",
                title="Choose Action",
                description="What would you like to do with your shopping list?",
                request_model=ActionRequest,
                response_model=ActionResponse,
                processor=ActionProcessor(),
                is_exit_point=True
            )
        )
        
        return steps
    
    def _get_python_type(self, field_type: str) -> Type:
        """Convert field type string to Python type"""
        type_map = {
            "text": str,
            "textarea": str,
            "number": int,
            "array": List[str],
            "select": str,
            "checkbox_group": List[str],
            "boolean": bool,
            "date": str,  # Could use date type
            "email": str
        }
        return type_map.get(field_type, str)


class ShoppingListProcessor(FormStepProcessor):
    """Processes shopping list form submissions"""
    
    def __init__(self, llm_provider: LLMProvider, context: ConversationContext):
        self.llm_provider = llm_provider
        self.context = context
    
    async def process(self, input_data: BaseModel, chain_context: Dict[str, Any]) -> BaseModel:
        """Process the shopping list form"""
        
        # Extract all items from the form
        all_items = []
        
        # Get items from different fields
        if hasattr(input_data, 'shopping_items'):
            all_items.extend(input_data.shopping_items)
        
        if hasattr(input_data, 'additional_items') and input_data.additional_items:
            # Parse additional items
            additional = input_data.additional_items.split(',')
            all_items.extend([item.strip() for item in additional])
        
        if hasattr(input_data, 'suggested_items'):
            all_items.extend(input_data.suggested_items)
        
        # Remove duplicates and empty items
        all_items = list(set(item for item in all_items if item))
        
        # Create response
        response_model = type(self).process.__annotations__['return']
        return response_model(
            items_confirmed=all_items,
            next_action="choose_action"
        )


class ActionProcessor(FormStepProcessor):
    """Processes action selection"""
    
    async def process(self, input_data: BaseModel, chain_context: Dict[str, Any]) -> BaseModel:
        """Process the selected action"""
        
        # Get previous step data
        items = chain_context.get("step_collect_items_response", {}).get("items_confirmed", [])
        
        # Simulate action execution
        if input_data.action == "order_online":
            # Simulate online order
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            message = f"Order placed successfully! {len(items)} items will be delivered."
            success = True
        elif input_data.action == "save_list":
            message = f"Shopping list saved with {len(items)} items."
            order_id = None
            success = True
        elif input_data.action == "share_list":
            recipient = getattr(input_data, 'share_with', 'contacts')
            message = f"Shopping list shared with {recipient}."
            order_id = None
            success = True
        else:
            message = "Action completed."
            order_id = None
            success = True
        
        response_model = type(self).process.__annotations__['return']
        return response_model(
            success=success,
            message=message,
            order_id=order_id
        )


class ConversationFormBridge:
    """Bridge between conversational AI and form chains"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.generator = AIFormChainGenerator(llm_provider)
        self.active_contexts: Dict[str, ConversationContext] = {}
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Process a user message and return appropriate response"""
        
        # Get or create context
        if user_id not in self.active_contexts:
            self.active_contexts[user_id] = ConversationContext(messages=[])
        
        context = self.active_contexts[user_id]
        
        # Add message to context
        context.messages.append({
            "role": "user",
            "content": message,
            "timestamp": (timestamp or datetime.now()).isoformat()
        })
        
        # Analyze message
        response = await self.llm_provider.process_response(message, context)
        
        # Determine action
        if len(context.messages) >= 3 or "please" in message.lower():
            # Create form chain
            chain = await self.generator.create_form_chain_from_conversation(
                context.messages,
                f"shopping_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "Smart Shopping List"
            )
            
            # Generate initial form
            entry_point = chain.get_entry_point()
            form_html = chain.generate_form_html(entry_point.id)
            
            return {
                "type": "form",
                "form_html": form_html,
                "chain_id": chain.chain_id,
                "message": "I've created a shopping list based on our conversation. Please review and confirm."
            }
        else:
            # Continue conversation
            return {
                "type": "conversation",
                "message": "Got it! Anything else for your shopping list?",
                "entities_found": response["updated_context"].entities.get("items", [])
            }
    
    def get_context(self, user_id: str) -> Optional[ConversationContext]:
        """Get conversation context for a user"""
        return self.active_contexts.get(user_id)


# Utility functions
def create_shopping_assistant_demo():
    """Create a demo of the shopping assistant with mom's messages"""
    
    # Mom's WhatsApp messages
    messages = [
        {"role": "user", "content": "Cabbage, tomato paste, celery, red & green bell pepper", "timestamp": "17:00"},
        {"role": "user", "content": "Anything else you want in the soup", "timestamp": "17:02"},
        {"role": "user", "content": "Yogurt & milk please", "timestamp": "17:08"}
    ]
    
    return messages


async def demo_ai_form_chain():
    """Demonstrate AI-powered form chain generation"""
    
    print("🤖 AI-Powered Form Chain Demo")
    print("="*50)
    
    # Create mock LLM provider
    llm = MockLLMProvider()
    
    # Create conversation bridge
    bridge = ConversationFormBridge(llm)
    
    # Process mom's messages
    messages = create_shopping_assistant_demo()
    user_id = "mom"
    
    print("\n📱 Processing WhatsApp conversation:")
    for msg in messages:
        print(f"  [{msg['timestamp']}] {msg['content']}")
        response = await bridge.process_message(
            user_id,
            msg['content'],
            datetime.strptime(f"2024-01-01 {msg['timestamp']}", "%Y-%m-%d %H:%M")
        )
        
        if response["type"] == "form":
            print(f"\n✅ Form generated!")
            print(f"   Chain ID: {response['chain_id']}")
            # Save form for inspection
            with open("shopping_form_demo.html", "w") as f:
                f.write(response["form_html"])
            print("   Saved to: shopping_form_demo.html")
        else:
            print(f"   AI: {response['message']}")
            if response.get("entities_found"):
                print(f"   Found items: {response['entities_found']}")
    
    # Show context
    context = bridge.get_context(user_id)
    print(f"\n📊 Final context:")
    print(f"   Total messages: {len(context.messages)}")
    print(f"   Intent: {context.intent}")
    print(f"   Items extracted: {context.entities.get('items', [])}")


# Export main components
__all__ = [
    'LLMConfig',
    'ConversationIntent',
    'ConversationContext',
    'LLMProvider',
    'MockLLMProvider',
    'AIFormChainGenerator',
    'ConversationFormBridge',
    'create_shopping_assistant_demo',
    'demo_ai_form_chain'
]


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_ai_form_chain())