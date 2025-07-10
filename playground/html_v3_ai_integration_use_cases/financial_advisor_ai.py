#!/usr/bin/env python3
"""
AI-Powered Financial Advisory Assistant

Transforms casual financial conversations into structured investment workflows,
budget plans, and personalized financial advice.

Features:
- Natural language understanding of financial goals
- Risk assessment through conversational analysis
- Dynamic portfolio recommendations
- Budget analysis and optimization
- Retirement planning calculators
- Tax optimization suggestions
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field, create_model
import json

from html_v3_ai import (
    LLMProvider, ConversationContext, ConversationIntent,
    AIFormChainGenerator
)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from html_v3 import FormChainEngine, FormStep, FormStepProcessor, FormFieldSpec, FieldType


class RiskTolerance(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"


class InvestmentGoal(str, Enum):
    RETIREMENT = "retirement"
    HOME_PURCHASE = "home_purchase"
    EDUCATION = "education"
    WEALTH_BUILDING = "wealth_building"
    EMERGENCY_FUND = "emergency_fund"
    DEBT_PAYOFF = "debt_payoff"


class AssetClass(str, Enum):
    STOCKS = "stocks"
    BONDS = "bonds"
    REAL_ESTATE = "real_estate"
    COMMODITIES = "commodities"
    CRYPTO = "cryptocurrency"
    CASH = "cash_equivalents"


class FinancialAIProvider(LLMProvider):
    """Financial-specific AI provider for investment advice"""
    
    def __init__(self):
        self.financial_indicators = {
            "conservative_keywords": ["safe", "secure", "stable", "low risk", "preserve"],
            "aggressive_keywords": ["growth", "high return", "maximize", "opportunity"],
            "retirement_keywords": ["retire", "retirement", "401k", "pension", "golden years"],
            "debt_keywords": ["debt", "loan", "credit card", "mortgage", "owe"],
            "savings_keywords": ["save", "savings", "emergency", "rainy day"],
            "investment_keywords": ["invest", "stocks", "bonds", "portfolio", "returns"]
        }
        
        self.portfolio_templates = {
            RiskTolerance.CONSERVATIVE: {
                AssetClass.BONDS: 0.60,
                AssetClass.STOCKS: 0.25,
                AssetClass.CASH: 0.15
            },
            RiskTolerance.MODERATE: {
                AssetClass.STOCKS: 0.50,
                AssetClass.BONDS: 0.35,
                AssetClass.REAL_ESTATE: 0.10,
                AssetClass.CASH: 0.05
            },
            RiskTolerance.AGGRESSIVE: {
                AssetClass.STOCKS: 0.70,
                AssetClass.BONDS: 0.15,
                AssetClass.REAL_ESTATE: 0.10,
                AssetClass.CRYPTO: 0.05
            }
        }
        
        self.financial_rules = {
            "emergency_fund_months": 6,
            "retirement_income_replacement": 0.80,
            "max_debt_to_income": 0.36,
            "housing_cost_ratio": 0.28
        }
    
    async def analyze_conversation(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze financial conversation for goals and risk profile"""
        
        messages_text = " ".join([m["content"].lower() for m in context.messages])
        
        # Extract financial entities
        entities = {
            "goals": [],
            "risk_tolerance": RiskTolerance.MODERATE,
            "time_horizon": None,
            "current_assets": {},
            "monthly_income": None,
            "monthly_expenses": None,
            "debt_info": {},
            "age": None
        }
        
        # Detect investment goals
        if any(word in messages_text for word in self.financial_indicators["retirement_keywords"]):
            entities["goals"].append(InvestmentGoal.RETIREMENT)
        if any(word in messages_text for word in ["house", "home", "property"]):
            entities["goals"].append(InvestmentGoal.HOME_PURCHASE)
        if any(word in messages_text for word in self.financial_indicators["debt_keywords"]):
            entities["goals"].append(InvestmentGoal.DEBT_PAYOFF)
        if any(word in messages_text for word in self.financial_indicators["savings_keywords"]):
            entities["goals"].append(InvestmentGoal.EMERGENCY_FUND)
        
        # Assess risk tolerance
        conservative_count = sum(1 for word in self.financial_indicators["conservative_keywords"] if word in messages_text)
        aggressive_count = sum(1 for word in self.financial_indicators["aggressive_keywords"] if word in messages_text)
        
        if conservative_count > aggressive_count:
            entities["risk_tolerance"] = RiskTolerance.CONSERVATIVE
        elif aggressive_count > conservative_count:
            entities["risk_tolerance"] = RiskTolerance.AGGRESSIVE
        
        # Extract time horizon
        import re
        year_match = re.search(r'(\d+)\s*years?', messages_text)
        if year_match:
            entities["time_horizon"] = int(year_match.group(1))
        
        # Extract monetary amounts
        money_pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+)k?\b'
        amounts = re.findall(money_pattern, messages_text)
        if amounts:
            # Simple heuristic: largest amount might be income or savings
            entities["available_capital"] = max([self._parse_amount(amt) for amt in amounts])
        
        # Extract age
        age_match = re.search(r'(\d{2})\s*(?:years?\s*old|yo)', messages_text)
        if age_match:
            entities["age"] = int(age_match.group(1))
        
        # Financial health assessment
        financial_health = self._assess_financial_health(entities)
        
        return {
            "intent": ConversationIntent.FINANCIAL,
            "entities": entities,
            "financial_health": financial_health,
            "recommendations": self._generate_initial_recommendations(entities, financial_health)
        }
    
    async def generate_form_schema(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate financial assessment form"""
        
        analysis = await self.analyze_conversation(context)
        entities = analysis["entities"]
        
        fields = []
        
        # Personal information
        fields.append({
            "name": "personal_info",
            "type": "section",
            "label": "Personal Information",
            "fields": [
                {"name": "age", "type": "number", "label": "Your age", 
                 "default": entities.get("age"), "min": 18, "max": 100, "required": True},
                {"name": "employment_status", "type": "select", "label": "Employment status",
                 "options": ["Employed", "Self-employed", "Retired", "Student", "Unemployed"],
                 "required": True}
            ]
        })
        
        # Financial situation
        fields.extend([
            {
                "name": "annual_income",
                "type": "number",
                "label": "Annual income (before taxes)",
                "min": 0,
                "step": 1000,
                "required": True,
                "help_text": "Include all sources of income"
            },
            {
                "name": "monthly_expenses",
                "type": "number",
                "label": "Average monthly expenses",
                "min": 0,
                "step": 100,
                "required": True,
                "help_text": "Include rent, utilities, food, etc."
            },
            {
                "name": "current_savings",
                "type": "number",
                "label": "Current savings and investments",
                "min": 0,
                "step": 100,
                "default": entities.get("available_capital", 0),
                "required": True
            }
        ])
        
        # Goals
        if entities["goals"]:
            fields.append({
                "name": "primary_goal",
                "type": "select",
                "label": "Primary financial goal",
                "options": [g.value for g in entities["goals"]],
                "default": entities["goals"][0].value,
                "required": True
            })
        else:
            fields.append({
                "name": "financial_goals",
                "type": "checkbox_group",
                "label": "What are your financial goals?",
                "options": [
                    {"value": "retirement", "label": "Save for retirement"},
                    {"value": "home_purchase", "label": "Buy a home"},
                    {"value": "education", "label": "Education funding"},
                    {"value": "emergency_fund", "label": "Build emergency fund"},
                    {"value": "debt_payoff", "label": "Pay off debt"},
                    {"value": "wealth_building", "label": "Build wealth"}
                ],
                "required": True
            })
        
        # Risk assessment
        fields.append({
            "name": "risk_comfort",
            "type": "range",
            "label": "How comfortable are you with investment risk?",
            "min": 1,
            "max": 10,
            "default": 5,
            "help_text": "1 = Very conservative, 10 = Very aggressive"
        })
        
        # Time horizon
        if not entities.get("time_horizon"):
            fields.append({
                "name": "investment_timeline",
                "type": "select",
                "label": "When will you need this money?",
                "options": [
                    "Less than 1 year",
                    "1-3 years",
                    "3-5 years",
                    "5-10 years",
                    "More than 10 years"
                ],
                "required": True
            })
        
        # Debt information
        fields.append({
            "name": "has_debt",
            "type": "boolean",
            "label": "Do you have any debt?",
            "default": InvestmentGoal.DEBT_PAYOFF in entities["goals"]
        })
        
        return {
            "title": "Let's Create Your Financial Plan",
            "description": "Based on our conversation, I'll help you build a personalized financial strategy",
            "fields": fields,
            "recommendations": analysis["recommendations"]
        }
    
    async def process_response(self, user_input: str, context: ConversationContext) -> Dict[str, Any]:
        """Process financial form responses"""
        
        context.messages.append({"role": "user", "content": user_input})
        
        # Re-analyze with new information
        new_analysis = await self.analyze_conversation(context)
        
        # Generate personalized advice
        advice = self._generate_personalized_advice(new_analysis["entities"])
        
        return {
            "updated_context": context,
            "financial_advice": advice,
            "next_steps": self._get_next_steps(new_analysis["entities"])
        }
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse monetary amounts from strings"""
        
        # Remove currency symbols and commas
        cleaned = amount_str.replace('$', '').replace(',', '')
        
        # Handle 'k' suffix
        if cleaned.endswith('k'):
            return float(cleaned[:-1]) * 1000
        
        return float(cleaned)
    
    def _assess_financial_health(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall financial health"""
        
        health_score = 50  # Base score
        issues = []
        strengths = []
        
        # Check emergency fund
        if entities.get("current_assets", {}).get("savings", 0) > 0:
            strengths.append("Has some savings")
            health_score += 10
        else:
            issues.append("No emergency fund")
            health_score -= 10
        
        # Check debt levels
        if InvestmentGoal.DEBT_PAYOFF in entities.get("goals", []):
            issues.append("Has debt to manage")
            health_score -= 5
        
        # Age-based assessment
        age = entities.get("age", 30)
        if age < 30 and entities.get("goals"):
            strengths.append("Starting financial planning early")
            health_score += 15
        
        return {
            "score": max(0, min(100, health_score)),
            "issues": issues,
            "strengths": strengths,
            "category": "Good" if health_score >= 70 else "Fair" if health_score >= 50 else "Needs Improvement"
        }
    
    def _generate_initial_recommendations(
        self,
        entities: Dict[str, Any],
        health: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate initial financial recommendations"""
        
        recommendations = []
        
        # Emergency fund recommendation
        if "No emergency fund" in health.get("issues", []):
            recommendations.append({
                "priority": "high",
                "action": "Build Emergency Fund",
                "description": "Start by saving $1,000, then build to 3-6 months of expenses",
                "timeline": "Immediate"
            })
        
        # Retirement planning
        age = entities.get("age", 30)
        if age < 60 and InvestmentGoal.RETIREMENT not in entities.get("goals", []):
            recommendations.append({
                "priority": "high",
                "action": "Start Retirement Savings",
                "description": f"At {age}, you have {65-age} years to build retirement wealth",
                "timeline": "This year"
            })
        
        # Debt management
        if InvestmentGoal.DEBT_PAYOFF in entities.get("goals", []):
            recommendations.append({
                "priority": "high",
                "action": "Create Debt Payoff Plan",
                "description": "Focus on high-interest debt first (avalanche method)",
                "timeline": "This month"
            })
        
        # Investment recommendations based on risk
        risk = entities.get("risk_tolerance", RiskTolerance.MODERATE)
        portfolio = self.portfolio_templates.get(risk, {})
        
        recommendations.append({
            "priority": "medium",
            "action": "Diversify Investments",
            "description": f"Consider a {risk.value} portfolio allocation",
            "timeline": "Next 3 months"
        })
        
        return recommendations[:4]  # Top 4 recommendations
    
    def _generate_personalized_advice(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed personalized financial advice"""
        
        age = entities.get("age", 30)
        income = entities.get("monthly_income", 5000)
        expenses = entities.get("monthly_expenses", 3000)
        savings_rate = (income - expenses) / income if income > 0 else 0
        
        advice = {
            "savings_rate": {
                "current": f"{savings_rate * 100:.1f}%",
                "recommended": "20%",
                "action": "Increase savings" if savings_rate < 0.20 else "Excellent savings rate!"
            },
            "portfolio_allocation": self._get_portfolio_recommendation(entities),
            "next_milestones": self._calculate_milestones(entities),
            "tax_tips": self._get_tax_optimization_tips(entities)
        }
        
        return advice
    
    def _get_portfolio_recommendation(self, entities: Dict[str, Any]) -> Dict[str, float]:
        """Get recommended portfolio allocation"""
        
        risk = entities.get("risk_tolerance", RiskTolerance.MODERATE)
        age = entities.get("age", 30)
        
        # Age-based adjustment
        base_portfolio = self.portfolio_templates[risk].copy()
        
        # Reduce stock allocation as age increases (rule of thumb: 100 - age)
        if age > 30:
            stock_percentage = max(0.30, min(0.80, (100 - age) / 100))
            current_stocks = base_portfolio.get(AssetClass.STOCKS, 0)
            
            if current_stocks > stock_percentage:
                # Move excess to bonds
                excess = current_stocks - stock_percentage
                base_portfolio[AssetClass.STOCKS] = stock_percentage
                base_portfolio[AssetClass.BONDS] = base_portfolio.get(AssetClass.BONDS, 0) + excess
        
        return base_portfolio
    
    def _calculate_milestones(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate financial milestones"""
        
        milestones = []
        current_savings = entities.get("current_savings", 0)
        monthly_savings = entities.get("monthly_income", 5000) - entities.get("monthly_expenses", 3000)
        
        # Emergency fund milestone
        emergency_target = entities.get("monthly_expenses", 3000) * 6
        if current_savings < emergency_target:
            months_to_emergency = (emergency_target - current_savings) / monthly_savings if monthly_savings > 0 else 999
            milestones.append({
                "goal": "6-Month Emergency Fund",
                "target": f"${emergency_target:,.0f}",
                "timeline": f"{months_to_emergency:.0f} months" if months_to_emergency < 999 else "Adjust budget"
            })
        
        # First $100k milestone
        if current_savings < 100000:
            months_to_100k = (100000 - current_savings) / monthly_savings if monthly_savings > 0 else 999
            milestones.append({
                "goal": "First $100,000",
                "target": "$100,000",
                "timeline": f"{months_to_100k/12:.1f} years" if months_to_100k < 999 else "Increase savings"
            })
        
        return milestones
    
    def _get_tax_optimization_tips(self, entities: Dict[str, Any]) -> List[str]:
        """Get tax optimization tips"""
        
        tips = []
        
        # 401k/IRA recommendations
        age = entities.get("age", 30)
        if age < 60:
            tips.append("Maximize 401(k) contributions for tax deduction ($22,500 limit for 2024)")
            tips.append("Consider Roth IRA for tax-free retirement growth ($6,500 limit)")
        
        # HSA recommendation
        tips.append("Use Health Savings Account (HSA) for triple tax advantage")
        
        # Investment tips
        if entities.get("current_savings", 0) > 50000:
            tips.append("Consider tax-loss harvesting in taxable accounts")
            tips.append("Hold tax-efficient index funds in taxable accounts")
        
        return tips[:3]
    
    def _get_next_steps(self, entities: Dict[str, Any]) -> List[str]:
        """Get actionable next steps"""
        
        steps = []
        
        # Priority-based steps
        if not entities.get("emergency_fund"):
            steps.append("Open high-yield savings account for emergency fund")
        
        if InvestmentGoal.RETIREMENT in entities.get("goals", []):
            steps.append("Set up automatic 401(k) contributions")
            steps.append("Open and fund an IRA account")
        
        if entities.get("has_debt"):
            steps.append("List all debts with interest rates")
            steps.append("Set up automatic extra payments on highest-rate debt")
        
        steps.append("Schedule monthly financial review")
        
        return steps[:4]


class FinancialPlanGenerator:
    """Generate comprehensive financial plans"""
    
    def __init__(self, ai_provider: FinancialAIProvider):
        self.ai_provider = ai_provider
    
    async def create_financial_plan(
        self,
        user_data: Dict[str, Any],
        goals: List[InvestmentGoal]
    ) -> Dict[str, Any]:
        """Create detailed financial plan"""
        
        plan = {
            "summary": self._create_executive_summary(user_data, goals),
            "current_situation": self._analyze_current_situation(user_data),
            "recommendations": await self._generate_recommendations(user_data, goals),
            "action_plan": self._create_action_plan(user_data, goals),
            "projections": self._calculate_projections(user_data)
        }
        
        return plan
    
    def _create_executive_summary(
        self,
        user_data: Dict[str, Any],
        goals: List[InvestmentGoal]
    ) -> Dict[str, Any]:
        """Create plan summary"""
        
        age = user_data.get("age", 30)
        years_to_retirement = max(0, 65 - age)
        
        return {
            "client_age": age,
            "time_horizon": f"{years_to_retirement} years to retirement",
            "primary_goals": [g.value for g in goals],
            "risk_profile": user_data.get("risk_tolerance", RiskTolerance.MODERATE).value,
            "plan_date": datetime.now().date().isoformat()
        }
    
    def _analyze_current_situation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current financial situation"""
        
        income = user_data.get("annual_income", 60000)
        expenses = user_data.get("monthly_expenses", 3000) * 12
        savings = user_data.get("current_savings", 10000)
        
        return {
            "annual_income": income,
            "annual_expenses": expenses,
            "savings_rate": (income - expenses) / income if income > 0 else 0,
            "net_worth": savings,  # Simplified
            "debt_to_income": 0,  # Would calculate from debt info
            "emergency_fund_months": savings / (expenses / 12) if expenses > 0 else 0
        }
    
    async def _generate_recommendations(
        self,
        user_data: Dict[str, Any],
        goals: List[InvestmentGoal]
    ) -> List[Dict[str, Any]]:
        """Generate specific recommendations"""
        
        recommendations = []
        
        # Emergency fund
        current_emergency = user_data.get("current_savings", 0)
        target_emergency = user_data.get("monthly_expenses", 3000) * 6
        
        if current_emergency < target_emergency:
            recommendations.append({
                "category": "Emergency Fund",
                "action": "Build emergency savings",
                "current": f"${current_emergency:,.0f}",
                "target": f"${target_emergency:,.0f}",
                "monthly_contribution": f"${(target_emergency - current_emergency) / 24:,.0f}",
                "timeline": "24 months"
            })
        
        # Retirement savings
        if InvestmentGoal.RETIREMENT in goals:
            annual_income = user_data.get("annual_income", 60000)
            retirement_target = annual_income * 0.15  # 15% savings rate
            
            recommendations.append({
                "category": "Retirement",
                "action": "Maximize retirement contributions",
                "current": "$0",  # Would get from data
                "target": f"${retirement_target:,.0f}/year",
                "accounts": ["401(k)", "Roth IRA"],
                "tax_benefit": f"${retirement_target * 0.25:,.0f} estimated tax savings"
            })
        
        # Investment allocation
        portfolio = self.ai_provider._get_portfolio_recommendation(user_data)
        recommendations.append({
            "category": "Portfolio Allocation",
            "action": "Rebalance portfolio",
            "allocation": {k.value: f"{v*100:.0f}%" for k, v in portfolio.items()},
            "risk_level": user_data.get("risk_tolerance", RiskTolerance.MODERATE).value
        })
        
        return recommendations
    
    def _create_action_plan(
        self,
        user_data: Dict[str, Any],
        goals: List[InvestmentGoal]
    ) -> List[Dict[str, Any]]:
        """Create step-by-step action plan"""
        
        actions = []
        
        # Month 1
        actions.append({
            "month": 1,
            "tasks": [
                "Open high-yield savings account",
                "Set up automatic emergency fund transfer",
                "Review and optimize monthly budget"
            ]
        })
        
        # Month 2
        actions.append({
            "month": 2,
            "tasks": [
                "Increase 401(k) contribution to employer match",
                "Open investment account",
                "Schedule quarterly financial reviews"
            ]
        })
        
        # Month 3
        actions.append({
            "month": 3,
            "tasks": [
                "Implement portfolio allocation",
                "Set up automatic rebalancing",
                "Review insurance coverage"
            ]
        })
        
        return actions
    
    def _calculate_projections(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial projections"""
        
        current_age = user_data.get("age", 30)
        retirement_age = 65
        current_savings = user_data.get("current_savings", 10000)
        monthly_contribution = 500  # Simplified
        annual_return = 0.07  # 7% average return
        
        # Simple compound interest calculation
        years = retirement_age - current_age
        months = years * 12
        
        future_value = current_savings * (1 + annual_return) ** years
        
        # Add monthly contributions
        monthly_rate = annual_return / 12
        contribution_value = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        
        total_retirement = future_value + contribution_value
        
        return {
            "retirement_projection": {
                "age_65_value": f"${total_retirement:,.0f}",
                "monthly_retirement_income": f"${total_retirement * 0.04 / 12:,.0f}",
                "years_of_income": "25+ years at 4% withdrawal rate"
            },
            "milestone_projections": [
                {"age": 40, "projected_value": f"${total_retirement * 0.3:,.0f}"},
                {"age": 50, "projected_value": f"${total_retirement * 0.6:,.0f}"},
                {"age": 60, "projected_value": f"${total_retirement * 0.85:,.0f}"}
            ]
        }


async def demonstrate_financial_advisor():
    """Demonstrate the AI-powered financial advisor"""
    
    print("💰 AI-Powered Financial Advisor Demo")
    print("="*60)
    
    # Example conversations
    conversations = [
        {
            "user": "young_professional",
            "messages": [
                "I'm 28 and just got promoted, making $85k now",
                "Want to start investing but scared of losing money",
                "Have about $15k saved but no idea what to do with it"
            ]
        },
        {
            "user": "pre_retiree",
            "messages": [
                "I'm 55 and thinking about retirement in 10 years",
                "Have $250k in 401k but worried it's not enough",
                "Should I be more conservative with investments now?"
            ]
        },
        {
            "user": "debt_focused",
            "messages": [
                "Help! I have $30k in student loans and $5k credit card debt",
                "Making $60k but feel like I'm drowning",
                "Want to buy a house someday but seems impossible"
            ]
        }
    ]
    
    ai_provider = FinancialAIProvider()
    
    for conv in conversations:
        print(f"\n💼 Financial Planning for: {conv['user']}")
        print("-" * 40)
        
        # Create context
        context = ConversationContext(messages=[
            {"role": "user", "content": msg} for msg in conv["messages"]
        ])
        
        # Analyze conversation
        analysis = await ai_provider.analyze_conversation(context)
        
        print("\n📊 Financial Analysis:")
        print(f"   Goals identified: {', '.join([g.value for g in analysis['entities']['goals']])}")
        print(f"   Risk profile: {analysis['entities']['risk_tolerance'].value}")
        print(f"   Financial health: {analysis['financial_health']['category']}")
        
        print("\n💡 Initial Recommendations:")
        for rec in analysis["recommendations"][:3]:
            print(f"   [{rec['priority'].upper()}] {rec['action']}")
            print(f"   → {rec['description']}")
        
        # Generate form schema
        schema = await ai_provider.generate_form_schema(context)
        
        print(f"\n📝 Generated assessment with {len(schema['fields'])} sections")
        
        # Simulate form completion
        if analysis['entities']['goals']:
            print("\n🎯 Creating Financial Plan...")
            
            plan_generator = FinancialPlanGenerator(ai_provider)
            
            # Mock user data
            user_data = {
                "age": analysis['entities'].get('age', 30),
                "annual_income": 60000,
                "monthly_expenses": 3000,
                "current_savings": 10000,
                "risk_tolerance": analysis['entities']['risk_tolerance']
            }
            
            plan = await plan_generator.create_financial_plan(
                user_data,
                analysis['entities']['goals']
            )
            
            print("\n📈 Financial Projections:")
            projections = plan['projections']['retirement_projection']
            print(f"   Retirement value: {projections['age_65_value']}")
            print(f"   Monthly income: {projections['monthly_retirement_income']}")
    
    print("\n" + "="*60)
    print("🌟 Financial Advisor Features:")
    print("- Natural language goal extraction")
    print("- Risk tolerance assessment")
    print("- Personalized portfolio recommendations")
    print("- Tax optimization strategies")
    print("- Retirement projections")
    print("- Debt management plans")


if __name__ == "__main__":
    asyncio.run(demonstrate_financial_advisor())