"""
Advanced Code Analyzer for Nexus Executor
Provides comprehensive code analysis, optimization suggestions, and quality metrics
"""

import ast
import dis
import inspect
import io
import json
import re
import tokenize
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import logging

from .models import (
    CodeArtifact, CodeLanguage, CodeAnalysis, 
    OptimizationSuggestion, TestCase
)

logger = logging.getLogger(__name__)


# ============================================================================
# COMPLEXITY METRICS
# ============================================================================

class ComplexityCalculator:
    """Calculate various complexity metrics for code"""
    
    @staticmethod
    def calculate_cyclomatic_complexity(tree: ast.AST) -> int:
        """Calculate McCabe cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Decision points increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # Each and/or adds complexity
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Assert):
                complexity += 1
            elif isinstance(node, ast.comprehension):
                complexity += sum(1 for _ in node.ifs)
        
        return complexity
    
    @staticmethod
    def calculate_cognitive_complexity(tree: ast.AST) -> int:
        """Calculate cognitive complexity (how hard to understand)"""
        
        class CognitiveVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                self.nesting_level = 0
            
            def visit_If(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
            
            def visit_While(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
            
            def visit_For(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
            
            def visit_ExceptHandler(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
            
            def visit_BoolOp(self, node):
                self.complexity += len(node.values) - 1
                self.generic_visit(node)
            
            def visit_Lambda(self, node):
                self.complexity += 1
                self.generic_visit(node)
        
        visitor = CognitiveVisitor()
        visitor.visit(tree)
        return visitor.complexity
    
    @staticmethod
    def calculate_halstead_metrics(tree: ast.AST) -> Dict[str, float]:
        """Calculate Halstead complexity metrics"""
        operators = []
        operands = []
        
        for node in ast.walk(tree):
            # Operators
            if isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
                                ast.Pow, ast.LShift, ast.RShift, ast.BitOr,
                                ast.BitXor, ast.BitAnd, ast.FloorDiv)):
                operators.append(type(node).__name__)
            elif isinstance(node, (ast.And, ast.Or, ast.Not)):
                operators.append(type(node).__name__)
            elif isinstance(node, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
                                  ast.Is, ast.IsNot, ast.In, ast.NotIn)):
                operators.append(type(node).__name__)
            
            # Operands
            elif isinstance(node, ast.Name):
                operands.append(node.id)
            elif isinstance(node, (ast.Constant, ast.Num, ast.Str)):
                operands.append(str(getattr(node, 'value', node.n if hasattr(node, 'n') else node.s)))
        
        n1 = len(set(operators))  # Unique operators
        n2 = len(set(operands))   # Unique operands
        N1 = len(operators)       # Total operators
        N2 = len(operands)        # Total operands
        
        # Halstead metrics
        n = n1 + n2  # Vocabulary
        N = N1 + N2  # Length
        
        if n1 > 0 and n2 > 0 and N > 0:
            volume = N * (n.bit_length() if n > 0 else 0)
            difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
            effort = volume * difficulty
            time = effort / 18  # Seconds to understand
            bugs = volume / 3000  # Estimated bugs
        else:
            volume = difficulty = effort = time = bugs = 0
        
        return {
            'vocabulary': n,
            'length': N,
            'volume': volume,
            'difficulty': difficulty,
            'effort': effort,
            'time_to_understand': time,
            'estimated_bugs': bugs
        }


# ============================================================================
# PATTERN DETECTOR
# ============================================================================

class PatternDetector:
    """Detect code patterns, anti-patterns, and code smells"""
    
    # Common anti-patterns
    ANTI_PATTERNS = {
        'god_function': 'Function with too many lines (>50)',
        'long_parameter_list': 'Function with too many parameters (>5)',
        'deep_nesting': 'Code nested too deeply (>4 levels)',
        'duplicate_code': 'Duplicated code blocks',
        'magic_numbers': 'Hard-coded numeric values',
        'global_state': 'Use of global variables',
        'empty_except': 'Empty exception handlers',
        'broad_except': 'Catching Exception or bare except',
        'mutable_default': 'Mutable default arguments',
    }
    
    @classmethod
    def detect_patterns(cls, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Detect patterns and anti-patterns in code"""
        issues = []
        
        # Check each function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                issues.extend(cls._check_function(node))
            elif isinstance(node, ast.ExceptHandler):
                issues.extend(cls._check_exception_handler(node))
            elif isinstance(node, (ast.Constant, ast.Num)):
                issues.extend(cls._check_magic_numbers(node))
        
        # Check for duplicate code
        issues.extend(cls._check_duplicates(code))
        
        return issues
    
    @classmethod
    def _check_function(cls, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Check function for anti-patterns"""
        issues = []
        
        # Check function length
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            lines = node.end_lineno - node.lineno
            if lines > 50:
                issues.append({
                    'type': 'god_function',
                    'line': node.lineno,
                    'description': f'Function {node.name} has {lines} lines (>50)',
                    'severity': 'medium'
                })
        
        # Check parameter count
        param_count = len(node.args.args) + len(node.args.kwonlyargs)
        if param_count > 5:
            issues.append({
                'type': 'long_parameter_list',
                'line': node.lineno,
                'description': f'Function {node.name} has {param_count} parameters (>5)',
                'severity': 'low'
            })
        
        # Check for mutable defaults
        for default in node.args.defaults + node.args.kw_defaults:
            if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                issues.append({
                    'type': 'mutable_default',
                    'line': node.lineno,
                    'description': f'Function {node.name} has mutable default argument',
                    'severity': 'high'
                })
        
        # Check nesting depth
        max_depth = cls._calculate_nesting_depth(node)
        if max_depth > 4:
            issues.append({
                'type': 'deep_nesting',
                'line': node.lineno,
                'description': f'Function {node.name} has nesting depth of {max_depth} (>4)',
                'severity': 'medium'
            })
        
        return issues
    
    @classmethod
    def _check_exception_handler(cls, node: ast.ExceptHandler) -> List[Dict[str, Any]]:
        """Check exception handling patterns"""
        issues = []
        
        # Check for empty except
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            issues.append({
                'type': 'empty_except',
                'line': node.lineno,
                'description': 'Empty exception handler',
                'severity': 'high'
            })
        
        # Check for broad except
        if node.type:
            if isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                issues.append({
                    'type': 'broad_except',
                    'line': node.lineno,
                    'description': 'Catching broad Exception',
                    'severity': 'medium'
                })
        elif not node.type:
            issues.append({
                'type': 'broad_except',
                'line': node.lineno,
                'description': 'Bare except clause',
                'severity': 'high'
            })
        
        return issues
    
    @classmethod
    def _check_magic_numbers(cls, node: Union[ast.Constant, ast.Num]) -> List[Dict[str, Any]]:
        """Check for magic numbers"""
        issues = []
        
        value = getattr(node, 'value', getattr(node, 'n', None))
        if isinstance(value, (int, float)) and value not in (0, 1, -1, 2, 10, 100):
            issues.append({
                'type': 'magic_numbers',
                'line': getattr(node, 'lineno', 0),
                'description': f'Magic number {value} should be a named constant',
                'severity': 'low'
            })
        
        return issues
    
    @classmethod
    def _check_duplicates(cls, code: str) -> List[Dict[str, Any]]:
        """Check for duplicate code blocks"""
        issues = []
        lines = code.splitlines()
        
        # Simple duplicate detection (check for identical consecutive lines)
        duplicates = defaultdict(list)
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                duplicates[stripped].append(i + 1)
        
        for line_text, occurrences in duplicates.items():
            if len(occurrences) > 2:
                issues.append({
                    'type': 'duplicate_code',
                    'lines': occurrences,
                    'description': f'Line "{line_text[:50]}..." appears {len(occurrences)} times',
                    'severity': 'low'
                })
        
        return issues
    
    @classmethod
    def _calculate_nesting_depth(cls, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = cls._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = cls._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth


# ============================================================================
# DEPENDENCY ANALYZER
# ============================================================================

class DependencyAnalyzer:
    """Analyze code dependencies and imports"""
    
    @staticmethod
    def analyze_imports(tree: ast.AST) -> Dict[str, Any]:
        """Analyze import statements"""
        imports = {
            'standard': [],
            'third_party': [],
            'local': [],
            'all_modules': set(),
            'from_imports': defaultdict(list)
        }
        
        standard_libs = {
            'os', 'sys', 're', 'json', 'math', 'random', 'datetime',
            'collections', 'itertools', 'functools', 'pathlib', 'typing',
            'asyncio', 'threading', 'multiprocessing', 'subprocess',
            'urllib', 'http', 'socket', 'sqlite3', 'csv', 'io'
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    imports['all_modules'].add(module)
                    
                    if module in standard_libs:
                        imports['standard'].append(module)
                    elif module.startswith('.'):
                        imports['local'].append(module)
                    else:
                        imports['third_party'].append(module)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                base_module = module.split('.')[0]
                imports['all_modules'].add(base_module)
                
                for alias in node.names:
                    imports['from_imports'][module].append(alias.name)
                
                if base_module in standard_libs:
                    imports['standard'].append(base_module)
                elif module.startswith('.') or node.level > 0:
                    imports['local'].append(module)
                else:
                    imports['third_party'].append(base_module)
        
        # Convert set to list for JSON serialization
        imports['all_modules'] = list(imports['all_modules'])
        
        return imports
    
    @staticmethod
    def build_dependency_graph(tree: ast.AST) -> Dict[str, List[str]]:
        """Build function/class dependency graph"""
        graph = defaultdict(list)
        current_scope = []
        
        class DependencyVisitor(ast.NodeVisitor):
            def __init__(self, graph, scope):
                self.graph = graph
                self.scope = scope
            
            def visit_FunctionDef(self, node):
                func_name = '.'.join(self.scope + [node.name])
                
                # Find function calls within this function
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            self.graph[func_name].append(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            self.graph[func_name].append(child.func.attr)
                
                self.scope.append(node.name)
                self.generic_visit(node)
                self.scope.pop()
            
            def visit_ClassDef(self, node):
                self.scope.append(node.name)
                self.generic_visit(node)
                self.scope.pop()
        
        visitor = DependencyVisitor(graph, current_scope)
        visitor.visit(tree)
        
        return dict(graph)


# ============================================================================
# OPTIMIZATION SUGGESTER
# ============================================================================

class OptimizationSuggester:
    """Suggest code optimizations"""
    
    @staticmethod
    def suggest_optimizations(tree: ast.AST, code: str) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions"""
        suggestions = []
        
        for node in ast.walk(tree):
            # Suggest list comprehensions
            if isinstance(node, ast.For):
                suggestion = OptimizationSuggester._check_for_comprehension(node, code)
                if suggestion:
                    suggestions.append(suggestion)
            
            # Suggest using enumerate
            elif isinstance(node, ast.For):
                suggestion = OptimizationSuggester._check_for_enumerate(node, code)
                if suggestion:
                    suggestions.append(suggestion)
            
            # Suggest using sets for membership testing
            elif isinstance(node, ast.In):
                suggestion = OptimizationSuggester._check_for_set_usage(node, code)
                if suggestion:
                    suggestions.append(suggestion)
        
        # Check for performance patterns
        suggestions.extend(OptimizationSuggester._check_performance_patterns(code))
        
        return suggestions
    
    @staticmethod
    def _check_for_comprehension(node: ast.For, code: str) -> Optional[OptimizationSuggestion]:
        """Check if for loop can be list comprehension"""
        # Simple check: for loop with single append
        if len(node.body) == 1 and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Call):
                call = node.body[0].value
                if isinstance(call.func, ast.Attribute) and call.func.attr == 'append':
                    return OptimizationSuggestion(
                        type='performance',
                        severity='low',
                        line_range=(node.lineno, getattr(node, 'end_lineno', node.lineno)),
                        description='This loop could be a list comprehension',
                        estimated_improvement=0.2
                    )
        return None
    
    @staticmethod
    def _check_for_enumerate(node: ast.For, code: str) -> Optional[OptimizationSuggestion]:
        """Check if enumerate should be used"""
        # This would need more sophisticated analysis
        return None
    
    @staticmethod
    def _check_for_set_usage(node: ast.In, code: str) -> Optional[OptimizationSuggestion]:
        """Check if set should be used instead of list"""
        # This would need more sophisticated analysis
        return None
    
    @staticmethod
    def _check_performance_patterns(code: str) -> List[OptimizationSuggestion]:
        """Check for common performance anti-patterns"""
        suggestions = []
        
        # Check for string concatenation in loops
        if 'for ' in code and '+=' in code and ('str(' in code or '"' in code or "'" in code):
            suggestions.append(OptimizationSuggestion(
                type='performance',
                severity='medium',
                line_range=(0, 0),
                description='String concatenation in loop detected. Consider using join() or list',
                estimated_improvement=0.5
            ))
        
        return suggestions


# ============================================================================
# MAIN ANALYZER
# ============================================================================

class NexusCodeAnalyzer:
    """Main code analyzer combining all analysis features"""
    
    def __init__(self):
        self.complexity_calc = ComplexityCalculator()
        self.pattern_detector = PatternDetector()
        self.dependency_analyzer = DependencyAnalyzer()
        self.optimization_suggester = OptimizationSuggester()
    
    def analyze(self, artifact: CodeArtifact) -> CodeAnalysis:
        """Perform comprehensive code analysis"""
        
        # Only analyze Python for now
        if artifact.language != CodeLanguage.PYTHON:
            return self._basic_analysis(artifact)
        
        try:
            # Parse AST
            tree = ast.parse(artifact.content)
            
            # Calculate complexity
            complexity = {
                'cyclomatic': self.complexity_calc.calculate_cyclomatic_complexity(tree),
                'cognitive': self.complexity_calc.calculate_cognitive_complexity(tree),
                **self.complexity_calc.calculate_halstead_metrics(tree)
            }
            
            # Analyze imports
            import_analysis = self.dependency_analyzer.analyze_imports(tree)
            
            # Build dependency graph
            dep_graph = self.dependency_analyzer.build_dependency_graph(tree)
            
            # Detect patterns and issues
            issues = self.pattern_detector.detect_patterns(tree, artifact.content)
            
            # Get optimization suggestions
            optimizations = self.optimization_suggester.suggest_optimizations(tree, artifact.content)
            
            # Extract functions and classes
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            # Count lines
            lines = artifact.content.splitlines()
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            
            # Create analysis result
            return CodeAnalysis(
                artifact_id=artifact.id,
                language=artifact.language,
                lines_of_code=code_lines,
                complexity=complexity,
                imports=import_analysis['all_modules'],
                functions=functions,
                classes=classes,
                potential_issues=issues,
                security_risks=[],  # Would be filled by security analyzer
                performance_hints=[opt.description for opt in optimizations],
                dependencies_graph=dep_graph
            )
            
        except SyntaxError as e:
            return CodeAnalysis(
                artifact_id=artifact.id,
                language=artifact.language,
                lines_of_code=len(artifact.content.splitlines()),
                complexity={'error': 'Syntax error in code'},
                imports=[],
                functions=[],
                classes=[],
                potential_issues=[{
                    'type': 'syntax_error',
                    'description': str(e),
                    'severity': 'critical'
                }],
                security_risks=[],
                performance_hints=[]
            )
    
    def _basic_analysis(self, artifact: CodeArtifact) -> CodeAnalysis:
        """Basic analysis for non-Python languages"""
        lines = artifact.content.splitlines()
        return CodeAnalysis(
            artifact_id=artifact.id,
            language=artifact.language,
            lines_of_code=len(lines),
            complexity={'basic': len(lines)},
            imports=[],
            functions=[],
            classes=[],
            potential_issues=[],
            security_risks=[],
            performance_hints=[]
        )
    
    def generate_test_suggestions(self, analysis: CodeAnalysis) -> List[TestCase]:
        """Generate test case suggestions based on analysis"""
        test_cases = []
        
        # Generate tests for each function
        for func_name in analysis.functions:
            test_cases.append(TestCase(
                name=f"test_{func_name}",
                description=f"Test for function {func_name}",
                input_data={},
                expected_output=None,
                test_type='unit',
                code=f"""def test_{func_name}():
    # TODO: Implement test for {func_name}
    assert True
""",
                coverage_target=func_name
            ))
        
        return test_cases