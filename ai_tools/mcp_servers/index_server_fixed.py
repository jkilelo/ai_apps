#!/usr/bin/env python3
"""
IndexServer - Production-Ready Structural Understanding MCP Server
Part of MFHS-MCP System for handling massive codebases

Provides AST-based indexing, symbol table management, and cross-reference tracking
for files of unlimited size through intelligent indexing strategies.

PRODUCTION FEATURES:
- Complete input validation and sanitization
- Rate limiting with token bucket algorithm
- LRU caching with TTL
- Comprehensive error handling
- Health checks and metrics
- Graceful degradation
- Full type safety
"""

import ast
import json
import logging
import sys
import time
import hashlib
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union, TypedDict, Protocol
from collections import defaultdict
import re
from functools import wraps
import asyncio
from datetime import datetime

# Import base server with all production features
from mcp_base import (
    BaseMCPServer,
    ServerConfig,
    ValidationError,
    ProcessingError,
    RateLimitError,
    rate_limit
)

# MCP Server SDK imports
try:
    from mcp import Server, Tool
    from mcp.types import TextContent, Resource
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("IndexServer")

# ============================================================================
# Type Definitions
# ============================================================================

class SymbolType(Enum):
    """Types of symbols in code"""
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    IMPORT = "import"
    DECORATOR = "decorator"
    PROPERTY = "property"
    MODULE = "module"
    PACKAGE = "package"

class RelationType(Enum):
    """Types of relationships between symbols"""
    INHERITS = "inherits"
    IMPORTS = "imports"
    CALLS = "calls"
    REFERENCES = "references"
    DECORATES = "decorates"
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    OVERRIDES = "overrides"
    IMPLEMENTS = "implements"

class ChangeType(Enum):
    """Types of incremental changes"""
    ADD_SYMBOL = "add_symbol"
    REMOVE_SYMBOL = "remove_symbol"
    UPDATE_SYMBOL = "update_symbol"
    ADD_RELATIONSHIP = "add_relationship"
    REMOVE_RELATIONSHIP = "remove_relationship"

# TypedDict for better type safety
class ImportInfo(TypedDict):
    module: str
    name: Optional[str]
    alias: Optional[str]
    line: int
    type: str

class SymbolDict(TypedDict):
    name: str
    type: str
    line_start: int
    line_end: int
    column_start: int
    column_end: int
    docstring: Optional[str]
    signature: Optional[str]
    parent: Optional[str]
    modifiers: List[str]
    annotations: Dict[str, Any]

class ChangeDict(TypedDict):
    type: str
    symbol: Optional[SymbolDict]
    symbol_name: Optional[str]
    updates: Optional[Dict[str, Any]]
    relationship: Optional[Dict[str, Any]]

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Symbol:
    """Represents a code symbol with full metadata"""
    name: str
    type: SymbolType
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    docstring: Optional[str] = None
    signature: Optional[str] = None
    parent: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    annotations: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> SymbolDict:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'type': self.type.value,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'column_start': self.column_start,
            'column_end': self.column_end,
            'docstring': self.docstring,
            'signature': self.signature,
            'parent': self.parent,
            'modifiers': self.modifiers,
            'annotations': self.annotations
        }

@dataclass
class Relationship:
    """Represents a relationship between symbols"""
    source: str
    target: str
    type: RelationType
    line: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['type'] = self.type.value
        return data

@dataclass
class FileIndex:
    """Complete index of a file with all metadata"""
    file_path: str
    language: str
    total_lines: int
    total_chars: int
    hash: str
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    relationships: List[Relationship] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    call_graph: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    dependency_graph: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    complexity_metrics: Dict[str, int] = field(default_factory=dict)
    index_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'file_path': self.file_path,
            'language': self.language,
            'total_lines': self.total_lines,
            'total_chars': self.total_chars,
            'hash': self.hash,
            'symbols': {k: v.to_dict() for k, v in self.symbols.items()},
            'relationships': [r.to_dict() for r in self.relationships],
            'imports': self.imports,
            'exports': self.exports,
            'call_graph': {k: list(v) for k, v in self.call_graph.items()},
            'dependency_graph': {k: list(v) for k, v in self.dependency_graph.items()},
            'complexity_metrics': self.complexity_metrics,
            'index_time': self.index_time
        }

@dataclass
class IndexingResult:
    """Result of indexing operation"""
    success: bool
    index: Optional[FileIndex] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

# ============================================================================
# AST Indexing Engine
# ============================================================================

class ASTIndexer:
    """Advanced AST-based code indexer with error recovery"""
    
    def __init__(self, max_complexity: int = 100):
        """Initialize indexer with complexity limits"""
        self.max_complexity = max_complexity
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.symbols: Dict[str, Symbol] = {}
        self.relationships: List[Relationship] = []
        self.imports: List[ImportInfo] = []
        self.exports: List[str] = []
        self.call_graph: Dict[str, Set[str]] = defaultdict(set)
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        
    def index_python(self, code: str, file_path: str) -> IndexingResult:
        """Index Python code using AST with error recovery"""
        start_time = time.time()
        warnings: List[str] = []
        
        # Reset state
        self._reset()
        
        # Calculate file metrics
        lines = code.splitlines()
        total_lines = len(lines)
        total_chars = len(code)
        file_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Parse AST with error recovery
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            warnings.append(f"Syntax error at line {e.lineno}: {e.msg}")
            
            # Try to parse partial code by removing problematic lines
            tree = self._parse_with_recovery(code, e.lineno if e.lineno else 0)
            if not tree:
                return IndexingResult(
                    success=False,
                    error=f"Failed to parse file: {e}",
                    warnings=warnings
                )
        
        # Walk AST and extract symbols
        try:
            self._walk_ast(tree)
        except Exception as e:
            logger.error(f"Error walking AST: {e}")
            warnings.append(f"Partial indexing: {e}")
        
        # Calculate complexity metrics
        complexity = self._calculate_complexity(tree)
        
        # Check complexity limits
        if complexity.get('cyclomatic_complexity', 0) > self.max_complexity:
            warnings.append(
                f"High complexity detected: {complexity['cyclomatic_complexity']}"
            )
        
        # Create index
        index = FileIndex(
            file_path=file_path,
            language="python",
            total_lines=total_lines,
            total_chars=total_chars,
            hash=file_hash,
            symbols=self.symbols,
            relationships=self.relationships,
            imports=self.imports,
            exports=self.exports,
            call_graph=self.call_graph,
            dependency_graph=self.dependency_graph,
            complexity_metrics=complexity,
            index_time=time.time() - start_time
        )
        
        return IndexingResult(
            success=True,
            index=index,
            warnings=warnings
        )
    
    def _reset(self) -> None:
        """Reset indexer state"""
        self.current_class = None
        self.current_function = None
        self.symbols = {}
        self.relationships = []
        self.imports = []
        self.exports = []
        self.call_graph = defaultdict(set)
        self.dependency_graph = defaultdict(set)
    
    def _parse_with_recovery(
        self,
        code: str,
        error_line: int
    ) -> Optional[ast.AST]:
        """Try to parse code with error recovery"""
        lines = code.splitlines()
        
        # Try removing the error line
        if 0 <= error_line - 1 < len(lines):
            lines[error_line - 1] = "pass  # Error recovery"
            try:
                return ast.parse('\n'.join(lines))
            except SyntaxError:
                pass
        
        # Try parsing only the valid prefix
        for i in range(len(lines), 0, -1):
            try:
                partial_code = '\n'.join(lines[:i])
                return ast.parse(partial_code)
            except SyntaxError:
                continue
        
        return None
    
    def _walk_ast(self, node: ast.AST, parent: Optional[str] = None) -> None:
        """Recursively walk AST and extract symbols"""
        
        # Handle different node types
        if isinstance(node, ast.ClassDef):
            self._process_class(node, parent)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._process_function(node, parent)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            self._process_import(node)
        elif isinstance(node, ast.Assign):
            self._process_assignment(node, parent)
        elif isinstance(node, ast.Call):
            self._process_call(node, parent)
        
        # Recursively process child nodes
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                self._walk_ast(child, node.name if hasattr(node, 'name') else parent)
            else:
                self._walk_ast(child, parent)
    
    def _process_class(self, node: ast.ClassDef, parent: Optional[str]) -> None:
        """Process class definition"""
        symbol_name = f"{parent}.{node.name}" if parent else node.name
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract base classes
        bases: List[str] = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
                self.relationships.append(
                    Relationship(
                        source=symbol_name,
                        target=base.id,
                        type=RelationType.INHERITS,
                        line=node.lineno
                    )
                )
            elif isinstance(base, ast.Attribute):
                base_name = ast.unparse(base) if hasattr(ast, 'unparse') else str(base)
                bases.append(base_name)
        
        # Extract decorators
        decorators = []
        for dec in node.decorator_list:
            if hasattr(dec, 'id'):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Call) and hasattr(dec.func, 'id'):
                decorators.append(dec.func.id)
        
        # Create symbol
        symbol = Symbol(
            name=symbol_name,
            type=SymbolType.CLASS,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            column_start=node.col_offset,
            column_end=node.end_col_offset or node.col_offset,
            docstring=docstring,
            parent=parent,
            annotations={'bases': bases, 'decorators': decorators}
        )
        
        self.symbols[symbol_name] = symbol
        self.exports.append(symbol_name)
        
        # Process class body
        old_class = self.current_class
        self.current_class = symbol_name
        for item in node.body:
            self._walk_ast(item, symbol_name)
        self.current_class = old_class
    
    def _process_function(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        parent: Optional[str]
    ) -> None:
        """Process function/method definition"""
        symbol_name = f"{parent}.{node.name}" if parent else node.name
        symbol_type = SymbolType.METHOD if parent else SymbolType.FUNCTION
        
        # Extract signature
        args: List[str] = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                try:
                    arg_str += f": {ast.unparse(arg.annotation)}" if hasattr(ast, 'unparse') else f": ..."
                except Exception:
                    arg_str += ": ..."
            args.append(arg_str)
        
        signature = f"({', '.join(args)})"
        if node.returns:
            try:
                signature += f" -> {ast.unparse(node.returns)}" if hasattr(ast, 'unparse') else " -> ..."
            except Exception:
                signature += " -> ..."
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Check modifiers
        modifiers: List[str] = []
        if isinstance(node, ast.AsyncFunctionDef):
            modifiers.append("async")
        
        # Process decorators
        for dec in node.decorator_list:
            if hasattr(dec, 'id'):
                modifiers.append(f"@{dec.id}")
                if dec.id == "property":
                    symbol_type = SymbolType.PROPERTY
            elif isinstance(dec, ast.Call) and hasattr(dec.func, 'id'):
                modifiers.append(f"@{dec.func.id}")
        
        # Create symbol
        symbol = Symbol(
            name=symbol_name,
            type=symbol_type,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            column_start=node.col_offset,
            column_end=node.end_col_offset or node.col_offset,
            docstring=docstring,
            signature=signature,
            parent=parent,
            modifiers=modifiers
        )
        
        self.symbols[symbol_name] = symbol
        if not parent:
            self.exports.append(symbol_name)
        
        # Process function body
        old_function = self.current_function
        self.current_function = symbol_name
        for item in node.body:
            self._walk_ast(item, symbol_name)
        self.current_function = old_function
    
    def _process_import(self, node: Union[ast.Import, ast.ImportFrom]) -> None:
        """Process import statement"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_info: ImportInfo = {
                    'module': alias.name,
                    'name': None,
                    'alias': alias.asname,
                    'line': node.lineno,
                    'type': 'import'
                }
                self.imports.append(import_info)
                
                # Create import symbol
                symbol = Symbol(
                    name=alias.asname or alias.name,
                    type=SymbolType.IMPORT,
                    line_start=node.lineno,
                    line_end=node.lineno
                )
                self.symbols[f"import:{alias.name}"] = symbol
        
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                import_info: ImportInfo = {
                    'module': module,
                    'name': alias.name,
                    'alias': alias.asname,
                    'line': node.lineno,
                    'type': 'from_import'
                }
                self.imports.append(import_info)
                
                # Add to dependency graph
                if module:
                    current = self.current_function or self.current_class or '__module__'
                    self.dependency_graph[current].add(module)
    
    def _process_assignment(self, node: ast.Assign, parent: Optional[str]) -> None:
        """Process variable assignment"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Check if it's a constant (UPPER_CASE)
                symbol_type = SymbolType.CONSTANT if target.id.isupper() else SymbolType.VARIABLE
                
                symbol_name = f"{parent}.{target.id}" if parent else target.id
                symbol = Symbol(
                    name=symbol_name,
                    type=symbol_type,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    parent=parent
                )
                self.symbols[symbol_name] = symbol
                
                # Export module-level variables
                if not parent and symbol_type == SymbolType.CONSTANT:
                    self.exports.append(target.id)
    
    def _process_call(self, node: ast.Call, parent: Optional[str]) -> None:
        """Process function call to build call graph"""
        caller = parent or '__module__'
        
        if hasattr(node.func, 'id'):
            callee = node.func.id
            self.call_graph[caller].add(callee)
            
            # Add relationship
            self.relationships.append(
                Relationship(
                    source=caller,
                    target=callee,
                    type=RelationType.CALLS,
                    line=node.lineno
                )
            )
        elif hasattr(node.func, 'attr'):
            # Method call
            if hasattr(node.func.value, 'id'):
                callee = f"{node.func.value.id}.{node.func.attr}"
                self.call_graph[caller].add(callee)
                
                self.relationships.append(
                    Relationship(
                        source=caller,
                        target=callee,
                        type=RelationType.CALLS,
                        line=node.lineno
                    )
                )
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate code complexity metrics"""
        metrics = {
            'cyclomatic_complexity': 1,  # Base complexity
            'cognitive_complexity': 0,
            'nesting_depth': 0,
            'number_of_classes': 0,
            'number_of_functions': 0,
            'number_of_methods': 0,
            'lines_of_code': 0,
            'comment_lines': 0
        }
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_depth = 0
                self.max_depth = 0
                self.in_class = False
            
            def visit_If(self, node: ast.If) -> None:
                metrics['cyclomatic_complexity'] += 1
                metrics['cognitive_complexity'] += (1 + self.current_depth)
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_For(self, node: ast.For) -> None:
                metrics['cyclomatic_complexity'] += 1
                metrics['cognitive_complexity'] += (1 + self.current_depth)
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_While(self, node: ast.While) -> None:
                metrics['cyclomatic_complexity'] += 1
                metrics['cognitive_complexity'] += (1 + self.current_depth)
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                metrics['number_of_classes'] += 1
                old_in_class = self.in_class
                self.in_class = True
                self.generic_visit(node)
                self.in_class = old_in_class
            
            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                if self.in_class:
                    metrics['number_of_methods'] += 1
                else:
                    metrics['number_of_functions'] += 1
                self.generic_visit(node)
            
            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                if self.in_class:
                    metrics['number_of_methods'] += 1
                else:
                    metrics['number_of_functions'] += 1
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        metrics['nesting_depth'] = visitor.max_depth
        
        return metrics

# ============================================================================
# Incremental Indexer
# ============================================================================

class IncrementalIndexer:
    """Incremental indexing for real-time updates with validation"""
    
    def __init__(self, max_cache_size: int = 100):
        """Initialize with cache limits"""
        self.max_cache_size = max_cache_size
        self.cache: Dict[str, FileIndex] = {}
        self.change_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    def update_index(
        self,
        file_path: str,
        changes: List[ChangeDict],
        validator: Any
    ) -> IndexingResult:
        """Update index incrementally based on changes"""
        
        # Validate file path
        try:
            safe_path = validator.validate_file_path(file_path, must_exist=False)
        except ValidationError as e:
            return IndexingResult(success=False, error=str(e))
        
        # Get existing index or create new
        if file_path in self.cache:
            index = self.cache[file_path]
        else:
            # Need to create full index first
            try:
                with open(safe_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                indexer = ASTIndexer()
                result = indexer.index_python(code, file_path)
                if not result.success or not result.index:
                    return result
                index = result.index
                self.cache[file_path] = index
            except Exception as e:
                return IndexingResult(
                    success=False,
                    error=f"Failed to read file: {e}"
                )
        
        # Apply changes incrementally
        warnings = []
        for change in changes:
            try:
                self._apply_change(index, change)
            except Exception as e:
                warnings.append(f"Failed to apply change: {e}")
        
        # Record change history
        self.change_history.append({
            'file_path': file_path,
            'timestamp': time.time(),
            'changes': changes
        })
        
        # Trim history if too large
        if len(self.change_history) > self.max_history:
            self.change_history = self.change_history[-self.max_history:]
        
        # Manage cache size
        if len(self.cache) > self.max_cache_size:
            # Remove oldest entry
            oldest = min(self.cache.keys(), key=lambda k: self.cache[k].index_time)
            del self.cache[oldest]
        
        return IndexingResult(
            success=True,
            index=index,
            warnings=warnings
        )
    
    def _apply_change(self, index: FileIndex, change: ChangeDict) -> None:
        """Apply a single change to the index"""
        change_type_str = change.get('type', '')
        
        try:
            change_type = ChangeType(change_type_str)
        except ValueError:
            raise ValueError(f"Invalid change type: {change_type_str}")
        
        if change_type == ChangeType.ADD_SYMBOL:
            if not change.get('symbol'):
                raise ValueError("Symbol data required for ADD_SYMBOL")
            symbol_data = change['symbol']
            symbol = Symbol(
                name=symbol_data['name'],
                type=SymbolType(symbol_data['type']),
                line_start=symbol_data['line_start'],
                line_end=symbol_data['line_end'],
                column_start=symbol_data.get('column_start', 0),
                column_end=symbol_data.get('column_end', 0),
                docstring=symbol_data.get('docstring'),
                signature=symbol_data.get('signature'),
                parent=symbol_data.get('parent'),
                modifiers=symbol_data.get('modifiers', []),
                annotations=symbol_data.get('annotations', {})
            )
            index.symbols[symbol.name] = symbol
        
        elif change_type == ChangeType.REMOVE_SYMBOL:
            symbol_name = change.get('symbol_name')
            if not symbol_name:
                raise ValueError("Symbol name required for REMOVE_SYMBOL")
            if symbol_name in index.symbols:
                del index.symbols[symbol_name]
        
        elif change_type == ChangeType.UPDATE_SYMBOL:
            symbol_name = change.get('symbol_name')
            updates = change.get('updates')
            if not symbol_name or not updates:
                raise ValueError("Symbol name and updates required for UPDATE_SYMBOL")
            if symbol_name in index.symbols:
                for key, value in updates.items():
                    setattr(index.symbols[symbol_name], key, value)
        
        elif change_type == ChangeType.ADD_RELATIONSHIP:
            rel_data = change.get('relationship')
            if not rel_data:
                raise ValueError("Relationship data required for ADD_RELATIONSHIP")
            rel = Relationship(
                source=rel_data['source'],
                target=rel_data['target'],
                type=RelationType(rel_data['type']),
                line=rel_data['line'],
                metadata=rel_data.get('metadata', {})
            )
            index.relationships.append(rel)

# ============================================================================
# Cross-Reference Tracker
# ============================================================================

class CrossReferenceTracker:
    """Track cross-references across multiple files with optimization"""
    
    def __init__(self, max_files: int = 1000):
        """Initialize with limits"""
        self.max_files = max_files
        self.global_symbols: Dict[str, Dict[str, Any]] = {}
        self.references: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)
        self.file_count = 0
    
    def add_file_index(self, index: FileIndex) -> None:
        """Add a file index to global tracking"""
        
        # Check limits
        if self.file_count >= self.max_files:
            logger.warning(f"Maximum file limit reached ({self.max_files})")
            return
        
        # Add symbols to global registry
        for symbol_name, symbol in index.symbols.items():
            full_name = f"{index.file_path}:{symbol_name}"
            self.global_symbols[full_name] = {
                'file': index.file_path,
                'line': symbol.line_start,
                'type': symbol.type.value,
                'signature': symbol.signature
            }
        
        # Track imports
        for imp in index.imports:
            self.import_graph[index.file_path].add(imp['module'])
        
        # Track references
        for rel in index.relationships:
            if rel.type == RelationType.REFERENCES:
                self.references[rel.target].append({
                    'file': index.file_path,
                    'line': rel.line,
                    'source': rel.source
                })
        
        self.file_count += 1
    
    def find_references(self, symbol: str) -> List[Dict[str, Any]]:
        """Find all references to a symbol"""
        return self.references.get(symbol, [])
    
    def find_definition(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Find definition of a symbol"""
        # First try exact match
        if symbol in self.global_symbols:
            return self.global_symbols[symbol]
        
        # Try with file prefix
        for full_name, info in self.global_symbols.items():
            if full_name.endswith(f":{symbol}"):
                return info
        
        return None
    
    def get_import_chain(
        self,
        start_file: str,
        target_file: str,
        max_depth: int = 10
    ) -> Optional[List[str]]:
        """Find import chain from start_file to target_file"""
        from collections import deque
        
        # BFS to find shortest path with depth limit
        queue = deque([(start_file, [start_file], 0)])
        visited = {start_file}
        
        while queue:
            current, path, depth = queue.popleft()
            
            if depth > max_depth:
                continue
            
            if current == target_file:
                return path
            
            for imported in self.import_graph.get(current, []):
                if imported not in visited:
                    visited.add(imported)
                    queue.append((imported, path + [imported], depth + 1))
        
        return None

# ============================================================================
# Production-Ready Index Server
# ============================================================================

class IndexServer(BaseMCPServer):
    """Production-ready MCP Server for structural code indexing"""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        """Initialize with production features"""
        # Set defaults
        if config is None:
            config = {
                'name': 'index-server',
                'version': '2.0.0',
                'max_request_size': 100 * 1024 * 1024,  # 100MB
                'rate_limit_calls': 50,
                'rate_limit_window': 60,
                'cache_ttl': 3600,
                'max_cache_size': 100
            }
        
        super().__init__(config)
        
        # Initialize indexing components
        self.indexer = ASTIndexer()
        self.incremental = IncrementalIndexer()
        self.cross_ref = CrossReferenceTracker()
        self.indexes: Dict[str, FileIndex] = {}
        
        logger.info(f"IndexServer v{config['version']} initialized")
    
    def _register_tools(self) -> None:
        """Register MCP tools with full validation and error handling"""
        
        @self.server.tool()
        @rate_limit(max_calls=10, time_window=60)
        async def index_file(
            file_path: str,
            language: str = "python"
        ) -> TextContent:
            """
            Create or update index for a file.
            
            Args:
                file_path: Path to file to index
                language: Programming language (currently only 'python')
            
            Returns:
                JSON with index summary or error
            """
            start_time = time.time()
            
            try:
                # Validate inputs
                safe_path = self.validator.validate_file_path(file_path)
                
                if language not in ["python"]:
                    raise ValidationError(f"Unsupported language: {language}")
                
                # Check cache
                cache_key = f"index:{file_path}:{language}"
                if cached := await self.cache.get(cache_key):
                    self.metrics.cache_hits += 1
                    return TextContent(text=cached)
                
                # Read and validate file
                with open(safe_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Check file size
                if len(code) > self.config['max_request_size']:
                    raise ValidationError(
                        f"File too large: {len(code)} bytes (max: {self.config['max_request_size']})"
                    )
                
                # Create index
                result = self.indexer.index_python(code, str(safe_path))
                
                if not result.success:
                    raise ProcessingError(result.error or "Indexing failed")
                
                if not result.index:
                    raise ProcessingError("No index generated")
                
                index = result.index
                
                # Store index
                self.indexes[str(safe_path)] = index
                self.incremental.cache[str(safe_path)] = index
                self.cross_ref.add_file_index(index)
                
                # Create response
                response = {
                    'success': True,
                    'file_path': str(safe_path),
                    'language': language,
                    'total_lines': index.total_lines,
                    'total_symbols': len(index.symbols),
                    'total_relationships': len(index.relationships),
                    'complexity': index.complexity_metrics,
                    'index_time': index.index_time,
                    'warnings': result.warnings,
                    'timestamp': datetime.now().isoformat()
                }
                
                response_json = json.dumps(response, indent=2)
                
                # Cache response
                await self.cache.set(cache_key, response_json)
                
                # Update metrics
                self.metrics.update(
                    success=True,
                    processing_time=time.time() - start_time
                )
                
                return TextContent(text=response_json)
                
            except ValidationError as e:
                self.metrics.validation_errors += 1
                logger.warning(f"Validation error: {e}")
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e),
                    'type': 'validation_error'
                }, indent=2))
            except Exception as e:
                self.metrics.processing_errors += 1
                logger.exception("Error indexing file")
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e),
                    'type': 'processing_error'
                }, indent=2))
        
        @self.server.tool()
        @rate_limit(max_calls=20, time_window=60)
        async def get_symbols(
            file_path: str,
            symbol_type: Optional[str] = None
        ) -> TextContent:
            """
            Get symbols from indexed file.
            
            Args:
                file_path: Path to indexed file
                symbol_type: Optional filter by symbol type
            
            Returns:
                JSON with symbols or error
            """
            try:
                # Validate inputs
                safe_path = self.validator.validate_file_path(file_path, must_exist=False)
                
                if str(safe_path) not in self.indexes:
                    return TextContent(text=json.dumps({
                        'success': False,
                        'error': f'File not indexed: {safe_path}'
                    }, indent=2))
                
                index = self.indexes[str(safe_path)]
                symbols = index.symbols
                
                # Filter by type if specified
                if symbol_type:
                    try:
                        type_enum = SymbolType(symbol_type)
                        symbols = {
                            k: v for k, v in symbols.items()
                            if v.type == type_enum
                        }
                    except ValueError:
                        return TextContent(text=json.dumps({
                            'success': False,
                            'error': f'Invalid symbol type: {symbol_type}',
                            'valid_types': [t.value for t in SymbolType]
                        }, indent=2))
                
                # Convert to serializable format
                result = {
                    'success': True,
                    'file_path': str(safe_path),
                    'symbol_count': len(symbols),
                    'symbols': {k: v.to_dict() for k, v in symbols.items()}
                }
                
                return TextContent(text=json.dumps(result, indent=2))
                
            except Exception as e:
                logger.exception("Error getting symbols")
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e)
                }, indent=2))
        
        @self.server.tool()
        @rate_limit(max_calls=20, time_window=60)
        async def find_references(
            symbol_name: str,
            scope: str = "global"
        ) -> TextContent:
            """
            Find all references to a symbol.
            
            Args:
                symbol_name: Name of symbol to find
                scope: Search scope ('global' or 'local')
            
            Returns:
                JSON with references or error
            """
            try:
                # Validate inputs
                symbol_name = self.validator.sanitize_string(symbol_name, max_length=255)
                
                if scope not in ["global", "local"]:
                    raise ValidationError(f"Invalid scope: {scope}")
                
                references = self.cross_ref.find_references(symbol_name)
                definition = self.cross_ref.find_definition(symbol_name)
                
                result = {
                    'success': True,
                    'symbol': symbol_name,
                    'definition': definition,
                    'references': references,
                    'total_references': len(references)
                }
                
                return TextContent(text=json.dumps(result, indent=2))
                
            except Exception as e:
                logger.exception("Error finding references")
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e)
                }, indent=2))
        
        @self.server.tool()
        @rate_limit(max_calls=10, time_window=60)
        async def update_index(
            file_path: str,
            changes: List[Dict[str, Any]]
        ) -> TextContent:
            """
            Update index incrementally with changes.
            
            Args:
                file_path: Path to file to update
                changes: List of changes to apply
            
            Returns:
                JSON with update result or error
            """
            try:
                # Validate inputs
                if not changes:
                    raise ValidationError("No changes provided")
                
                if len(changes) > 100:
                    raise ValidationError(f"Too many changes: {len(changes)} (max: 100)")
                
                # Convert to typed changes
                typed_changes: List[ChangeDict] = []
                for change in changes:
                    typed_change: ChangeDict = {
                        'type': change.get('type', ''),
                        'symbol': change.get('symbol'),
                        'symbol_name': change.get('symbol_name'),
                        'updates': change.get('updates'),
                        'relationship': change.get('relationship')
                    }
                    typed_changes.append(typed_change)
                
                # Apply changes
                result = self.incremental.update_index(
                    file_path,
                    typed_changes,
                    self.validator
                )
                
                if not result.success:
                    raise ProcessingError(result.error or "Update failed")
                
                if result.index:
                    self.indexes[file_path] = result.index
                
                return TextContent(text=json.dumps({
                    'success': True,
                    'file_path': file_path,
                    'changes_applied': len(changes),
                    'total_symbols': len(result.index.symbols) if result.index else 0,
                    'warnings': result.warnings
                }, indent=2))
                
            except Exception as e:
                logger.exception("Error updating index")
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e)
                }, indent=2))
        
        @self.server.tool()
        async def get_complexity(file_path: str) -> TextContent:
            """
            Get complexity metrics for indexed file.
            
            Args:
                file_path: Path to indexed file
            
            Returns:
                JSON with complexity metrics or error
            """
            try:
                # Validate inputs
                safe_path = self.validator.validate_file_path(file_path, must_exist=False)
                
                if str(safe_path) not in self.indexes:
                    return TextContent(text=json.dumps({
                        'success': False,
                        'error': f'File not indexed: {safe_path}'
                    }, indent=2))
                
                index = self.indexes[str(safe_path)]
                
                # Calculate maintainability index
                complexity = index.complexity_metrics.get('cyclomatic_complexity', 0)
                if complexity < 10:
                    maintainability = 'excellent'
                elif complexity < 20:
                    maintainability = 'good'
                elif complexity < 30:
                    maintainability = 'fair'
                else:
                    maintainability = 'poor'
                
                result = {
                    'success': True,
                    'file_path': str(safe_path),
                    'metrics': index.complexity_metrics,
                    'total_lines': index.total_lines,
                    'summary': {
                        'complexity_score': complexity,
                        'cognitive_load': index.complexity_metrics.get('cognitive_complexity', 0),
                        'maintainability': maintainability,
                        'risk_level': 'high' if complexity > 30 else 'medium' if complexity > 20 else 'low'
                    }
                }
                
                return TextContent(text=json.dumps(result, indent=2))
                
            except Exception as e:
                logger.exception("Error getting complexity")
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e)
                }, indent=2))

# ============================================================================
# Main Entry Point
# ============================================================================

def main() -> None:
    """Main entry point"""
    import asyncio
    
    # Load configuration from environment or use defaults
    config: ServerConfig = {
        'name': 'index-server',
        'version': '2.0.0',
        'log_level': 'INFO'
    }
    
    server = IndexServer(config)
    
    try:
        logger.info(f"Starting IndexServer v{config['version']}...")
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()