#!/usr/bin/env python3
"""
Performance Monitoring Dashboard
=================================
Real-time performance tracking for Claude Code operations
"""

import json
import time
import psutil
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import deque
import statistics

@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: str
    operation: str
    response_time: float
    token_usage: int
    memory_usage: float
    cpu_usage: float
    cache_hit: bool = False
    error: bool = False
    
@dataclass
class PerformanceStats:
    """Aggregated performance statistics"""
    operation: str
    total_calls: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    total_tokens: int
    cache_hit_rate: float
    error_rate: float
    avg_memory: float
    avg_cpu: float
    
class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self, max_history: int = 1000):
        self.metrics_history = deque(maxlen=max_history)
        self.alerts = []
        self.start_time = time.time()
        self.metrics_file = Path(".claude/metrics.jsonl")
        self.alerts_config = {
            "slow_response": 5.0,  # seconds
            "high_token_usage": 10000,
            "low_cache_hit": 0.5,
            "high_error_rate": 0.05,
            "high_memory": 80.0,  # percent
            "high_cpu": 80.0  # percent
        }
        
    def record_metric(self, 
                     operation: str,
                     response_time: float,
                     token_usage: int,
                     cache_hit: bool = False,
                     error: bool = False):
        """Record a performance metric"""
        metric = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            response_time=response_time,
            token_usage=token_usage,
            memory_usage=psutil.virtual_memory().percent,
            cpu_usage=psutil.cpu_percent(interval=0.1),
            cache_hit=cache_hit,
            error=error
        )
        
        self.metrics_history.append(metric)
        
        # Check for alerts
        self._check_alerts(metric)
        
        # Persist to file
        self._persist_metric(metric)
        
        return metric
        
    def _check_alerts(self, metric: PerformanceMetrics):
        """Check if metric triggers any alerts"""
        alerts = []
        
        if metric.response_time > self.alerts_config["slow_response"]:
            alerts.append(f"SLOW_RESPONSE: {metric.operation} took {metric.response_time:.2f}s")
            
        if metric.token_usage > self.alerts_config["high_token_usage"]:
            alerts.append(f"HIGH_TOKEN_USAGE: {metric.operation} used {metric.token_usage} tokens")
            
        if metric.memory_usage > self.alerts_config["high_memory"]:
            alerts.append(f"HIGH_MEMORY: Memory usage at {metric.memory_usage:.1f}%")
            
        if metric.cpu_usage > self.alerts_config["high_cpu"]:
            alerts.append(f"HIGH_CPU: CPU usage at {metric.cpu_usage:.1f}%")
            
        for alert in alerts:
            self.alerts.append({
                "timestamp": metric.timestamp,
                "alert": alert,
                "metric": asdict(metric)
            })
            print(f"[ALERT] {alert}")
            
    def _persist_metric(self, metric: PerformanceMetrics):
        """Save metric to file"""
        self.metrics_file.parent.mkdir(exist_ok=True)
        with open(self.metrics_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(metric)) + '\n')
            
    def get_stats(self, operation: Optional[str] = None, 
                  time_window: Optional[int] = None) -> List[PerformanceStats]:
        """Get aggregated statistics"""
        metrics = list(self.metrics_history)
        
        # Filter by time window (minutes)
        if time_window:
            cutoff = datetime.now() - timedelta(minutes=time_window)
            metrics = [m for m in metrics 
                      if datetime.fromisoformat(m.timestamp) > cutoff]
            
        # Group by operation
        operations = {}
        for metric in metrics:
            if operation and metric.operation != operation:
                continue
                
            if metric.operation not in operations:
                operations[metric.operation] = []
            operations[metric.operation].append(metric)
            
        # Calculate stats
        stats = []
        for op_name, op_metrics in operations.items():
            if not op_metrics:
                continue
                
            response_times = [m.response_time for m in op_metrics]
            response_times.sort()
            
            stat = PerformanceStats(
                operation=op_name,
                total_calls=len(op_metrics),
                avg_response_time=statistics.mean(response_times),
                p95_response_time=response_times[int(len(response_times) * 0.95)] if response_times else 0,
                p99_response_time=response_times[int(len(response_times) * 0.99)] if response_times else 0,
                total_tokens=sum(m.token_usage for m in op_metrics),
                cache_hit_rate=sum(1 for m in op_metrics if m.cache_hit) / len(op_metrics),
                error_rate=sum(1 for m in op_metrics if m.error) / len(op_metrics),
                avg_memory=statistics.mean([m.memory_usage for m in op_metrics]),
                avg_cpu=statistics.mean([m.cpu_usage for m in op_metrics])
            )
            stats.append(stat)
            
        return stats
        
    def print_dashboard(self):
        """Print performance dashboard"""
        print("\n" + "=" * 80)
        print(" " * 25 + "PERFORMANCE DASHBOARD")
        print("=" * 80)
        
        uptime = time.time() - self.start_time
        print(f"\nUptime: {timedelta(seconds=int(uptime))}")
        print(f"Total Operations: {len(self.metrics_history)}")
        print(f"Active Alerts: {len(self.alerts)}")
        
        # Recent performance (last 10 minutes)
        print("\n[LAST 10 MINUTES]")
        print("-" * 80)
        recent_stats = self.get_stats(time_window=10)
        
        if recent_stats:
            print(f"{'Operation':<30} {'Calls':>8} {'Avg RT':>10} {'P95 RT':>10} {'Tokens':>10} {'Cache%':>8} {'Error%':>8}")
            print("-" * 80)
            
            for stat in recent_stats:
                print(f"{stat.operation:<30} {stat.total_calls:>8} "
                      f"{stat.avg_response_time:>9.2f}s {stat.p95_response_time:>9.2f}s "
                      f"{stat.total_tokens:>10} {stat.cache_hit_rate:>7.1%} {stat.error_rate:>7.1%}")
                      
        # System resources
        print("\n[SYSTEM RESOURCES]")
        print("-" * 80)
        mem = psutil.virtual_memory()
        print(f"Memory: {mem.percent:.1f}% used ({mem.used / 1024**3:.1f}GB / {mem.total / 1024**3:.1f}GB)")
        print(f"CPU: {psutil.cpu_percent(interval=1):.1f}% (cores: {psutil.cpu_count()})")
        
        # Recent alerts
        if self.alerts:
            print("\n[RECENT ALERTS]")
            print("-" * 80)
            for alert in self.alerts[-5:]:
                print(f"{alert['timestamp']}: {alert['alert']}")
                
        print("=" * 80)
        
    def export_report(self, output_path: Optional[Path] = None) -> Path:
        """Export detailed performance report"""
        if not output_path:
            output_path = Path(f".claude/reports/performance_{datetime.now():%Y%m%d_%H%M%S}.json")
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "total_operations": len(self.metrics_history),
            "statistics": {
                "all_time": [asdict(s) for s in self.get_stats()],
                "last_hour": [asdict(s) for s in self.get_stats(time_window=60)],
                "last_10min": [asdict(s) for s in self.get_stats(time_window=10)]
            },
            "alerts": self.alerts,
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / 1024**3,
                "python_version": sys.version
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        return output_path
        
class PerformanceOptimizer:
    """AI-driven performance optimization suggestions"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        
    def analyze_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        stats = self.monitor.get_stats()
        
        for stat in stats:
            issues = []
            
            # Slow operations
            if stat.avg_response_time > 3.0:
                issues.append({
                    "type": "slow_operation",
                    "severity": "high" if stat.avg_response_time > 5.0 else "medium",
                    "suggestion": "Consider caching or optimizing algorithm"
                })
                
            # High token usage
            avg_tokens = stat.total_tokens / stat.total_calls if stat.total_calls > 0 else 0
            if avg_tokens > 5000:
                issues.append({
                    "type": "high_token_usage",
                    "severity": "medium",
                    "suggestion": "Optimize prompts or use context compression"
                })
                
            # Low cache hit rate
            if stat.cache_hit_rate < 0.3 and stat.total_calls > 10:
                issues.append({
                    "type": "low_cache_utilization",
                    "severity": "low",
                    "suggestion": "Implement better caching strategy"
                })
                
            # High error rate
            if stat.error_rate > 0.1:
                issues.append({
                    "type": "high_error_rate",
                    "severity": "critical",
                    "suggestion": "Debug and fix error causes"
                })
                
            if issues:
                bottlenecks.append({
                    "operation": stat.operation,
                    "issues": issues,
                    "stats": asdict(stat)
                })
                
        return bottlenecks
        
    def suggest_optimizations(self) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        bottlenecks = self.analyze_bottlenecks()
        
        # Analyze patterns
        high_severity_count = sum(1 for b in bottlenecks 
                                 for i in b["issues"] 
                                 if i["severity"] in ["high", "critical"])
                                 
        if high_severity_count > 0:
            suggestions.append(f"URGENT: Fix {high_severity_count} high/critical severity issues")
            
        # Check cache effectiveness
        stats = self.monitor.get_stats()
        if stats:
            overall_cache_rate = sum(s.cache_hit_rate * s.total_calls for s in stats) / sum(s.total_calls for s in stats)
            if overall_cache_rate < 0.5:
                suggestions.append("Improve caching: Current hit rate is below 50%")
                
        # Memory optimization
        recent_metrics = list(self.monitor.metrics_history)[-100:]
        if recent_metrics:
            avg_memory = statistics.mean([m.memory_usage for m in recent_metrics])
            if avg_memory > 70:
                suggestions.append(f"Memory pressure detected: Average usage {avg_memory:.1f}%")
                
        return suggestions
        
# Global monitor instance
_monitor = None

def get_monitor() -> PerformanceMonitor:
    """Get or create global monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor
    
def monitor_operation(operation: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            monitor = get_monitor()
            start_time = time.time()
            error = False
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise
            finally:
                response_time = time.time() - start_time
                # Estimate token usage (would need actual integration)
                token_usage = int(response_time * 1000)  # Placeholder
                monitor.record_metric(
                    operation=operation,
                    response_time=response_time,
                    token_usage=token_usage,
                    error=error
                )
                
        def sync_wrapper(*args, **kwargs):
            monitor = get_monitor()
            start_time = time.time()
            error = False
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise
            finally:
                response_time = time.time() - start_time
                token_usage = int(response_time * 1000)  # Placeholder
                monitor.record_metric(
                    operation=operation,
                    response_time=response_time,
                    token_usage=token_usage,
                    error=error
                )
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
    
def main():
    """Main entry point for performance monitoring"""
    import sys
    import os
    from pathlib import Path
    
    # Ensure proper working directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    monitor = get_monitor()
    optimizer = PerformanceOptimizer(monitor)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "dashboard":
            monitor.print_dashboard()
            
        elif command == "analyze":
            bottlenecks = optimizer.analyze_bottlenecks()
            print("\n[PERFORMANCE BOTTLENECKS]")
            print("=" * 80)
            for b in bottlenecks:
                print(f"\nOperation: {b['operation']}")
                for issue in b["issues"]:
                    print(f"  [{issue['severity'].upper()}] {issue['type']}")
                    print(f"    Suggestion: {issue['suggestion']}")
                    
        elif command == "optimize":
            suggestions = optimizer.suggest_optimizations()
            print("\n[OPTIMIZATION SUGGESTIONS]")
            print("=" * 80)
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. {suggestion}")
                
        elif command == "export":
            output_path = monitor.export_report()
            print(f"[SUCCESS] Report exported to: {output_path}")
            
    else:
        # Default: show dashboard
        monitor.print_dashboard()
        
if __name__ == "__main__":
    main()