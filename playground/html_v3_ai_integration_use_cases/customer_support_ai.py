#!/usr/bin/env python3
"""
AI-Powered Customer Support System

Transforms customer support conversations into structured troubleshooting workflows,
automated ticket routing, and resolution tracking.

Features:
- Natural language understanding of technical issues
- Intelligent ticket categorization and priority
- Dynamic troubleshooting workflows
- Knowledge base integration
- Escalation management
- Customer satisfaction tracking
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


class IssueCategory(str, Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    PRODUCT = "product"
    SERVICE = "service"
    FEEDBACK = "feedback"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ProductType(str, Enum):
    SOFTWARE = "software"
    HARDWARE = "hardware"
    SERVICE = "service"
    SUBSCRIPTION = "subscription"


class SupportAIProvider(LLMProvider):
    """Customer support-specific AI provider"""
    
    def __init__(self):
        self.issue_patterns = {
            "login": {
                "keywords": ["can't login", "password", "access denied", "locked out", "sign in"],
                "category": IssueCategory.ACCOUNT,
                "common_solutions": [
                    "Reset password",
                    "Clear browser cache",
                    "Check account status",
                    "Verify email"
                ]
            },
            "performance": {
                "keywords": ["slow", "lag", "freeze", "crash", "not responding"],
                "category": IssueCategory.TECHNICAL,
                "common_solutions": [
                    "Restart application",
                    "Check system requirements",
                    "Update software",
                    "Clear cache"
                ]
            },
            "billing": {
                "keywords": ["charge", "payment", "invoice", "refund", "subscription"],
                "category": IssueCategory.BILLING,
                "common_solutions": [
                    "Review billing history",
                    "Update payment method",
                    "Process refund",
                    "Adjust billing cycle"
                ]
            },
            "error": {
                "keywords": ["error", "bug", "broken", "not working", "failed"],
                "category": IssueCategory.TECHNICAL,
                "common_solutions": [
                    "Check error logs",
                    "Reinstall application",
                    "Update to latest version",
                    "Contact technical support"
                ]
            }
        }
        
        self.urgency_indicators = {
            "critical": ["urgent", "asap", "emergency", "critical", "down", "stopped working completely"],
            "high": ["important", "need help", "frustrated", "affecting work", "business impact"],
            "medium": ["issue", "problem", "help", "question"],
            "low": ["wondering", "curious", "when you get a chance", "minor"]
        }
        
        self.sentiment_indicators = {
            "angry": ["furious", "unacceptable", "terrible", "worst", "angry", "frustrated"],
            "upset": ["disappointed", "unhappy", "not satisfied", "poor service"],
            "neutral": ["issue", "problem", "help", "question"],
            "positive": ["thank you", "appreciate", "helpful", "great"]
        }
        
        self.knowledge_base = {
            "password_reset": {
                "title": "How to Reset Your Password",
                "steps": [
                    "Go to the login page",
                    "Click 'Forgot Password'",
                    "Enter your email address",
                    "Check your email for reset link",
                    "Create a new password"
                ],
                "estimated_time": "5 minutes"
            },
            "clear_cache": {
                "title": "Clear Browser Cache",
                "steps": [
                    "Open browser settings",
                    "Find 'Clear browsing data'",
                    "Select 'Cached images and files'",
                    "Click 'Clear data'",
                    "Restart browser"
                ],
                "estimated_time": "2 minutes"
            }
        }
    
    async def analyze_conversation(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze support conversation for issues and urgency"""
        
        messages_text = " ".join([m["content"].lower() for m in context.messages])
        
        # Extract issue details
        entities = {
            "issues": [],
            "category": IssueCategory.GENERAL,
            "priority": Priority.MEDIUM,
            "sentiment": "neutral",
            "product_mentioned": None,
            "error_codes": [],
            "affected_features": [],
            "customer_attempts": []
        }
        
        # Detect issue types
        detected_issues = []
        for issue_type, data in self.issue_patterns.items():
            if any(keyword in messages_text for keyword in data["keywords"]):
                detected_issues.append({
                    "type": issue_type,
                    "category": data["category"],
                    "solutions": data["common_solutions"]
                })
                entities["category"] = data["category"]
        
        entities["issues"] = detected_issues
        
        # Determine priority
        for priority, indicators in self.urgency_indicators.items():
            if any(indicator in messages_text for indicator in indicators):
                entities["priority"] = Priority(priority)
                break
        
        # Analyze sentiment
        for sentiment, indicators in self.sentiment_indicators.items():
            if any(indicator in messages_text for indicator in indicators):
                entities["sentiment"] = sentiment
                break
        
        # Extract error codes
        import re
        error_pattern = r'(?:error|code)[:;\s]+([A-Z0-9\-]+)'
        errors = re.findall(error_pattern, messages_text.upper())
        entities["error_codes"] = errors
        
        # Detect product mentions
        products = ["software", "app", "website", "mobile", "desktop", "api"]
        for product in products:
            if product in messages_text:
                entities["product_mentioned"] = product
                break
        
        # Identify customer attempts
        attempt_phrases = ["i tried", "i've tried", "already tried", "attempted"]
        for phrase in attempt_phrases:
            if phrase in messages_text:
                entities["customer_attempts"].append("Previous troubleshooting attempted")
        
        # Generate initial diagnosis
        diagnosis = self._generate_diagnosis(entities)
        
        return {
            "intent": ConversationIntent.SUPPORT,
            "entities": entities,
            "diagnosis": diagnosis,
            "recommended_actions": self._get_recommended_actions(entities, diagnosis)
        }
    
    async def generate_form_schema(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate support ticket form"""
        
        analysis = await self.analyze_conversation(context)
        entities = analysis["entities"]
        
        fields = []
        
        # Customer information
        fields.append({
            "name": "customer_info",
            "type": "section",
            "label": "Contact Information",
            "fields": [
                {"name": "full_name", "type": "text", "label": "Your Name", "required": True},
                {"name": "email", "type": "email", "label": "Email Address", "required": True},
                {"name": "account_id", "type": "text", "label": "Account ID (if known)", "required": False}
            ]
        })
        
        # Issue details
        fields.extend([
            {
                "name": "issue_summary",
                "type": "text",
                "label": "Brief description of the issue",
                "default": self._summarize_issue(context.messages),
                "required": True
            },
            {
                "name": "issue_details",
                "type": "textarea",
                "label": "Detailed description",
                "default": " ".join([m["content"] for m in context.messages]),
                "required": True,
                "help_text": "Include any error messages, when it started, and what you were doing"
            }
        ])
        
        # Product/Service affected
        fields.append({
            "name": "affected_product",
            "type": "select",
            "label": "Which product/service is affected?",
            "options": [
                "Web Application",
                "Mobile App",
                "Desktop Software",
                "API/Integration",
                "Other"
            ],
            "default": self._detect_product(entities),
            "required": True
        })
        
        # Error information
        if entities.get("error_codes"):
            fields.append({
                "name": "error_codes",
                "type": "text",
                "label": "Error codes",
                "default": ", ".join(entities["error_codes"]),
                "required": False
            })
        
        # Impact assessment
        fields.append({
            "name": "impact",
            "type": "radio",
            "label": "How is this affecting you?",
            "options": [
                {"value": "blocker", "label": "I cannot work at all"},
                {"value": "major", "label": "Major impact on my work"},
                {"value": "minor", "label": "Minor inconvenience"},
                {"value": "none", "label": "No immediate impact"}
            ],
            "default": self._assess_impact(entities),
            "required": True
        })
        
        # Troubleshooting attempts
        fields.append({
            "name": "attempted_solutions",
            "type": "checkbox_group",
            "label": "What have you already tried?",
            "options": [
                "Restarted application/device",
                "Cleared cache/cookies",
                "Updated software",
                "Checked internet connection",
                "Tried different browser/device",
                "None of the above"
            ],
            "required": False
        })
        
        # Environment details
        fields.append({
            "name": "environment",
            "type": "section",
            "label": "Technical Details",
            "fields": [
                {"name": "operating_system", "type": "select", 
                 "label": "Operating System",
                 "options": ["Windows", "macOS", "Linux", "iOS", "Android", "Other"],
                 "required": False},
                {"name": "browser", "type": "select",
                 "label": "Browser (if applicable)",
                 "options": ["Chrome", "Firefox", "Safari", "Edge", "Other", "N/A"],
                 "required": False}
            ]
        })
        
        # Attachment option
        fields.append({
            "name": "attachments",
            "type": "file",
            "label": "Attach screenshots or logs",
            "accept": "image/*,.log,.txt",
            "multiple": True,
            "required": False,
            "help_text": "Screenshots help us resolve issues faster"
        })
        
        # Preferred contact method
        fields.append({
            "name": "contact_preference",
            "type": "radio",
            "label": "Preferred contact method",
            "options": [
                {"value": "email", "label": "Email"},
                {"value": "phone", "label": "Phone"},
                {"value": "chat", "label": "Live Chat"}
            ],
            "default": "email",
            "required": True
        })
        
        return {
            "title": "Support Ticket - Let's Resolve This Together",
            "description": f"Priority: {entities['priority'].value.upper()} | Category: {entities['category'].value}",
            "fields": fields,
            "diagnosis": analysis["diagnosis"],
            "quick_solutions": self._get_quick_solutions(entities)
        }
    
    async def process_response(self, user_input: str, context: ConversationContext) -> Dict[str, Any]:
        """Process support ticket response"""
        
        context.messages.append({"role": "user", "content": user_input})
        
        # Create support ticket
        ticket = self._create_support_ticket(context)
        
        # Generate troubleshooting workflow
        workflow = self._generate_troubleshooting_workflow(context.entities)
        
        # Check for immediate solutions
        immediate_solution = self._check_knowledge_base(context.entities)
        
        return {
            "updated_context": context,
            "ticket": ticket,
            "workflow": workflow,
            "immediate_solution": immediate_solution,
            "next_steps": self._get_support_next_steps(context.entities)
        }
    
    def _generate_diagnosis(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate initial diagnosis"""
        
        diagnosis = {
            "confidence": 0.0,
            "probable_cause": "Unknown",
            "affected_systems": [],
            "resolution_time": "Unknown"
        }
        
        # Analyze based on issue patterns
        if entities["issues"]:
            main_issue = entities["issues"][0]
            
            if main_issue["type"] == "login":
                diagnosis.update({
                    "confidence": 0.85,
                    "probable_cause": "Authentication issue",
                    "affected_systems": ["Authentication", "User Management"],
                    "resolution_time": "15-30 minutes"
                })
            elif main_issue["type"] == "performance":
                diagnosis.update({
                    "confidence": 0.70,
                    "probable_cause": "System performance degradation",
                    "affected_systems": ["Application Performance", "Infrastructure"],
                    "resolution_time": "1-2 hours"
                })
            elif main_issue["type"] == "billing":
                diagnosis.update({
                    "confidence": 0.90,
                    "probable_cause": "Billing system issue",
                    "affected_systems": ["Billing", "Subscription Management"],
                    "resolution_time": "24-48 hours"
                })
        
        return diagnosis
    
    def _get_recommended_actions(
        self,
        entities: Dict[str, Any],
        diagnosis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Get recommended support actions"""
        
        actions = []
        
        # Priority-based actions
        if entities["priority"] == Priority.CRITICAL:
            actions.append({
                "action": "escalate",
                "description": "Escalate to senior support immediately",
                "urgency": "immediate"
            })
        
        # Category-based actions
        if entities["category"] == IssueCategory.TECHNICAL:
            actions.extend([
                {
                    "action": "collect_logs",
                    "description": "Gather system logs and diagnostics",
                    "urgency": "high"
                },
                {
                    "action": "remote_session",
                    "description": "Offer remote support session",
                    "urgency": "medium"
                }
            ])
        elif entities["category"] == IssueCategory.BILLING:
            actions.append({
                "action": "billing_review",
                "description": "Review account billing history",
                "urgency": "high"
            })
        
        # Sentiment-based actions
        if entities["sentiment"] in ["angry", "upset"]:
            actions.insert(0, {
                "action": "empathy_response",
                "description": "Acknowledge frustration and apologize",
                "urgency": "immediate"
            })
        
        return actions[:3]
    
    def _summarize_issue(self, messages: List[Dict[str, str]]) -> str:
        """Create brief issue summary"""
        
        if not messages:
            return ""
        
        # Take first sentence or first 100 chars
        first_message = messages[0]["content"]
        if "." in first_message:
            return first_message.split(".")[0]
        else:
            return first_message[:100] + "..." if len(first_message) > 100 else first_message
    
    def _detect_product(self, entities: Dict[str, Any]) -> str:
        """Detect which product is affected"""
        
        product = entities.get("product_mentioned", "")
        
        if "mobile" in product or "app" in product:
            return "Mobile App"
        elif "website" in product or "web" in product:
            return "Web Application"
        elif "api" in product:
            return "API/Integration"
        else:
            return "Web Application"  # Default
    
    def _assess_impact(self, entities: Dict[str, Any]) -> str:
        """Assess impact level"""
        
        if entities["priority"] == Priority.CRITICAL:
            return "blocker"
        elif entities["priority"] == Priority.HIGH:
            return "major"
        else:
            return "minor"
    
    def _get_quick_solutions(self, entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get quick solution suggestions"""
        
        solutions = []
        
        if entities["issues"]:
            for issue in entities["issues"][:2]:
                for solution in issue["solutions"][:2]:
                    solutions.append({
                        "title": solution,
                        "time": "2-5 minutes",
                        "success_rate": "60-80%"
                    })
        
        return solutions
    
    def _create_support_ticket(self, context: ConversationContext) -> Dict[str, Any]:
        """Create support ticket from context"""
        
        ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "ticket_id": ticket_id,
            "status": IssueStatus.NEW,
            "priority": context.entities.get("priority", Priority.MEDIUM),
            "category": context.entities.get("category", IssueCategory.GENERAL),
            "created_at": datetime.now().isoformat(),
            "customer_sentiment": context.entities.get("sentiment", "neutral"),
            "sla": self._calculate_sla(context.entities)
        }
    
    def _calculate_sla(self, entities: Dict[str, Any]) -> Dict[str, str]:
        """Calculate SLA based on priority"""
        
        sla_times = {
            Priority.CRITICAL: {"response": "1 hour", "resolution": "4 hours"},
            Priority.HIGH: {"response": "4 hours", "resolution": "24 hours"},
            Priority.MEDIUM: {"response": "24 hours", "resolution": "3 days"},
            Priority.LOW: {"response": "48 hours", "resolution": "7 days"}
        }
        
        return sla_times.get(entities.get("priority", Priority.MEDIUM))
    
    def _generate_troubleshooting_workflow(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate step-by-step troubleshooting workflow"""
        
        workflow = []
        
        if entities.get("category") == IssueCategory.TECHNICAL:
            workflow.extend([
                {
                    "step": 1,
                    "action": "Verify System Status",
                    "description": "Check if issue is widespread",
                    "automated": True,
                    "estimated_time": "1 minute"
                },
                {
                    "step": 2,
                    "action": "Basic Troubleshooting",
                    "description": "Clear cache, restart application",
                    "automated": False,
                    "estimated_time": "5 minutes"
                },
                {
                    "step": 3,
                    "action": "Advanced Diagnostics",
                    "description": "Collect logs, check configurations",
                    "automated": True,
                    "estimated_time": "10 minutes"
                }
            ])
        elif entities.get("category") == IssueCategory.ACCOUNT:
            workflow.extend([
                {
                    "step": 1,
                    "action": "Verify Account Status",
                    "description": "Check if account is active",
                    "automated": True,
                    "estimated_time": "30 seconds"
                },
                {
                    "step": 2,
                    "action": "Reset Credentials",
                    "description": "Send password reset if needed",
                    "automated": True,
                    "estimated_time": "2 minutes"
                }
            ])
        
        return workflow
    
    def _check_knowledge_base(self, entities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if knowledge base has immediate solution"""
        
        if entities.get("issues"):
            issue_type = entities["issues"][0]["type"]
            
            if issue_type == "login" and "password_reset" in self.knowledge_base:
                return self.knowledge_base["password_reset"]
            elif issue_type == "performance" and "clear_cache" in self.knowledge_base:
                return self.knowledge_base["clear_cache"]
        
        return None
    
    def _get_support_next_steps(self, entities: Dict[str, Any]) -> List[str]:
        """Get next support steps"""
        
        steps = []
        
        if entities.get("priority") == Priority.CRITICAL:
            steps.append("Senior support engineer will contact you within 1 hour")
        else:
            steps.append("Support agent will review your ticket")
        
        steps.extend([
            "You'll receive email confirmation with ticket number",
            "Track progress in your support portal",
            "We'll update you within SLA timeframe"
        ])
        
        return steps


class TicketManagementSystem:
    """Manage support tickets and workflows"""
    
    def __init__(self, ai_provider: SupportAIProvider):
        self.ai_provider = ai_provider
        self.tickets = {}
        self.agent_queue = []
    
    async def create_ticket(
        self,
        customer_data: Dict[str, Any],
        issue_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create and route support ticket"""
        
        # Generate ticket
        ticket = {
            "id": f"TICKET-{len(self.tickets) + 1:06d}",
            "customer": customer_data,
            "issue": issue_data,
            "status": IssueStatus.NEW,
            "created_at": datetime.now(),
            "updates": [],
            "assigned_to": None,
            "resolution": None
        }
        
        # Determine routing
        routing = await self._route_ticket(issue_data)
        ticket["routing"] = routing
        
        # Auto-assign if possible
        if routing["auto_assignable"]:
            ticket["assigned_to"] = routing["suggested_agent"]
            ticket["status"] = IssueStatus.IN_PROGRESS
        
        # Store ticket
        self.tickets[ticket["id"]] = ticket
        
        # Generate initial response
        initial_response = await self._generate_initial_response(ticket)
        
        return {
            "ticket": ticket,
            "initial_response": initial_response,
            "estimated_resolution": routing["estimated_time"]
        }
    
    async def _route_ticket(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route ticket to appropriate team/agent"""
        
        category = issue_data.get("category", IssueCategory.GENERAL)
        priority = issue_data.get("priority", Priority.MEDIUM)
        
        routing = {
            "team": "general_support",
            "skill_required": "basic",
            "auto_assignable": False,
            "suggested_agent": None,
            "estimated_time": "24 hours"
        }
        
        # Route based on category and priority
        if category == IssueCategory.TECHNICAL:
            routing["team"] = "technical_support"
            routing["skill_required"] = "technical"
            
            if priority == Priority.CRITICAL:
                routing["team"] = "senior_technical"
                routing["skill_required"] = "advanced"
                routing["estimated_time"] = "4 hours"
        
        elif category == IssueCategory.BILLING:
            routing["team"] = "billing_support"
            routing["skill_required"] = "billing"
            routing["estimated_time"] = "48 hours"
        
        # Check for auto-assignment
        if priority in [Priority.LOW, Priority.MEDIUM]:
            routing["auto_assignable"] = True
            routing["suggested_agent"] = "bot_agent_1"
        
        return routing
    
    async def _generate_initial_response(self, ticket: Dict[str, Any]) -> str:
        """Generate initial customer response"""
        
        priority = ticket["issue"].get("priority", Priority.MEDIUM)
        category = ticket["issue"].get("category", IssueCategory.GENERAL)
        
        response = f"""
Thank you for contacting our support team.

Your ticket #{ticket['id']} has been created and assigned to our {ticket['routing']['team'].replace('_', ' ').title()} team.

Priority: {priority.value.upper()}
Expected Response Time: {ticket['routing']['estimated_time']}

What happens next:
1. A support specialist will review your case
2. You'll receive updates via your preferred contact method
3. You can track progress at support.example.com/tickets/{ticket['id']}
"""
        
        # Add empathy for upset customers
        if ticket["issue"].get("sentiment") in ["angry", "upset"]:
            response = "We sincerely apologize for the inconvenience you're experiencing.\n\n" + response
        
        return response


async def demonstrate_customer_support():
    """Demonstrate the AI-powered customer support system"""
    
    print("🎧 AI-Powered Customer Support Demo")
    print("="*60)
    
    # Example support conversations
    conversations = [
        {
            "customer": "frustrated_user",
            "messages": [
                "I can't login to my account! This is urgent!",
                "I've tried resetting my password 3 times already",
                "I need access NOW for an important meeting",
                "Error code: AUTH_FAILED_403"
            ]
        },
        {
            "customer": "confused_user",
            "messages": [
                "The app is running really slow lately",
                "Sometimes it freezes for like 30 seconds",
                "Using Chrome on Windows 10, started last week"
            ]
        },
        {
            "customer": "billing_inquiry",
            "messages": [
                "I was charged twice this month",
                "My invoice shows $99 but I see two charges on my card",
                "Account ID: ACC-12345, need a refund please"
            ]
        }
    ]
    
    ai_provider = SupportAIProvider()
    ticket_system = TicketManagementSystem(ai_provider)
    
    for conv in conversations:
        print(f"\n🎫 Support Case: {conv['customer']}")
        print("-" * 40)
        
        # Create context
        context = ConversationContext(messages=[
            {"role": "user", "content": msg} for msg in conv["messages"]
        ])
        
        # Analyze support request
        analysis = await ai_provider.analyze_conversation(context)
        
        print("\n📊 Issue Analysis:")
        print(f"   Category: {analysis['entities']['category'].value}")
        print(f"   Priority: {analysis['entities']['priority'].value.upper()}")
        print(f"   Sentiment: {analysis['entities']['sentiment']}")
        if analysis['entities']['error_codes']:
            print(f"   Error codes: {', '.join(analysis['entities']['error_codes'])}")
        
        print("\n🔍 Diagnosis:")
        diagnosis = analysis["diagnosis"]
        print(f"   Probable cause: {diagnosis['probable_cause']}")
        print(f"   Confidence: {diagnosis['confidence']*100:.0f}%")
        print(f"   Est. resolution: {diagnosis['resolution_time']}")
        
        print("\n💡 Recommended Actions:")
        for action in analysis["recommended_actions"][:2]:
            print(f"   [{action['urgency'].upper()}] {action['description']}")
        
        # Generate support form
        schema = await ai_provider.generate_form_schema(context)
        print(f"\n📝 Generated ticket form with {len(schema['fields'])} sections")
        
        # Quick solutions
        if schema.get("quick_solutions"):
            print("\n⚡ Quick Solutions Available:")
            for solution in schema["quick_solutions"][:2]:
                print(f"   - {solution['title']} ({solution['time']})")
        
        # Create ticket
        customer_data = {
            "name": conv["customer"],
            "email": f"{conv['customer']}@example.com"
        }
        
        ticket_result = await ticket_system.create_ticket(
            customer_data,
            analysis["entities"]
        )
        
        print(f"\n🎟️ Ticket Created: {ticket_result['ticket']['id']}")
        print(f"   Routed to: {ticket_result['ticket']['routing']['team']}")
        print(f"   Status: {ticket_result['ticket']['status'].value}")
    
    print("\n" + "="*60)
    print("🌟 Customer Support AI Features:")
    print("- Natural language issue detection")
    print("- Intelligent ticket routing")
    print("- Sentiment analysis and empathy")
    print("- Knowledge base integration")
    print("- SLA management")
    print("- Automated troubleshooting workflows")


if __name__ == "__main__":
    asyncio.run(demonstrate_customer_support())