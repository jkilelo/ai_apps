"""Advanced Cost Optimization System for Multi-Model LLM Usage

This module implements sophisticated cost optimization strategies:
- Dynamic cost modeling with real-time updates
- Token usage optimization and prediction
- Budget management and quotas
- Cost-aware prompt engineering
- Provider cost comparison and switching
"""

from typing import Dict, Any, List, Optional, Tuple, NamedTuple
from pydantic import BaseModel, Field
from loguru import logger
from enum import Enum
import time
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from collections import defaultdict, deque


class OptimizationStrategy(str, Enum):
    """Cost optimization strategies"""
    AGGRESSIVE = "aggressive"  # Minimize cost at all costs
    BALANCED = "balanced"      # Balance cost with quality/speed
    CONSERVATIVE = "conservative"  # Prioritize quality, optimize cost secondarily
    DYNAMIC = "dynamic"        # Adapt based on usage patterns


class BudgetPeriod(str, Enum):
    """Budget tracking periods"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class CostPrediction:
    """Cost prediction for a request"""
    provider_name: str
    estimated_cost: float
    confidence: float  # 0.0 to 1.0
    input_tokens: int
    output_tokens_estimated: int
    factors_considered: List[str]
    optimization_suggestions: List[str]


@dataclass
class BudgetStatus:
    """Current budget status"""
    period: BudgetPeriod
    allocated_budget: float
    spent_amount: float
    remaining_budget: float
    utilization_percentage: float
    projected_end_of_period_spend: float
    is_over_budget: bool
    days_remaining_in_period: int
    recommended_daily_spend: float


class TokenOptimizer:
    """Intelligent token usage optimization"""
    
    def __init__(self):
        self.compression_patterns = {
            # Common patterns that can be compressed
            'json_formatting': {
                'pattern': r'\{\s*"([^"]+)"\s*:\s*"([^"]+)"\s*\}',
                'replacement': '{"$1":"$2"}',
                'savings_ratio': 0.15
            },
            'whitespace_optimization': {
                'pattern': r'\s{2,}',
                'replacement': ' ',
                'savings_ratio': 0.10
            },
            'redundant_phrases': {
                'patterns': [
                    'please help me',
                    'can you please',
                    'I would like you to',
                    'if you could'
                ],
                'savings_ratio': 0.08
            }
        }
        
        self.prompt_templates = {
            'concise': {
                'prefix': 'Answer concisely:',
                'suffix': '(Keep response under 100 words)',
                'expected_reduction': 0.60
            },
            'structured': {
                'prefix': 'Respond in structured format:',
                'suffix': '(Use bullet points or lists)',
                'expected_reduction': 0.20
            },
            'direct': {
                'prefix': 'Direct answer only:',
                'suffix': '(No explanations unless essential)',
                'expected_reduction': 0.40
            }
        }
    
    def optimize_prompt_for_cost(self, prompt: str, target_reduction: float = 0.20) -> Tuple[str, float]:
        """Optimize prompt to reduce token usage while preserving meaning"""
        original_length = len(prompt)
        optimized = prompt
        total_savings = 0.0
        
        # Apply compression patterns
        for pattern_name, pattern_info in self.compression_patterns.items():
            if 'pattern' in pattern_info:
                import re
                matches = len(re.findall(pattern_info['pattern'], optimized))
                if matches > 0:
                    optimized = re.sub(
                        pattern_info['pattern'],
                        pattern_info['replacement'],
                        optimized
                    )
                    total_savings += pattern_info['savings_ratio'] * (matches / 10)  # Scaled impact
            elif 'patterns' in pattern_info:
                for phrase in pattern_info['patterns']:
                    if phrase.lower() in optimized.lower():
                        optimized = optimized.replace(phrase, '')
                        total_savings += pattern_info['savings_ratio'] * 0.1
        
        # Apply template optimization if needed
        if total_savings < target_reduction:
            remaining_reduction = target_reduction - total_savings
            
            if remaining_reduction > 0.30:
                template = self.prompt_templates['concise']
            elif remaining_reduction > 0.15:
                template = self.prompt_templates['direct']
            else:
                template = self.prompt_templates['structured']
            
            optimized = f"{template['prefix']} {optimized} {template['suffix']}"
            total_savings += template['expected_reduction'] * 0.5  # Conservative estimate
        
        actual_reduction = 1.0 - (len(optimized) / original_length)
        
        return optimized, max(actual_reduction, total_savings)
    
    def estimate_output_tokens(
        self,
        prompt: str,
        task_type: str,
        historical_data: Optional[List[Tuple[int, int]]] = None
    ) -> int:
        """Estimate output tokens based on prompt and task type"""
        # Base estimation
        input_length = len(prompt)
        
        # Task-specific multipliers
        task_multipliers = {
            'reasoning': 1.5,
            'creative': 2.0,
            'coding': 1.2,
            'analytical': 1.8,
            'conversational': 0.8,
            'structured': 0.6,
            'factual': 0.4
        }
        
        base_estimate = input_length * 0.3  # 30% of input length
        multiplier = task_multipliers.get(task_type, 1.0)
        
        # Apply historical data if available
        if historical_data and len(historical_data) >= 3:
            # Use median ratio from historical data
            ratios = [output / max(input_len, 1) for input_len, output in historical_data]
            historical_ratio = statistics.median(ratios)
            estimate_with_history = input_length * historical_ratio
            
            # Weight between base estimate and historical
            final_estimate = (base_estimate * multiplier * 0.3) + (estimate_with_history * 0.7)
        else:
            final_estimate = base_estimate * multiplier
        
        # Apply bounds
        return max(50, min(int(final_estimate), 4000))  # Min 50, max 4000 tokens


class CostOptimizer:
    """Advanced cost optimization system for multi-model LLM usage"""
    
    def __init__(self, cost_models: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        self.cost_models = cost_models
        self.config = config or {}
        self.token_optimizer = TokenOptimizer()
        
        # Budget tracking
        self.budgets: Dict[BudgetPeriod, float] = {
            BudgetPeriod.DAILY: self.config.get('daily_budget', 10.0),
            BudgetPeriod.WEEKLY: self.config.get('weekly_budget', 50.0),
            BudgetPeriod.MONTHLY: self.config.get('monthly_budget', 200.0)
        }
        
        # Spending tracking
        self.spending_history: Dict[str, List[Tuple[datetime, float, str]]] = defaultdict(list)
        self.daily_spending: Dict[str, float] = defaultdict(float)  # Date -> Amount
        
        # Historical data for optimization
        self.token_usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.cost_efficiency_scores: Dict[str, float] = defaultdict(lambda: 0.5)
        
        # Optimization strategies
        self.strategy = OptimizationStrategy(self.config.get('optimization_strategy', 'balanced'))
        
        # Rate limiting for cost control
        self.hourly_spend_limits: Dict[str, float] = {
            provider: self.config.get(f'{provider}_hourly_limit', 5.0)
            for provider in self.cost_models.keys()
        }
    
    def predict_request_cost(
        self,
        prompt: str,
        provider_name: str,
        task_type: str = 'conversational',
        images: Optional[List] = None,
        historical_context: Optional[List] = None
    ) -> CostPrediction:
        """Predict cost for a specific request"""
        if provider_name not in self.cost_models:
            return CostPrediction(
                provider_name=provider_name,
                estimated_cost=0.0,
                confidence=0.0,
                input_tokens=0,
                output_tokens_estimated=0,
                factors_considered=['unknown_provider'],
                optimization_suggestions=['Provider not in cost models']
            )
        
        cost_model = self.cost_models[provider_name]
        
        # Estimate input tokens (this would use actual tokenizer in production)
        input_tokens = len(prompt) // 4  # Rough approximation
        
        # Get historical data for this provider and task type
        historical_key = f"{provider_name}_{task_type}"
        historical_data = list(self.token_usage_history.get(historical_key, []))
        
        # Estimate output tokens
        output_tokens = self.token_optimizer.estimate_output_tokens(
            prompt, task_type, historical_data
        )
        
        # Calculate base cost
        image_count = len(images) if images else 0
        estimated_cost = cost_model.calculate_cost(input_tokens, output_tokens, image_count)
        
        # Calculate confidence based on historical data availability
        confidence = 0.6  # Base confidence
        if len(historical_data) >= 10:
            confidence += 0.2
        if len(historical_data) >= 30:
            confidence += 0.1
        if image_count == 0:  # More confident without images
            confidence += 0.1
        
        factors_considered = [
            f"input_tokens_{input_tokens}",
            f"estimated_output_tokens_{output_tokens}",
            f"task_type_{task_type}",
            f"historical_samples_{len(historical_data)}"
        ]
        
        if image_count > 0:
            factors_considered.append(f"image_count_{image_count}")
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(
            prompt, estimated_cost, input_tokens, output_tokens, provider_name
        )
        
        return CostPrediction(
            provider_name=provider_name,
            estimated_cost=estimated_cost,
            confidence=min(confidence, 1.0),
            input_tokens=input_tokens,
            output_tokens_estimated=output_tokens,
            factors_considered=factors_considered,
            optimization_suggestions=optimization_suggestions
        )
    
    def _generate_optimization_suggestions(
        self,
        prompt: str,
        cost: float,
        input_tokens: int,
        output_tokens: int,
        provider_name: str
    ) -> List[str]:
        """Generate cost optimization suggestions"""
        suggestions = []
        
        # High cost warning
        if cost > 0.50:
            suggestions.append(f"High cost request (${cost:.3f}). Consider breaking into smaller requests.")
        
        # Token optimization suggestions
        if input_tokens > 2000:
            suggestions.append("Long prompt detected. Consider summarizing or splitting the request.")
        
        if output_tokens > 2000:
            suggestions.append("Large output expected. Consider asking for more concise responses.")
        
        # Provider-specific suggestions
        cheapest_provider = min(self.cost_models.keys(), 
                               key=lambda p: self.cost_models[p].cost_per_input_token)
        if provider_name != cheapest_provider:
            cheapest_cost = self.cost_models[cheapest_provider].calculate_cost(
                input_tokens, output_tokens, 0
            )
            if cost > cheapest_cost * 1.5:  # 50% more expensive
                suggestions.append(
                    f"Consider {cheapest_provider} provider for ${cheapest_cost:.3f} "
                    f"(${cost - cheapest_cost:.3f} savings)"
                )
        
        # Budget-based suggestions
        current_budget_status = self.get_budget_status(BudgetPeriod.DAILY)
        if current_budget_status.remaining_budget < cost * 10:  # Less than 10x this request remaining
            suggestions.append(
                f"Daily budget constraint: ${current_budget_status.remaining_budget:.2f} remaining"
            )
        
        # Prompt optimization suggestion
        if len(prompt) > 500:
            optimized_prompt, savings = self.token_optimizer.optimize_prompt_for_cost(prompt)
            if savings > 0.1:  # >10% savings
                suggestions.append(
                    f"Prompt optimization could save ~{savings:.1%} tokens "
                    f"(~${cost * savings:.3f})"
                )
        
        return suggestions
    
    def select_cost_optimal_provider(
        self,
        predictions: List[CostPrediction],
        quality_requirements: Optional[Dict[str, float]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Select the most cost-optimal provider given constraints"""
        if not predictions:
            return None
        
        # Filter by constraints
        viable_predictions = []
        for pred in predictions:
            if constraints:
                max_cost = constraints.get('max_cost')
                if max_cost and pred.estimated_cost > max_cost:
                    continue
                
                min_confidence = constraints.get('min_confidence', 0.0)
                if pred.confidence < min_confidence:
                    continue
                
                excluded_providers = constraints.get('excluded_providers', [])
                if pred.provider_name in excluded_providers:
                    continue
            
            # Check budget constraints
            if not self._can_afford_request(pred.estimated_cost):
                continue
                
            viable_predictions.append(pred)
        
        if not viable_predictions:
            logger.warning("No viable providers meet cost constraints")
            return None
        
        # Apply optimization strategy
        if self.strategy == OptimizationStrategy.AGGRESSIVE:
            # Pure cost minimization
            return min(viable_predictions, key=lambda p: p.estimated_cost).provider_name
        
        elif self.strategy == OptimizationStrategy.BALANCED:
            # Balance cost with historical efficiency
            scores = {}
            for pred in viable_predictions:
                efficiency = self.cost_efficiency_scores[pred.provider_name]
                cost_score = 1.0 / (pred.estimated_cost + 0.001)  # Avoid division by zero
                confidence_score = pred.confidence
                
                # Weighted score
                composite_score = (
                    cost_score * 0.4 +
                    efficiency * 0.3 +
                    confidence_score * 0.3
                )
                scores[pred.provider_name] = composite_score
            
            return max(scores.items(), key=lambda x: x[1])[0]
        
        elif self.strategy == OptimizationStrategy.CONSERVATIVE:
            # Prioritize confidence and efficiency, then cost
            scores = {}
            for pred in viable_predictions:
                efficiency = self.cost_efficiency_scores[pred.provider_name]
                confidence_score = pred.confidence
                cost_score = 1.0 / (pred.estimated_cost + 0.001)
                
                composite_score = (
                    confidence_score * 0.4 +
                    efficiency * 0.4 +
                    cost_score * 0.2
                )
                scores[pred.provider_name] = composite_score
            
            return max(scores.items(), key=lambda x: x[1])[0]
        
        else:  # DYNAMIC
            # Adapt based on current budget status
            budget_status = self.get_budget_status(BudgetPeriod.DAILY)
            
            if budget_status.utilization_percentage > 80:  # High utilization, be aggressive
                return min(viable_predictions, key=lambda p: p.estimated_cost).provider_name
            elif budget_status.utilization_percentage < 30:  # Low utilization, can be conservative
                return max(viable_predictions, key=lambda p: p.confidence).provider_name
            else:  # Medium utilization, balanced approach
                return self.select_cost_optimal_provider(
                    predictions,
                    quality_requirements,
                    constraints
                )  # Recursive call with BALANCED strategy temporarily
    
    def _can_afford_request(self, estimated_cost: float) -> bool:
        """Check if request fits within budget constraints"""
        # Check daily budget
        daily_status = self.get_budget_status(BudgetPeriod.DAILY)
        if daily_status.remaining_budget < estimated_cost:
            return False
        
        # Check if this would exceed recommended daily spend
        if estimated_cost > daily_status.recommended_daily_spend * 2:  # More than 2x recommended
            return False
        
        return True
    
    def record_actual_cost(
        self,
        provider_name: str,
        actual_cost: float,
        input_tokens: int,
        output_tokens: int,
        task_type: str = 'conversational',
        quality_score: Optional[float] = None
    ):
        """Record actual cost and usage for learning"""
        timestamp = datetime.now()
        
        # Record spending
        self.spending_history[provider_name].append((timestamp, actual_cost, task_type))
        
        # Update daily spending
        date_key = timestamp.strftime('%Y-%m-%d')
        self.daily_spending[date_key] += actual_cost
        
        # Record token usage for future predictions
        historical_key = f"{provider_name}_{task_type}"
        self.token_usage_history[historical_key].append((input_tokens, output_tokens))
        
        # Update efficiency score
        if quality_score is not None:
            # Calculate cost efficiency (quality per dollar)
            cost_efficiency = quality_score / max(actual_cost, 0.001)
            
            # Update running average
            current_score = self.cost_efficiency_scores[provider_name]
            self.cost_efficiency_scores[provider_name] = (
                current_score * 0.9 + cost_efficiency * 0.1
            )
        
        logger.debug(
            f"Recorded cost: {provider_name} ${actual_cost:.4f} "
            f"({input_tokens}+{output_tokens} tokens) quality={quality_score}"
        )
    
    def get_budget_status(self, period: BudgetPeriod) -> BudgetStatus:
        """Get current budget status for specified period"""
        now = datetime.now()
        
        # Calculate period boundaries
        if period == BudgetPeriod.DAILY:
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
            period_name = "daily"
        elif period == BudgetPeriod.WEEKLY:
            days_since_monday = now.weekday()
            period_start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            period_end = period_start + timedelta(weeks=1)
            period_name = "weekly"
        elif period == BudgetPeriod.MONTHLY:
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = period_start.replace(year=now.year + 1, month=1)
            else:
                period_end = period_start.replace(month=now.month + 1)
            period_name = "monthly"
        else:
            # Default to daily
            return self.get_budget_status(BudgetPeriod.DAILY)
        
        # Calculate spent amount in period
        spent_amount = 0.0
        for provider_history in self.spending_history.values():
            for timestamp, cost, _ in provider_history:
                if period_start <= timestamp < period_end:
                    spent_amount += cost
        
        # Get allocated budget
        allocated_budget = self.budgets[period]
        remaining_budget = allocated_budget - spent_amount
        utilization_percentage = (spent_amount / allocated_budget) * 100 if allocated_budget > 0 else 0
        
        # Calculate days remaining and projections
        time_remaining = period_end - now
        days_remaining = max(1, time_remaining.days)
        time_elapsed = now - period_start
        total_period_days = (period_end - period_start).days
        
        # Project end-of-period spend based on current trend
        if time_elapsed.total_seconds() > 0:
            spend_rate = spent_amount / (time_elapsed.total_seconds() / 86400)  # Per day
            projected_end_of_period_spend = spent_amount + (spend_rate * days_remaining)
        else:
            projected_end_of_period_spend = spent_amount
        
        # Recommended daily spend to stay on budget
        recommended_daily_spend = remaining_budget / days_remaining if days_remaining > 0 else 0
        
        return BudgetStatus(
            period=period,
            allocated_budget=allocated_budget,
            spent_amount=spent_amount,
            remaining_budget=remaining_budget,
            utilization_percentage=utilization_percentage,
            projected_end_of_period_spend=projected_end_of_period_spend,
            is_over_budget=spent_amount > allocated_budget,
            days_remaining_in_period=days_remaining,
            recommended_daily_spend=recommended_daily_spend
        )
    
    def get_cost_analytics(self) -> Dict[str, Any]:
        """Get comprehensive cost analytics"""
        analytics = {
            "budget_status": {},
            "provider_costs": {},
            "efficiency_scores": dict(self.cost_efficiency_scores),
            "spending_trends": {},
            "optimization_opportunities": []
        }
        
        # Budget status for all periods
        for period in BudgetPeriod:
            analytics["budget_status"][period.value] = self.get_budget_status(period).__dict__
        
        # Provider cost breakdown
        for provider_name, history in self.spending_history.items():
            total_cost = sum(cost for _, cost, _ in history)
            recent_cost = sum(
                cost for timestamp, cost, _ in history
                if timestamp > datetime.now() - timedelta(days=7)
            )
            
            analytics["provider_costs"][provider_name] = {
                "total_spend": total_cost,
                "recent_spend_7d": recent_cost,
                "request_count": len(history),
                "avg_cost_per_request": total_cost / len(history) if history else 0
            }
        
        # Spending trends
        daily_totals = {}
        for date_key, amount in self.daily_spending.items():
            daily_totals[date_key] = amount
        
        analytics["spending_trends"]["daily_totals"] = daily_totals
        
        # Optimization opportunities
        opportunities = []
        
        # High-cost provider identification
        if len(self.cost_models) > 1:
            provider_costs = {
                name: model.cost_per_input_token + model.cost_per_output_token
                for name, model in self.cost_models.items()
            }
            most_expensive = max(provider_costs.items(), key=lambda x: x[1])
            cheapest = min(provider_costs.items(), key=lambda x: x[1])
            
            if most_expensive[1] > cheapest[1] * 2:  # 2x difference
                opportunities.append({
                    "type": "provider_switching",
                    "description": f"Switch from {most_expensive[0]} to {cheapest[0]} could save up to {((most_expensive[1] - cheapest[1]) / most_expensive[1]) * 100:.1f}%",
                    "potential_savings": most_expensive[1] - cheapest[1]
                })
        
        # Budget optimization
        daily_status = self.get_budget_status(BudgetPeriod.DAILY)
        if daily_status.utilization_percentage > 90:
            opportunities.append({
                "type": "budget_management",
                "description": "Daily budget nearly exhausted. Consider prompt optimization or provider switching.",
                "urgency": "high"
            })
        
        analytics["optimization_opportunities"] = opportunities
        
        return analytics
    
    def update_budgets(self, new_budgets: Dict[BudgetPeriod, float]):
        """Update budget allocations"""
        for period, amount in new_budgets.items():
            if amount > 0:
                self.budgets[period] = amount
                logger.info(f"Updated {period.value} budget to ${amount:.2f}")
    
    def reset_spending_data(self, older_than_days: int = 30):
        """Clean up old spending data"""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        for provider_name in list(self.spending_history.keys()):
            original_count = len(self.spending_history[provider_name])
            self.spending_history[provider_name] = [
                (timestamp, cost, task_type)
                for timestamp, cost, task_type in self.spending_history[provider_name]
                if timestamp > cutoff_date
            ]
            
            removed_count = original_count - len(self.spending_history[provider_name])
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old spending records for {provider_name}")
        
        # Clean up daily spending data
        cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
        old_dates = [
            date_key for date_key in self.daily_spending.keys()
            if date_key < cutoff_date_str
        ]
        
        for date_key in old_dates:
            del self.daily_spending[date_key]
        
        logger.info(f"Cleaned up spending data older than {older_than_days} days")
