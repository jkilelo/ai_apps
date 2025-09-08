"""Comprehensive tests for production LLM integration system"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json

from src.cognition.enhanced_llm_manager import ProductionLLMManager, create_production_llm_manager
from src.cognition.llm_orchestrator import RequestContext, TaskType, RoutingStrategy, OrchestrationResult
from src.cognition.cost_optimizer import CostOptimizer, OptimizationStrategy, BudgetPeriod
from src.cognition.reliability_manager import ReliabilityManager, HealthStatus
from src.cognition.llm_monitoring import LLMMonitoringSystem, AlertSeverity


class TestProductionLLMManager:
    """Test suite for ProductionLLMManager"""
    
    @pytest.fixture
    async def production_config(self):
        """Test configuration for production manager"""
        return {
            'default_provider': 'openai',
            'cognition': {
                'providers': {
                    'openai': {
                        'enabled': True,
                        'model': 'gpt-4-turbo-preview',
                        'rate_limit': {'requests_per_minute': 60}
                    },
                    'anthropic': {
                        'enabled': True,
                        'model': 'claude-3-opus-20240229',
                        'rate_limit': {'requests_per_minute': 50}
                    },
                    'gemini': {
                        'enabled': True,
                        'model': 'gemini-pro',
                        'rate_limit': {'requests_per_minute': 60}
                    }
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
                'circuit_breaker_failure_threshold': 5,
                'health_check_enabled': True
            },
            'monitoring': {
                'metrics_retention_hours': 24,
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
                'cache_ttl': 300,
                'enable_batching': True,
                'batch_size': 5,
                'max_concurrent': 10
            }
        }
    
    @pytest.fixture
    async def mock_llm_manager(self):
        """Mock LLM manager with providers"""
        mock_manager = Mock()
        mock_manager.list_providers.return_value = ['openai', 'anthropic', 'gemini']
        mock_manager.get_provider = Mock()
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.estimate_tokens.return_value = 100
        mock_provider.generate.return_value = "Test response"
        mock_provider.get_name.return_value = "openai"
        mock_provider.get_model.return_value = "gpt-4-turbo-preview"
        mock_provider.get_max_context_window.return_value = 128000
        
        mock_manager.get_provider.return_value = mock_provider
        return mock_manager
    
    @pytest.mark.asyncio
    async def test_production_manager_initialization(self, production_config):
        """Test production manager initializes correctly"""
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['openai', 'anthropic', 'gemini']
            mock_llm_manager_class.return_value = mock_llm_manager
            
            manager = ProductionLLMManager(production_config)
            
            # Verify components are initialized
            assert manager.llm_manager is not None
            assert manager.cost_optimizer is not None
            assert manager.reliability_manager is not None
            assert manager.monitoring is not None
            assert manager.llm_orchestrator is not None
            
            # Verify configuration is applied
            assert manager.performance_settings['enable_caching'] is True
            assert manager.performance_settings['max_concurrent'] == 10
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_generate_with_orchestration(self, production_config):
        """Test generate method with full orchestration"""
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['openai', 'anthropic', 'gemini']
            mock_llm_manager_class.return_value = mock_llm_manager
            
            manager = ProductionLLMManager(production_config)
            
            # Mock orchestrator response
            mock_result = OrchestrationResult(
                success=True,
                response="Test response",
                provider_used="openai",
                total_latency_ms=500,
                actual_cost=0.05,
                tokens_used=150
            )\
            \n            manager.llm_orchestrator.orchestrate = AsyncMock(return_value=mock_result)
            \n            # Test generation
            result = await manager.generate(
                prompt="Test prompt",
                task_type=TaskType.CONVERSATIONAL,
                routing_strategy=RoutingStrategy.COST_OPTIMIZED
            )
            
            assert result.success is True
            assert result.response == "Test response"
            assert result.provider_used == "openai"
            assert result.actual_cost == 0.05
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_structured_generation(self, production_config):
        """Test structured output generation"""
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            action: str
            confidence: float
        
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['openai']
            mock_llm_manager_class.return_value = mock_llm_manager
            
            manager = ProductionLLMManager(production_config)
            
            # Mock structured response
            mock_result = OrchestrationResult(
                success=True,
                response=TestModel(action="click", confidence=0.9),
                provider_used="openai",
                total_latency_ms=600,
                actual_cost=0.08,
                tokens_used=200
            )
            
            manager.llm_orchestrator.orchestrate = AsyncMock(return_value=mock_result)
            
            result = await manager.generate_structured(
                prompt="Generate action",
                output_model=TestModel,
                task_type=TaskType.STRUCTURED
            )
            
            assert result.success is True
            assert isinstance(result.response, TestModel)
            assert result.response.action == "click"
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_batch_generation(self, production_config):
        """Test batch processing of requests"""
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['openai']
            mock_llm_manager_class.return_value = mock_llm_manager
            
            manager = ProductionLLMManager(production_config)
            
            # Mock individual responses
            mock_results = [
                OrchestrationResult(
                    success=True,
                    response=f"Response {i}",
                    provider_used="openai",
                    total_latency_ms=400 + i * 50,
                    actual_cost=0.03 + i * 0.01,
                    tokens_used=100 + i * 25
                ) for i in range(3)
            ]
            
            # Mock the generate method to return sequential results
            manager.generate = AsyncMock(side_effect=mock_results)
            
            requests = [
                {"prompt": f"Test prompt {i}", "task_type": TaskType.CONVERSATIONAL}
                for i in range(3)
            ]
            
            results = await manager.batch_generate(requests)
            
            assert len(results) == 3
            for i, result in enumerate(results):
                assert result.success is True
                assert result.response == f"Response {i}"
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_performance_optimization(self, production_config):
        """Test performance optimization functionality"""
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['openai']
            mock_llm_manager_class.return_value = mock_llm_manager
            
            manager = ProductionLLMManager(production_config)
            
            # Mock current metrics
            mock_metrics = {
                'orchestrator_metrics': {'providers': {}},
                'reliability_status': {'overall_health': {'score': 0.9}},
                'cost_analytics': {'provider_costs': {'avg_cost_per_request': 0.15}},
                'monitoring_report': {},
                'performance_settings': manager.performance_settings
            }
            
            manager.get_performance_metrics = Mock(return_value=mock_metrics)
            
            # Test optimization with target metrics
            target_metrics = {
                'max_cost_per_request': 0.10,
                'max_latency_ms': 1000,
                'min_success_rate': 0.95
            }
            
            optimization_results = await manager.optimize_performance(target_metrics)
            
            assert 'optimizations_applied' in optimization_results
            assert 'recommendations' in optimization_results
            assert isinstance(optimization_results['optimizations_applied'], list)
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_health_check(self, production_config):
        """Test comprehensive health check"""
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['openai', 'anthropic']
            mock_llm_manager_class.return_value = mock_llm_manager
            
            manager = ProductionLLMManager(production_config)
            
            # Mock reliability status
            mock_reliability_status = {
                'overall_health': {
                    'status': 'healthy',
                    'score': 0.95,
                    'healthy_providers': 2,
                    'total_providers': 2
                },
                'providers': {
                    'openai': {'status': 'healthy', 'health_score': 0.96, 'success_rate': 0.98},
                    'anthropic': {'status': 'healthy', 'health_score': 0.94, 'success_rate': 0.97}
                }\n            }
            
            manager.reliability_manager.get_reliability_status = Mock(return_value=mock_reliability_status)
            manager.monitoring.alert_manager.get_active_alerts = Mock(return_value=[])
            
            health = await manager.health_check()
            
            assert health['overall_status'] == 'healthy'
            assert 'components' in health
            assert 'providers' in health
            assert len(health['providers']) == 2
            assert health['alerts']['active_count'] == 0
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_error_handling_and_failover(self, production_config):
        """Test error handling and failover mechanisms"""
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['openai', 'anthropic']
            mock_llm_manager_class.return_value = mock_llm_manager
            
            manager = ProductionLLMManager(production_config)
            
            # Mock orchestrator to simulate failure then success
            manager.llm_orchestrator.orchestrate = AsyncMock(side_effect=[
                OrchestrationResult(
                    success=False,
                    error="Provider timeout",
                    total_latency_ms=5000,
                    actual_cost=0.0,
                    tokens_used=0,
                    fallback_used=True
                )
            ])
            
            result = await manager.generate(
                prompt="Test prompt",
                task_type=TaskType.CONVERSATIONAL
            )
            
            # Verify error was handled
            assert result.success is False
            assert result.error == "Provider timeout"
            assert result.fallback_used is True
            
            await manager.shutdown()


class TestCostOptimizer:
    """Test suite for cost optimization functionality"""
    
    @pytest.fixture
    def cost_models(self):
        """Sample cost models for testing"""
        from src.cognition.llm_orchestrator import CostModel
        return {
            'openai': CostModel(
                provider_name='openai',
                cost_per_input_token=0.00001,
                cost_per_output_token=0.00003
            ),
            'anthropic': CostModel(
                provider_name='anthropic',
                cost_per_input_token=0.000015,
                cost_per_output_token=0.000075
            ),
            'gemini': CostModel(
                provider_name='gemini',
                cost_per_input_token=0.0000035,
                cost_per_output_token=0.0000105
            )
        }
    
    def test_cost_prediction(self, cost_models):
        """Test cost prediction for requests"""
        optimizer = CostOptimizer(cost_models)
        
        prediction = optimizer.predict_request_cost(
            prompt="Test prompt " * 100,  # ~400 characters
            provider_name="openai",
            task_type="conversational"
        )
        
        assert prediction.provider_name == "openai"
        assert prediction.estimated_cost > 0
        assert prediction.confidence > 0
        assert len(prediction.factors_considered) > 0
        assert len(prediction.optimization_suggestions) >= 0
    
    def test_provider_selection_cost_optimized(self, cost_models):
        """Test cost-optimized provider selection"""
        optimizer = CostOptimizer(cost_models)
        
        # Generate predictions for all providers
        predictions = []
        for provider in cost_models.keys():
            pred = optimizer.predict_request_cost(
                prompt="Test prompt",
                provider_name=provider,
                task_type="conversational"
            )
            predictions.append(pred)
        
        # Select cheapest provider
        selected = optimizer.select_cost_optimal_provider(predictions)
        
        # Gemini should be cheapest based on our cost models
        assert selected == "gemini"
    
    def test_budget_tracking(self, cost_models):
        """Test budget tracking and status"""
        optimizer = CostOptimizer(cost_models)
        
        # Record some costs
        optimizer.record_actual_cost(
            provider_name="openai",
            actual_cost=5.50,
            input_tokens=1000,
            output_tokens=500,
            quality_score=0.9
        )
        
        # Check budget status
        daily_status = optimizer.get_budget_status(BudgetPeriod.DAILY)
        
        assert daily_status.spent_amount == 5.50
        assert daily_status.remaining_budget == optimizer.budgets[BudgetPeriod.DAILY] - 5.50
        assert daily_status.utilization_percentage > 0
    
    def test_token_optimization(self, cost_models):
        """Test token usage optimization"""
        optimizer = CostOptimizer(cost_models)
        token_optimizer = optimizer.token_optimizer
        
        long_prompt = """
        Please help me understand the complex topic of quantum computing.
        I would like you to explain it in great detail with examples.
        Can you please provide a comprehensive overview that covers all aspects?
        """
        
        optimized_prompt, reduction = token_optimizer.optimize_prompt_for_cost(
            long_prompt, target_reduction=0.30
        )
        
        assert len(optimized_prompt) <= len(long_prompt)
        assert reduction > 0
    
    def test_cost_analytics(self, cost_models):
        """Test cost analytics generation"""
        optimizer = CostOptimizer(cost_models)
        
        # Record some usage
        optimizer.record_actual_cost("openai", 2.50, 500, 300, 0.85)
        optimizer.record_actual_cost("anthropic", 1.80, 400, 250, 0.90)
        optimizer.record_actual_cost("gemini", 0.95, 600, 200, 0.80)
        
        analytics = optimizer.get_cost_analytics()
        
        assert 'budget_status' in analytics
        assert 'provider_costs' in analytics
        assert 'efficiency_scores' in analytics
        assert 'optimization_opportunities' in analytics
        
        # Check provider cost data
        assert 'openai' in analytics['provider_costs']
        assert analytics['provider_costs']['openai']['total_spend'] == 2.50


class TestReliabilityManager:
    """Test suite for reliability management"""
    
    def test_provider_health_tracking(self):
        """Test provider health tracking"""
        providers = ['openai', 'anthropic', 'gemini']
        manager = ReliabilityManager(providers)
        
        # Simulate successful requests
        manager._record_success('openai', 500.0)
        manager._record_success('openai', 600.0)
        manager._record_success('openai', 450.0)
        
        health = manager.health_data['openai']
        assert health.consecutive_successes == 3
        assert health.consecutive_failures == 0
        assert health.success_rate > 0
        assert health.status in [HealthStatus.HEALTHY, HealthStatus.RECOVERING]
    
    def test_circuit_breaker_functionality(self):
        """Test circuit breaker pattern"""
        providers = ['openai']
        manager = ReliabilityManager(providers)
        
        circuit = manager.circuit_breakers['openai']
        
        # Initially closed
        assert circuit.can_execute() is True
        
        # Record failures to open circuit
        for _ in range(6):  # More than failure threshold (5)
            manager._record_failure('openai', 1000.0, "Connection timeout")
        
        # Circuit should be open
        assert circuit.can_execute() is False
        
        # Simulate time passage for recovery
        circuit.last_failure_time = datetime.now() - timedelta(seconds=70)  # Past timeout
        
        # Should transition to half-open
        assert circuit.can_execute() is True
    
    @pytest.mark.asyncio
    async def test_reliability_execution(self):
        """Test execution with reliability management"""
        providers = ['openai', 'anthropic']
        manager = ReliabilityManager(providers)
        
        # Mock executor that fails first provider, succeeds with second
        call_count = 0
        async def mock_executor(provider):
            nonlocal call_count
            call_count += 1
            if provider == 'openai' and call_count == 1:
                raise Exception("Provider timeout")
            return f"Success with {provider}"
        
        success, result, metadata = await manager.execute_with_reliability(mock_executor)
        
        assert success is True
        assert result == "Success with anthropic"
        assert metadata['failover_occurred'] is True
        assert metadata['attempts'] >= 2
    
    def test_provider_selection(self):
        """Test provider selection based on health"""
        providers = ['openai', 'anthropic', 'gemini']
        manager = ReliabilityManager(providers)
        
        # Make one provider unhealthy
        for _ in range(10):
            manager._record_failure('openai', 2000.0, "High latency")
        
        # Get available providers (should exclude unhealthy ones)
        available = manager.get_available_providers()
        assert 'openai' not in available
        assert len(available) >= 2
        
        # Select provider
        selected = manager.select_provider()
        assert selected in available


class TestLLMMonitoring:
    """Test suite for monitoring and observability"""
    
    def test_metrics_collection(self):
        """Test metrics collection and storage"""
        from src.cognition.llm_monitoring import LLMMetricsCollector, MetricType
        
        collector = LLMMetricsCollector()
        
        # Record some metrics
        collector.increment_counter('test_counter', 5.0, {'provider': 'openai'})
        collector.set_gauge('test_gauge', 42.0, {'status': 'healthy'})
        collector.record_histogram('test_histogram', 150.0, {'task': 'reasoning'})
        
        # Verify metrics exist
        assert 'test_counter' in collector.metrics
        assert 'test_gauge' in collector.metrics
        assert 'test_histogram' in collector.metrics
        
        # Check metric values
        counter_stats = collector.get_metric('test_counter').calculate_statistics()
        assert counter_stats.get('sum', 0) >= 5.0
    
    def test_alert_management(self):
        """Test alert creation and evaluation"""
        from src.cognition.llm_monitoring import LLMMetricsCollector, AlertManager, AlertSeverity
        
        collector = LLMMetricsCollector()
        alert_manager = AlertManager(collector)
        
        # Create test alert
        alert = alert_manager.create_alert(
            alert_id='test_alert',
            name='Test Alert',
            description='Test alert for high values',
            metric_name='test_metric',
            threshold_value=100.0,
            comparison_operator='>',
            severity=AlertSeverity.WARNING
        )
        
        assert alert.id == 'test_alert'
        assert alert.threshold_value == 100.0
        assert alert.severity == AlertSeverity.WARNING
    
    def test_performance_reporting(self):
        """Test performance report generation"""
        monitoring = LLMMonitoringSystem()
        
        # Simulate some requests
        request_id_1 = monitoring.start_request_tracking('req1', 'openai', 'conversational')
        monitoring.finish_request_tracking(
            request_id_1, success=True, response_length=150, 
            cost=0.05, tokens_used=100, quality_score=0.85
        )
        
        request_id_2 = monitoring.start_request_tracking('req2', 'anthropic', 'reasoning')
        monitoring.finish_request_tracking(
            request_id_2, success=True, response_length=200,
            cost=0.08, tokens_used=150, quality_score=0.90
        )
        
        # Generate report
        report = monitoring.get_performance_report(60)
        
        assert 'providers' in report
        assert len(report['providers']) == 2
        assert 'openai' in report['providers']
        assert 'anthropic' in report['providers']
        
        # Check provider metrics
        openai_metrics = report['providers']['openai']
        assert openai_metrics['success_rate'] == 1.0
        assert openai_metrics['avg_cost_per_request'] == 0.05
    
    def test_dashboard_data(self):
        """Test dashboard data compilation"""
        monitoring = LLMMonitoringSystem()
        
        dashboard_data = monitoring.get_dashboard_data()
        
        assert 'performance_report' in dashboard_data
        assert 'active_alerts' in dashboard_data
        assert 'recent_alert_history' in dashboard_data
        assert 'provider_comparison' in dashboard_data


@pytest.mark.integration
class TestProductionIntegration:
    """Integration tests for full production system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_request_flow(self):
        """Test complete request flow through all components"""
        config = {
            'default_provider': 'openai',
            'cost_optimization': {'optimization_strategy': 'balanced'},
            'reliability': {'failover_strategy': 'circuit_breaker'},
            'monitoring': {'metrics_retention_hours': 1},
            'performance': {'enable_caching': True, 'max_concurrent': 5}
        }
        
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            # Setup mock LLM manager
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['openai']
            
            mock_provider = Mock()
            mock_provider.estimate_tokens.return_value = 100
            mock_provider.generate.return_value = "Integration test response"
            mock_provider.get_name.return_value = "openai"
            mock_llm_manager.get_provider.return_value = mock_provider
            
            mock_llm_manager_class.return_value = mock_llm_manager
            
            # Create production manager
            manager = ProductionLLMManager(config)
            
            # Mock orchestrator for predictable response
            mock_result = OrchestrationResult(
                success=True,
                response="Integration test response",
                provider_used="openai",
                total_latency_ms=750,
                actual_cost=0.075,
                tokens_used=175,
                quality_score=0.88
            )
            
            manager.llm_orchestrator.orchestrate = AsyncMock(return_value=mock_result)
            
            try:
                # Execute request
                result = await manager.generate(
                    prompt="Explain machine learning concepts",
                    task_type=TaskType.ANALYTICAL,
                    routing_strategy=RoutingStrategy.BALANCED,
                    max_cost=0.10
                )
                
                # Verify successful execution
                assert result.success is True
                assert result.response == "Integration test response"
                assert result.provider_used == "openai"
                assert result.actual_cost == 0.075
                
                # Verify metrics were collected
                metrics = manager.get_performance_metrics()
                assert 'orchestrator_metrics' in metrics
                assert 'cost_analytics' in metrics
                assert 'reliability_status' in metrics
                
                # Verify health check
                health = await manager.health_check()
                assert health['overall_status'] in ['healthy', 'degraded']  # Degraded OK in test
                
            finally:
                await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_failure_recovery_scenarios(self):
        """Test system behavior under various failure scenarios"""
        config = {
            'reliability': {
                'failover_strategy': 'circuit_breaker',
                'max_retries': 2,
                'circuit_breaker_failure_threshold': 3
            }
        }
        
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['openai', 'anthropic']
            mock_llm_manager_class.return_value = mock_llm_manager
            
            manager = ProductionLLMManager(config)
            
            # Test scenario 1: Provider timeout with successful failover
            manager.llm_orchestrator.orchestrate = AsyncMock(return_value=OrchestrationResult(
                success=True,
                response="Failover success",
                provider_used="anthropic",
                fallback_used=True,
                attempts=2,
                total_latency_ms=1200,
                actual_cost=0.09,
                tokens_used=160
            ))
            
            result = await manager.generate("Test prompt")
            assert result.success is True
            assert result.fallback_used is True
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_cost_budget_enforcement(self):
        """Test cost budget enforcement and optimization"""
        config = {
            'cost_optimization': {
                'optimization_strategy': 'aggressive',
                'daily_budget': 1.0,  # Very low budget
                'weekly_budget': 5.0,
                'monthly_budget': 20.0
            }
        }
        
        with patch('src.cognition.enhanced_llm_manager.LLMManager') as mock_llm_manager_class:
            mock_llm_manager = Mock()
            mock_llm_manager.list_providers.return_value = ['gemini']  # Cheapest provider
            mock_llm_manager_class.return_value = mock_llm_manager
            
            manager = ProductionLLMManager(config)
            
            # Simulate high-cost request that should be rejected or optimized
            manager.llm_orchestrator.orchestrate = AsyncMock(return_value=OrchestrationResult(
                success=True,
                response="Budget-conscious response",
                provider_used="gemini",
                total_latency_ms=400,
                actual_cost=0.15,
                tokens_used=80
            ))
            
            result = await manager.generate(
                prompt="Generate a comprehensive analysis",
                routing_strategy=RoutingStrategy.COST_OPTIMIZED,
                max_cost=0.20
            )
            
            # Should succeed with cost-optimized provider
            assert result.success is True
            assert result.provider_used == "gemini"
            
            await manager.shutdown()


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-s", "--tb=short"])