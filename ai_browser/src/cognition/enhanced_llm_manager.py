"""Enhanced Production-Ready LLM Manager

This module integrates all advanced LLM orchestration components:
- Multi-model orchestration with intelligent routing
- Cost optimization and budget management
- Reliability and failover mechanisms
- Comprehensive monitoring and alerting
- Performance optimization strategies
- Production deployment utilities
"""

from typing import Dict, Any, List, Optional, Type, Union, Tuple, AsyncGenerator
from pydantic import BaseModel
from loguru import logger
import asyncio
import time
from datetime import datetime
import uuid

from .llm import LLMManager, ILLMProvider
from .llm_orchestrator import (
    LLMOrchestrator, RequestContext, TaskType, RoutingStrategy,
    ProviderCapability, OrchestrationResult, create_smart_context
)
from .cost_optimizer import CostOptimizer, OptimizationStrategy, BudgetPeriod
from .reliability_manager import ReliabilityManager, FailoverStrategy
from .llm_monitoring import LLMMonitoringSystem, AlertSeverity


class ProductionLLMManager:
    """Production-ready LLM manager with full orchestration capabilities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize base LLM manager
        self.llm_manager = LLMManager(
            default_provider=self.config.get('default_provider'),
            auto_load=self.config.get('auto_load_providers', True)
        )
        
        # Initialize orchestration components
        self._initialize_orchestration()
        
        # Performance optimization settings
        self.performance_config = self.config.get('performance', {})
        self._initialize_performance_optimizations()
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._start_background_tasks()
        
        logger.info(f"Initialized ProductionLLMManager with {len(self.llm_manager.list_providers())} providers")
    
    def _initialize_orchestration(self):
        """Initialize orchestration components"""
        providers = self.llm_manager.list_providers()
        
        # Cost optimization
        cost_models = self.llm_orchestrator.COST_MODELS if hasattr(self, 'llm_orchestrator') else {}
        self.cost_optimizer = CostOptimizer(
            cost_models=cost_models,
            config=self.config.get('cost_optimization', {})
        )
        
        # Reliability management
        self.reliability_manager = ReliabilityManager(
            providers=providers,
            config=self.config.get('reliability', {})
        )
        
        # Monitoring system
        self.monitoring = LLMMonitoringSystem(
            config=self.config.get('monitoring', {})
        )
        self.monitoring.set_cost_tracker(self.cost_optimizer)
        
        # Main orchestrator
        self.llm_orchestrator = LLMOrchestrator(
            llm_manager=self.llm_manager,
            config=self.config.get('orchestration', {})
        )
        
        # Setup monitoring integration
        self._setup_monitoring_integration()
    
    def _setup_monitoring_integration(self):
        """Setup monitoring integration with other components"""
        # Setup custom alerts based on configuration
        custom_alerts = self.config.get('alerts', [])
        for alert_config in custom_alerts:
            self.monitoring.alert_manager.create_alert(
                alert_id=alert_config['id'],
                name=alert_config['name'],
                description=alert_config['description'],
                metric_name=alert_config['metric'],
                threshold_value=alert_config['threshold'],
                comparison_operator=alert_config['operator'],
                severity=AlertSeverity(alert_config.get('severity', 'warning')),
                notification_channels=alert_config.get('channels', [])
            )
        
        # Setup notification handlers
        notification_config = self.config.get('notifications', {})
        if 'console' in notification_config:
            from .llm_monitoring import console_notification_handler
            self.monitoring.alert_manager.register_notification_handler(
                'console', console_notification_handler
            )
    
    def _initialize_performance_optimizations(self):
        """Initialize performance optimization settings"""
        self.performance_settings = {
            'enable_caching': self.performance_config.get('enable_caching', True),
            'cache_ttl': self.performance_config.get('cache_ttl', 300),
            'enable_batching': self.performance_config.get('enable_batching', False),
            'batch_size': self.performance_config.get('batch_size', 5),
            'enable_streaming': self.performance_config.get('enable_streaming', False),
            'connection_pooling': self.performance_config.get('connection_pooling', True),
            'max_concurrent': self.performance_config.get('max_concurrent', 10)
        }
        
        # Connection pool for concurrent requests
        self.request_semaphore = asyncio.Semaphore(
            self.performance_settings['max_concurrent']
        )
        
        # Request batching queue
        if self.performance_settings['enable_batching']:
            self.batch_queue = asyncio.Queue()
            self.batch_processor_task = None
    
    def _start_background_tasks(self):
        """Start background optimization and maintenance tasks"""
        # Performance metrics collection
        task = asyncio.create_task(self._performance_metrics_collector())
        self._background_tasks.append(task)
        
        # Provider health synchronization
        task = asyncio.create_task(self._sync_provider_health())
        self._background_tasks.append(task)
        
        # Cost tracking synchronization
        task = asyncio.create_task(self._sync_cost_tracking())
        self._background_tasks.append(task)
        
        # Batch processing if enabled
        if self.performance_settings['enable_batching']:
            task = asyncio.create_task(self._batch_processor())
            self._background_tasks.append(task)
    
    async def generate(
        self,
        prompt: str,
        task_type: Optional[TaskType] = None,
        routing_strategy: Optional[RoutingStrategy] = None,
        max_cost: Optional[float] = None,
        max_latency_ms: Optional[int] = None,
        required_capabilities: Optional[List[ProviderCapability]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> OrchestrationResult:
        """Generate response with full orchestration"""
        # Create request context
        if task_type or routing_strategy or max_cost or max_latency_ms or required_capabilities:
            context = RequestContext(
                task_type=task_type or TaskType.CONVERSATIONAL,
                routing_strategy=routing_strategy or RoutingStrategy.BALANCED,
                max_cost=max_cost,
                max_latency_ms=max_latency_ms,
                required_capabilities=required_capabilities or [],
                user_id=kwargs.get('user_id'),
                session_id=kwargs.get('session_id'),
                conversation_id=kwargs.get('conversation_id')
            )
        else:
            context = await create_smart_context(
                task_description=prompt,
                user_preferences=user_preferences
            )
        
        # Apply performance optimizations
        if self.performance_settings['enable_caching']:
            context.cache_enabled = True
            context.cache_ttl_seconds = self.performance_settings['cache_ttl']
        
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        
        # Start monitoring
        selected_provider = None
        try:
            # Use orchestrator for execution
            async with self.request_semaphore:  # Limit concurrency
                result = await self.llm_orchestrator.orchestrate(
                    prompt=prompt,
                    context=context,
                    **kwargs
                )
            
            # Track the request
            selected_provider = result.provider_used
            if selected_provider:
                self.monitoring.start_request_tracking(
                    request_id, selected_provider, context.task_type.value
                )
                
                self.monitoring.finish_request_tracking(
                    request_id=request_id,
                    success=result.success,
                    response_length=len(str(result.response)) if result.response else 0,
                    cost=result.actual_cost,
                    tokens_used=result.tokens_used,
                    quality_score=result.quality_score
                )
            
            return result
            
        except Exception as e:
            # Track failed request
            if selected_provider:
                self.monitoring.finish_request_tracking(
                    request_id=request_id,
                    success=False,
                    error=str(e)
                )
            
            logger.error(f"Request {request_id} failed: {e}")
            raise
    
    async def generate_structured(
        self,
        prompt: str,
        output_model: Type[BaseModel],
        task_type: Optional[TaskType] = None,
        **kwargs
    ) -> OrchestrationResult:
        """Generate structured response"""
        # Structured output typically requires reasoning capability
        if not task_type:
            task_type = TaskType.STRUCTURED
        
        required_capabilities = kwargs.get('required_capabilities', [])
        if ProviderCapability.STRUCTURED_OUTPUT not in required_capabilities:
            required_capabilities.append(ProviderCapability.STRUCTURED_OUTPUT)
        
        kwargs['required_capabilities'] = required_capabilities
        
        return await self.generate(
            prompt=prompt,
            task_type=task_type,
            output_model=output_model,
            **kwargs
        )
    
    async def generate_with_images(
        self,
        prompt: str,
        images: List[Union[str, bytes]],
        task_type: Optional[TaskType] = None,
        **kwargs
    ) -> OrchestrationResult:
        """Generate response with image inputs"""
        if not task_type:
            task_type = TaskType.MULTIMODAL
        
        required_capabilities = kwargs.get('required_capabilities', [])
        if ProviderCapability.VISION not in required_capabilities:
            required_capabilities.append(ProviderCapability.VISION)
        
        kwargs['required_capabilities'] = required_capabilities
        
        return await self.generate(
            prompt=prompt,
            task_type=task_type,
            images=images,
            **kwargs
        )
    
    async def batch_generate(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: Optional[int] = None
    ) -> List[OrchestrationResult]:
        """Process multiple requests concurrently"""
        if not self.performance_settings['enable_batching']:
            logger.warning("Batching not enabled, processing sequentially")
        
        max_concurrent = max_concurrent or self.performance_settings['batch_size']
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_request(request_data: Dict[str, Any]) -> OrchestrationResult:
            async with semaphore:
                return await self.generate(**request_data)
        
        tasks = [process_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(OrchestrationResult(
                    success=False,
                    error=str(result),
                    total_latency_ms=0,
                    actual_cost=0.0,
                    tokens_used=0
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def stream_generate(
        self,
        prompt: str,
        task_type: Optional[TaskType] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response generation (if supported by provider)"""
        if not self.performance_settings['enable_streaming']:
            # Fallback to regular generation
            result = await self.generate(prompt, task_type, **kwargs)
            if result.success and result.response:
                yield str(result.response)
            return
        
        # For streaming, we need to select provider first
        context = await create_smart_context(
            task_description=prompt,
            user_preferences=kwargs.get('user_preferences')
        )
        
        selection = await self.llm_orchestrator._select_provider(prompt, context)
        provider = self.llm_manager.get_provider(selection.primary_provider)
        
        # Check if provider supports streaming
        if hasattr(provider, 'stream_generate'):
            async for chunk in provider.stream_generate(prompt, **kwargs):
                yield chunk
        else:
            # Fallback to regular generation
            result = await self.generate(prompt, task_type, **kwargs)
            if result.success and result.response:
                yield str(result.response)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            "orchestrator_metrics": self.llm_orchestrator.get_metrics_summary(),
            "reliability_status": self.reliability_manager.get_reliability_status(),
            "cost_analytics": self.cost_optimizer.get_cost_analytics(),
            "monitoring_report": self.monitoring.get_performance_report(),
            "performance_settings": self.performance_settings
        }
    
    def get_provider_comparison(self) -> Dict[str, Any]:
        """Get detailed provider comparison"""
        comparison = {}
        
        for provider_name in self.llm_manager.list_providers():
            # Get metrics from orchestrator
            orchestrator_metrics = self.llm_orchestrator.provider_metrics.get(provider_name)
            
            # Get reliability data
            reliability_data = self.reliability_manager.health_data.get(provider_name)
            
            # Get cost data
            cost_analytics = self.cost_optimizer.get_cost_analytics()
            provider_costs = cost_analytics.get('provider_costs', {}).get(provider_name, {})
            
            comparison[provider_name] = {
                "health_score": reliability_data.health_score if reliability_data else 0.0,
                "success_rate": orchestrator_metrics.availability if orchestrator_metrics else 0.0,
                "avg_latency_ms": orchestrator_metrics.avg_latency_ms if orchestrator_metrics else 0.0,
                "total_cost": provider_costs.get('total_spend', 0.0),
                "avg_cost_per_request": provider_costs.get('avg_cost_per_request', 0.0),
                "total_requests": orchestrator_metrics.total_requests if orchestrator_metrics else 0,
                "capabilities": list(self.llm_orchestrator.PROVIDER_CAPABILITIES.get(provider_name, {}).keys()),
                "status": reliability_data.status.value if reliability_data else "unknown"
            }
        
        return comparison
    
    async def optimize_performance(self, target_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Optimize system performance based on target metrics"""
        optimization_results = {
            "optimizations_applied": [],
            "performance_impact": {},
            "recommendations": []
        }
        
        current_metrics = self.get_performance_metrics()
        
        # Cost optimization
        if 'max_cost_per_request' in target_metrics:
            target_cost = target_metrics['max_cost_per_request']
            current_avg_cost = current_metrics['cost_analytics'].get('provider_costs', {}).get('avg_cost_per_request', 0)
            
            if current_avg_cost > target_cost:
                # Switch to more cost-effective strategy
                old_strategy = self.cost_optimizer.strategy
                self.cost_optimizer.strategy = OptimizationStrategy.AGGRESSIVE
                
                optimization_results['optimizations_applied'].append(
                    f"Switched cost strategy from {old_strategy} to {OptimizationStrategy.AGGRESSIVE}"
                )
        
        # Latency optimization
        if 'max_latency_ms' in target_metrics:
            target_latency = target_metrics['max_latency_ms']
            
            # Enable caching if not already enabled
            if not self.performance_settings['enable_caching']:
                self.performance_settings['enable_caching'] = True
                optimization_results['optimizations_applied'].append("Enabled response caching")
            
            # Increase concurrency if latency is high
            current_concurrent = self.performance_settings['max_concurrent']
            if current_concurrent < 20:  # Reasonable limit
                new_concurrent = min(current_concurrent * 2, 20)
                self.performance_settings['max_concurrent'] = new_concurrent
                self.request_semaphore = asyncio.Semaphore(new_concurrent)
                
                optimization_results['optimizations_applied'].append(
                    f"Increased max concurrent requests from {current_concurrent} to {new_concurrent}"
                )
        
        # Reliability optimization
        if 'min_success_rate' in target_metrics:
            target_success_rate = target_metrics['min_success_rate']
            
            # Switch to reliability-focused routing
            reliability_config = self.reliability_manager.config
            if reliability_config.get('failover_strategy') != FailoverStrategy.RELIABILITY_OPTIMIZED:
                reliability_config['failover_strategy'] = FailoverStrategy.RELIABILITY_OPTIMIZED
                optimization_results['optimizations_applied'].append(
                    "Switched to reliability-optimized failover strategy"
                )
        
        # Generate recommendations
        recommendations = self._generate_performance_recommendations(current_metrics, target_metrics)
        optimization_results['recommendations'] = recommendations
        
        return optimization_results
    
    def _generate_performance_recommendations(self, current_metrics: Dict[str, Any], target_metrics: Dict[str, float]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Analyze current state and suggest improvements
        reliability_status = current_metrics['reliability_status']
        overall_health = reliability_status['overall_health']
        
        if overall_health['score'] < 0.8:
            recommendations.append(
                "Consider reviewing provider health - overall health score is below 80%"
            )
        
        # Cost recommendations
        cost_analytics = current_metrics['cost_analytics']
        opportunities = cost_analytics.get('optimization_opportunities', [])
        
        for opportunity in opportunities:
            recommendations.append(f"Cost optimization: {opportunity['description']}")
        
        # Performance recommendations
        if not self.performance_settings['enable_caching']:
            recommendations.append("Enable response caching to improve latency and reduce costs")
        
        if not self.performance_settings['enable_batching']:
            recommendations.append("Enable request batching for high-throughput scenarios")
        
        return recommendations
    
    async def _performance_metrics_collector(self):
        """Background task for performance metrics collection"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Update system metrics
                active_requests = self.performance_settings['max_concurrent'] - self.request_semaphore._value
                queue_depth = 0  # Would track actual queue if implemented
                
                self.monitoring.update_system_metrics(
                    queue_depth=queue_depth,
                    concurrent_requests=active_requests
                )
                
            except Exception as e:
                logger.error(f"Performance metrics collection error: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def _sync_provider_health(self):
        """Synchronize provider health between components"""
        while True:
            try:
                await asyncio.sleep(30)  # Sync every 30 seconds
                
                # Get health data from reliability manager
                reliability_status = self.reliability_manager.get_reliability_status()
                
                # Update monitoring with provider health
                for provider_name, provider_data in reliability_status['providers'].items():
                    health_data = {
                        'availability': provider_data['success_rate'],
                        'error_rate': provider_data['error_rate']
                    }
                    self.monitoring.update_provider_health_metrics(provider_name, health_data)
                
            except Exception as e:
                logger.error(f"Provider health sync error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _sync_cost_tracking(self):
        """Synchronize cost tracking data"""
        while True:
            try:
                await asyncio.sleep(300)  # Sync every 5 minutes
                
                # Update cost optimizer with latest usage data
                orchestrator_metrics = self.llm_orchestrator.get_metrics_summary()
                
                for provider_name, metrics in orchestrator_metrics['providers'].items():
                    if metrics.get('total_cost', 0) > 0:
                        self.cost_optimizer.record_actual_cost(
                            provider_name=provider_name,
                            actual_cost=metrics['total_cost'],
                            input_tokens=metrics.get('total_tokens', 0) // 2,  # Estimate
                            output_tokens=metrics.get('total_tokens', 0) // 2,  # Estimate
                            quality_score=0.8  # Default quality score
                        )
                
            except Exception as e:
                logger.error(f"Cost tracking sync error: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def _batch_processor(self):
        """Process batched requests"""
        while True:
            try:
                batch_requests = []
                
                # Collect requests for batching
                try:
                    # Wait for first request
                    first_request = await asyncio.wait_for(
                        self.batch_queue.get(),
                        timeout=1.0
                    )
                    batch_requests.append(first_request)
                    
                    # Collect additional requests up to batch size
                    for _ in range(self.performance_settings['batch_size'] - 1):
                        try:
                            request = await asyncio.wait_for(
                                self.batch_queue.get(),
                                timeout=0.1  # Short timeout for additional requests
                            )
                            batch_requests.append(request)
                        except asyncio.TimeoutError:
                            break  # No more requests available
                    
                except asyncio.TimeoutError:
                    continue  # No requests to process
                
                # Process batch
                if batch_requests:
                    logger.debug(f"Processing batch of {len(batch_requests)} requests")
                    results = await self.batch_generate(batch_requests)
                    
                    # Return results to original callers (would need future/callback mechanism)
                    # This is a simplified implementation
                    
            except Exception as e:
                logger.error(f"Batch processor error: {e}")
                await asyncio.sleep(10)  # Brief pause on error
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {},
            "providers": {},
            "alerts": {
                "active_count": 0,
                "critical_count": 0
            }
        }
        
        # Check LLM manager
        try:
            providers = self.llm_manager.list_providers()
            health_status["components"]["llm_manager"] = {
                "status": "healthy",
                "provider_count": len(providers)
            }
        except Exception as e:
            health_status["components"]["llm_manager"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check reliability manager
        try:
            reliability_status = self.reliability_manager.get_reliability_status()
            overall_health = reliability_status["overall_health"]
            
            health_status["components"]["reliability_manager"] = {
                "status": overall_health["status"],
                "health_score": overall_health["score"],
                "healthy_providers": overall_health["healthy_providers"],
                "total_providers": overall_health["total_providers"]
            }
            
            if overall_health["status"] in ["degraded", "critical"]:
                health_status["overall_status"] = "degraded"
            
            # Provider details
            for provider_name, provider_data in reliability_status["providers"].items():
                health_status["providers"][provider_name] = {
                    "status": provider_data["status"],
                    "health_score": provider_data["health_score"],
                    "success_rate": provider_data["success_rate"]
                }
                
        except Exception as e:
            health_status["components"]["reliability_manager"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "unhealthy"
        
        # Check monitoring system
        try:
            active_alerts = self.monitoring.alert_manager.get_active_alerts()
            critical_alerts = [alert for alert in active_alerts if alert.severity == AlertSeverity.CRITICAL]
            
            health_status["components"]["monitoring"] = {
                "status": "healthy",
                "active_alerts": len(active_alerts),
                "critical_alerts": len(critical_alerts)
            }
            
            health_status["alerts"]["active_count"] = len(active_alerts)
            health_status["alerts"]["critical_count"] = len(critical_alerts)
            
            if len(critical_alerts) > 0:
                health_status["overall_status"] = "critical"
            elif len(active_alerts) > 5:
                health_status["overall_status"] = "degraded"
                
        except Exception as e:
            health_status["components"]["monitoring"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown all components"""
        logger.info("Shutting down ProductionLLMManager")
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Shutdown components
        await self.llm_orchestrator.shutdown()
        await self.reliability_manager.shutdown()
        await self.monitoring.shutdown()
        
        logger.info("ProductionLLMManager shutdown complete")


# Utility functions for production deployment

def load_production_config(config_path: str) -> Dict[str, Any]:
    """Load production configuration from file"""
    import json
    from pathlib import Path
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    logger.info(f"Loaded production configuration from {config_path}")
    return config


async def create_production_llm_manager(
    config_path: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> ProductionLLMManager:
    """Create and initialize production LLM manager"""
    if config_path:
        config = load_production_config(config_path)
    elif config is None:
        config = {}
    
    manager = ProductionLLMManager(config)
    
    # Wait a moment for background tasks to start
    await asyncio.sleep(1)
    
    # Perform initial health check
    health = await manager.health_check()
    logger.info(f"Production LLM Manager initialized with status: {health['overall_status']}")
    
    return manager


def validate_production_config(config: Dict[str, Any]) -> List[str]:
    """Validate production configuration and return list of issues"""
    issues = []
    
    # Check required sections
    required_sections = ['cognition', 'reliability', 'monitoring', 'performance']
    for section in required_sections:
        if section not in config:
            issues.append(f"Missing required configuration section: {section}")
    
    # Validate cognition config
    cognition_config = config.get('cognition', {})
    if 'providers' not in cognition_config:
        issues.append("Missing providers configuration in cognition section")
    
    # Validate reliability config
    reliability_config = config.get('reliability', {})
    failover_strategy = reliability_config.get('failover_strategy', 'circuit_breaker')
    if failover_strategy not in [s.value for s in FailoverStrategy]:
        issues.append(f"Invalid failover strategy: {failover_strategy}")
    
    # Validate monitoring config
    monitoring_config = config.get('monitoring', {})
    if 'alerts' in monitoring_config:
        for alert in monitoring_config['alerts']:
            required_fields = ['id', 'name', 'metric', 'threshold', 'operator']
            for field in required_fields:
                if field not in alert:
                    issues.append(f"Missing required alert field: {field}")
    
    return issues


# Production deployment example
async def example_production_deployment():
    """Example of production deployment"""
    # Load configuration
    config = {
        'default_provider': 'openai',
        'cognition': {
            'providers': {
                'openai': {'enabled': True, 'model': 'gpt-4-turbo-preview'},
                'anthropic': {'enabled': True, 'model': 'claude-3-opus-20240229'},
                'gemini': {'enabled': True, 'model': 'gemini-pro'}
            }
        },
        'cost_optimization': {
            'optimization_strategy': 'balanced',
            'daily_budget': 100.0,
            'weekly_budget': 500.0,
            'monthly_budget': 2000.0
        },
        'reliability': {
            'failover_strategy': 'circuit_breaker',
            'max_retries': 3,
            'circuit_breaker_failure_threshold': 5
        },
        'monitoring': {
            'metrics_retention_hours': 48,
            'alerts': [
                {
                    'id': 'high_cost',
                    'name': 'High Daily Cost',
                    'metric': 'daily_cost',
                    'threshold': 80.0,
                    'operator': '>',
                    'severity': 'warning'
                }
            ]
        },
        'performance': {
            'enable_caching': True,
            'enable_batching': True,
            'max_concurrent': 10
        }
    }
    
    # Validate configuration
    issues = validate_production_config(config)
    if issues:
        logger.warning(f"Configuration issues found: {issues}")
    
    # Create production manager
    manager = await create_production_llm_manager(config=config)
    
    try:
        # Example usage
        result = await manager.generate(
            prompt="Explain quantum computing in simple terms",
            task_type=TaskType.CONVERSATIONAL,
            routing_strategy=RoutingStrategy.COST_OPTIMIZED,
            max_cost=0.10
        )
        
        print(f"Response: {result.response}")
        print(f"Provider used: {result.provider_used}")
        print(f"Cost: ${result.actual_cost:.4f}")
        print(f"Success: {result.success}")
        
        # Get performance metrics
        metrics = manager.get_performance_metrics()
        print(f"\nPerformance metrics: {json.dumps(metrics, indent=2, default=str)}")
        
    finally:
        # Cleanup
        await manager.shutdown()


# Alias for backward compatibility with examples
EnhancedLLMManager = ProductionLLMManager


if __name__ == "__main__":
    # Run example deployment
    asyncio.run(example_production_deployment())
