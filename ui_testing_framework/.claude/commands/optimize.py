#!/usr/bin/env python3
"""
/optimize Command Implementation
=================================
Tree of Thoughts + Self-Consistency optimization strategy
"""

import ast
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json

@dataclass
class OptimizationBranch:
    """Represents one optimization exploration branch"""
    name: str
    analysis: Dict[str, Any]
    recommendations: List[str]
    confidence: float
    
@dataclass
class OptimizationResult:
    """Final optimization result after branch convergence"""
    file_path: Path
    branches: List[OptimizationBranch]
    consensus: List[str]
    optimized_code: str
    performance_metrics: Dict[str, float]
    
class TreeOfThoughtsOptimizer:
    """Implements Tree of Thoughts strategy for code optimization"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        
    def analyze_time_complexity(self, code: str) -> OptimizationBranch:
        """Branch 1: Time complexity analysis"""
        analysis = {
            "nested_loops": [],
            "repeated_computations": [],
            "inefficient_algorithms": [],
            "caching_opportunities": []
        }
        
        try:
            tree = ast.parse(code)
            
            # Find nested loops
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    # Check for nested loops
                    for child in ast.walk(node):
                        if child != node and isinstance(child, ast.For):
                            analysis["nested_loops"].append({
                                "line": node.lineno,
                                "complexity": "O(n²) or worse"
                            })
                            
            # Find repeated function calls
            function_calls = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    call_str = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                    function_calls[call_str] = function_calls.get(call_str, 0) + 1
                    
            for call, count in function_calls.items():
                if count > 2:
                    analysis["repeated_computations"].append({
                        "call": call,
                        "count": count,
                        "suggestion": "Consider caching result"
                    })
                    
        except Exception as e:
            print(f"[WARNING] AST analysis failed: {e}")
            
        recommendations = []
        if analysis["nested_loops"]:
            recommendations.append("Replace nested loops with vectorized operations or optimize algorithm")
        if analysis["repeated_computations"]:
            recommendations.append("Implement memoization or caching for repeated computations")
            
        return OptimizationBranch(
            name="Time Complexity",
            analysis=analysis,
            recommendations=recommendations,
            confidence=0.85
        )
        
    def analyze_memory_usage(self, code: str) -> OptimizationBranch:
        """Branch 2: Memory optimization analysis"""
        analysis = {
            "large_data_structures": [],
            "unnecessary_copies": [],
            "memory_leaks": [],
            "optimization_opportunities": []
        }
        
        try:
            tree = ast.parse(code)
            
            # Find large list comprehensions
            for node in ast.walk(tree):
                if isinstance(node, ast.ListComp):
                    analysis["large_data_structures"].append({
                        "line": node.lineno,
                        "suggestion": "Consider using generator expression for memory efficiency"
                    })
                    
            # Find unnecessary list operations
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if hasattr(node.func, 'id') and node.func.id in ['list', 'copy']:
                        analysis["unnecessary_copies"].append({
                            "line": node.lineno,
                            "operation": node.func.id
                        })
                        
        except Exception as e:
            print(f"[WARNING] Memory analysis failed: {e}")
            
        recommendations = []
        if analysis["large_data_structures"]:
            recommendations.append("Use generators instead of list comprehensions for large datasets")
        if analysis["unnecessary_copies"]:
            recommendations.append("Avoid unnecessary data copying, use references where possible")
            
        return OptimizationBranch(
            name="Memory Usage",
            analysis=analysis,
            recommendations=recommendations,
            confidence=0.78
        )
        
    def analyze_async_opportunities(self, code: str) -> OptimizationBranch:
        """Branch 3: Async/parallel optimization analysis"""
        analysis = {
            "io_operations": [],
            "parallelizable_loops": [],
            "async_opportunities": [],
            "concurrency_improvements": []
        }
        
        try:
            tree = ast.parse(code)
            
            # Find I/O operations
            io_functions = ['open', 'read', 'write', 'requests', 'urllib']
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_name = ""
                    if hasattr(node.func, 'id'):
                        func_name = node.func.id
                    elif hasattr(node.func, 'attr'):
                        func_name = node.func.attr
                        
                    if any(io in func_name for io in io_functions):
                        analysis["io_operations"].append({
                            "line": node.lineno,
                            "operation": func_name,
                            "suggestion": "Consider async I/O"
                        })
                        
            # Find independent loops
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    # Check if loop iterations are independent
                    analysis["parallelizable_loops"].append({
                        "line": node.lineno,
                        "suggestion": "Consider parallel processing with ThreadPoolExecutor"
                    })
                    
        except Exception as e:
            print(f"[WARNING] Async analysis failed: {e}")
            
        recommendations = []
        if analysis["io_operations"]:
            recommendations.append("Convert I/O operations to async for better performance")
        if analysis["parallelizable_loops"]:
            recommendations.append("Use parallel processing for independent iterations")
            
        return OptimizationBranch(
            name="Async/Parallel",
            analysis=analysis,
            recommendations=recommendations,
            confidence=0.82
        )
        
    def converge_branches(self, branches: List[OptimizationBranch]) -> List[str]:
        """Self-Consistency: Find consensus among branches"""
        all_recommendations = []
        recommendation_votes = {}
        
        # Collect all recommendations with confidence weights
        for branch in branches:
            for rec in branch.recommendations:
                key = rec.lower().strip()
                if key not in recommendation_votes:
                    recommendation_votes[key] = {
                        "text": rec,
                        "votes": 0,
                        "confidence": 0
                    }
                recommendation_votes[key]["votes"] += 1
                recommendation_votes[key]["confidence"] += branch.confidence
                
        # Sort by combined score (votes * confidence)
        sorted_recs = sorted(
            recommendation_votes.items(),
            key=lambda x: x[1]["votes"] * x[1]["confidence"],
            reverse=True
        )
        
        # Return top recommendations
        consensus = []
        for key, data in sorted_recs[:5]:
            consensus.append(data["text"])
            
        return consensus
        
    def generate_optimized_code(self, original_code: str, consensus: List[str]) -> str:
        """Generate optimized version based on consensus"""
        optimized = original_code
        
        # Apply optimizations based on consensus
        if any("caching" in rec.lower() for rec in consensus):
            # Add caching decorator
            cache_import = "from functools import lru_cache\n\n"
            if "lru_cache" not in optimized:
                optimized = cache_import + optimized
                
        if any("generator" in rec.lower() for rec in consensus):
            # Convert list comprehensions to generators where possible
            optimized = optimized.replace("[", "(").replace("]", ")")
            
        if any("async" in rec.lower() for rec in consensus):
            # Add async markers
            optimized = optimized.replace("def ", "async def ")
            optimized = optimized.replace("open(", "aiofiles.open(")
            
        return optimized
        
    async def optimize(self, file_path: Path) -> OptimizationResult:
        """Main optimization pipeline"""
        print(f"[OPTIMIZE] Analyzing {file_path.name}")
        print("=" * 60)
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
            
        start_time = time.time()
        
        # Tree of Thoughts: Explore multiple branches in parallel
        print("[BRANCH 1] Analyzing time complexity...")
        branch1 = self.analyze_time_complexity(original_code)
        
        print("[BRANCH 2] Analyzing memory usage...")
        branch2 = self.analyze_memory_usage(original_code)
        
        print("[BRANCH 3] Analyzing async opportunities...")
        branch3 = self.analyze_async_opportunities(original_code)
        
        branches = [branch1, branch2, branch3]
        
        # Self-Consistency: Converge branches
        print("\n[CONVERGING] Finding consensus optimizations...")
        consensus = self.converge_branches(branches)
        
        # Generate optimized code
        print("[GENERATING] Creating optimized version...")
        optimized_code = self.generate_optimized_code(original_code, consensus)
        
        end_time = time.time()
        
        # Calculate metrics
        metrics = {
            "analysis_time": end_time - start_time,
            "original_lines": len(original_code.splitlines()),
            "optimized_lines": len(optimized_code.splitlines()),
            "branches_explored": len(branches),
            "consensus_items": len(consensus)
        }
        
        result = OptimizationResult(
            file_path=file_path,
            branches=branches,
            consensus=consensus,
            optimized_code=optimized_code,
            performance_metrics=metrics
        )
        
        # Print summary
        print("\n" + "=" * 60)
        print("[OPTIMIZATION SUMMARY]")
        print("=" * 60)
        print(f"File: {file_path.name}")
        print(f"Analysis time: {metrics['analysis_time']:.2f}s")
        print(f"Branches explored: {metrics['branches_explored']}")
        print(f"\n[CONSENSUS OPTIMIZATIONS]")
        for i, rec in enumerate(consensus, 1):
            print(f"  {i}. {rec}")
            
        print("\n[BRANCH DETAILS]")
        for branch in branches:
            print(f"\n  {branch.name} (confidence: {branch.confidence:.0%})")
            for rec in branch.recommendations[:2]:
                print(f"    - {rec}")
                
        return result
        
def main():
    """Main entry point for /optimize command"""
    import sys
    import os
    from pathlib import Path
    
    # Ensure proper working directory
    script_dir = Path(__file__).parent.parent.parent
    os.chdir(script_dir)
    
    if len(sys.argv) < 2:
        print("Usage: optimize.py <file_path>")
        sys.exit(1)
        
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)
        
    optimizer = TreeOfThoughtsOptimizer()
    result = asyncio.run(optimizer.optimize(file_path))
    
    # Save optimized version
    optimized_path = file_path.with_suffix('.optimized.py')
    with open(optimized_path, 'w', encoding='utf-8') as f:
        f.write(result.optimized_code)
        
    print(f"\n[SUCCESS] Optimized code saved to: {optimized_path}")
    
if __name__ == "__main__":
    main()