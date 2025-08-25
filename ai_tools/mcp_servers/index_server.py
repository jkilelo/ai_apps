#!/usr/bin/env python3
"""
IndexServer - Structural Understanding MCP Server
Part of MFHS-MCP System for handling massive codebases

Provides AST-based indexing, symbol table management, and cross-reference tracking
for files of unlimited size through intelligent indexing strategies.
"""

import ast
import json
import logging
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union
import hashlib
import time
from collections import defaultdict
import re

# MCP Server SDK imports
try:
    from mcp import Server, Tool
    from mcp.types import TextContent, Resource
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IndexServer")

# ============================================================================
# Data Models
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

@dataclass
class Symbol:
    """Represents a code symbol"""
    name: str
    type: SymbolType
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    docstring: Optional[str] = None
    signature: Optional[str] = None
    parent: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)  # async, static, private, etc.
    annotations: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['type'] = self.type.value
        return data

@dataclass
class Relationship:
    """Represents a relationship between symbols"""
    source: str
    target: str
    type: RelationType
    line: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['type'] = self.type.value
        return data

@dataclass
class FileIndex:
    """Complete index of a file"""
    file_path: str
    language: str
    total_lines: int
    total_chars: int
    hash: str
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    relationships: List[Relationship] = field(default_factory=list)
    imports: List[Dict[str, Any]] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    call_graph: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    dependency_graph: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    complexity_metrics: Dict[str, int] = field(default_factory=dict)
    index_time: float = 0.0
    
    def to_dict(self) -> Dict:
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

# ============================================================================
# AST Indexer
# ============================================================================

class ASTIndexer:
    """Advanced AST-based code indexer"""
    
    def __init__(self):
        self.current_class = None
        self.current_function = None
        self.symbols = {}
        self.relationships = []
        self.imports = []
        self.exports = []
        self.call_graph = defaultdict(set)
        self.dependency_graph = defaultdict(set)
        
    def index_python(self, code: str, file_path: str) -> FileIndex:
        """Index Python code using AST"""
        start_time = time.time()
        
        # Calculate file metrics
        lines = code.splitlines()
        total_lines = len(lines)
        total_chars = len(code)
        file_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return FileIndex(
                file_path=file_path,
                language="python",
                total_lines=total_lines,
                total_chars=total_chars,
                hash=file_hash,
                index_time=time.time() - start_time
            )
        
        # Walk AST and extract symbols
        self._walk_ast(tree)
        
        # Calculate complexity metrics
        complexity = self._calculate_complexity(tree)
        
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
        
        return index
    
    def _walk_ast(self, node: ast.AST, parent: Optional[str] = None):
        """Recursively walk AST and extract symbols"""
        
        # Handle different node types
        if isinstance(node, ast.ClassDef):
            self._process_class(node, parent)
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            self._process_function(node, parent)
        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
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
    
    def _process_class(self, node: ast.ClassDef, parent: Optional[str]):
        """Process class definition"""
        symbol_name = f"{parent}.{node.name}" if parent else node.name
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract base classes
        bases = []
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
            annotations={'bases': bases, 'decorators': [d.id for d in node.decorator_list if hasattr(d, 'id')]}
        )
        
        self.symbols[symbol_name] = symbol
        self.current_class = symbol_name
        
        # Process class body
        for item in node.body:
            self._walk_ast(item, symbol_name)
        
        self.current_class = parent
    
    def _process_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], parent: Optional[str]):
        """Process function/method definition"""
        symbol_name = f"{parent}.{node.name}" if parent else node.name
        symbol_type = SymbolType.METHOD if parent else SymbolType.FUNCTION
        
        # Extract signature
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}" if hasattr(ast, 'unparse') else f": ..."
            args.append(arg_str)
        
        signature = f"({', '.join(args)})"
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}" if hasattr(ast, 'unparse') else " -> ..."
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Check modifiers
        modifiers = []
        if isinstance(node, ast.AsyncFunctionDef):
            modifiers.append("async")
        if node.decorator_list:
            for dec in node.decorator_list:
                if hasattr(dec, 'id'):
                    modifiers.append(f"@{dec.id}")
                    if dec.id == "property":
                        symbol_type = SymbolType.PROPERTY
        
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
        self.current_function = symbol_name
        
        # Process function body
        for item in node.body:
            self._walk_ast(item, symbol_name)
        
        self.current_function = parent
    
    def _process_import(self, node: Union[ast.Import, ast.ImportFrom]):
        """Process import statement"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_info = {
                    'module': alias.name,
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
                import_info = {
                    'module': module,
                    'name': alias.name,
                    'alias': alias.asname,
                    'line': node.lineno,
                    'type': 'from_import'
                }
                self.imports.append(import_info)
                
                # Add to dependency graph
                if module:
                    self.dependency_graph[self.current_function or self.current_class or '__module__'].add(module)
    
    def _process_assignment(self, node: ast.Assign, parent: Optional[str]):
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
    
    def _process_call(self, node: ast.Call, parent: Optional[str]):
        """Process function call to build call graph"""
        if hasattr(node.func, 'id'):
            caller = parent or '__module__'
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
            caller = parent or '__module__'
            if hasattr(node.func.value, 'id'):
                callee = f"{node.func.value.id}.{node.func.attr}"
                self.call_graph[caller].add(callee)
    
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
            
            def visit_If(self, node):
                metrics['cyclomatic_complexity'] += 1
                metrics['cognitive_complexity'] += (1 + self.current_depth)
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_For(self, node):
                metrics['cyclomatic_complexity'] += 1
                metrics['cognitive_complexity'] += (1 + self.current_depth)
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_While(self, node):
                metrics['cyclomatic_complexity'] += 1
                metrics['cognitive_complexity'] += (1 + self.current_depth)
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_ClassDef(self, node):
                metrics['number_of_classes'] += 1
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                if self.current_depth > 0:  # Method inside class
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
    """Incremental indexing for real-time updates"""
    
    def __init__(self):
        self.cache: Dict[str, FileIndex] = {}
        self.change_history: List[Dict] = []
    
    def update_index(self, file_path: str, changes: List[Dict]) -> FileIndex:
        """Update index incrementally based on changes"""
        
        # Get existing index or create new
        if file_path in self.cache:
            index = self.cache[file_path]
        else:
            # Need to create full index first
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            indexer = ASTIndexer()
            index = indexer.index_python(code, file_path)
            self.cache[file_path] = index
        
        # Apply changes incrementally
        for change in changes:
            self._apply_change(index, change)
        
        # Record change history
        self.change_history.append({
            'file_path': file_path,
            'timestamp': time.time(),
            'changes': changes
        })
        
        return index
    
    def _apply_change(self, index: FileIndex, change: Dict):
        """Apply a single change to the index"""
        change_type = change.get('type')
        
        if change_type == 'add_symbol':
            symbol = Symbol(**change['symbol'])
            index.symbols[symbol.name] = symbol
        
        elif change_type == 'remove_symbol':
            symbol_name = change['symbol_name']
            if symbol_name in index.symbols:
                del index.symbols[symbol_name]
        
        elif change_type == 'update_symbol':
            symbol_name = change['symbol_name']
            if symbol_name in index.symbols:
                for key, value in change['updates'].items():
                    setattr(index.symbols[symbol_name], key, value)
        
        elif change_type == 'add_relationship':
            rel = Relationship(**change['relationship'])
            index.relationships.append(rel)

# ============================================================================
# Cross-Reference Tracker
# ============================================================================

class CrossReferenceTracker:
    """Track cross-references across multiple files"""
    
    def __init__(self):
        self.global_symbols: Dict[str, Dict] = {}  # symbol -> {file, line, type}
        self.references: Dict[str, List[Dict]] = defaultdict(list)  # symbol -> [{file, line, context}]
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)  # file -> imported files
    
    def add_file_index(self, index: FileIndex):
        """Add a file index to global tracking"""
        
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
    
    def find_references(self, symbol: str) -> List[Dict]:
        """Find all references to a symbol"""
        return self.references.get(symbol, [])
    
    def find_definition(self, symbol: str) -> Optional[Dict]:
        """Find definition of a symbol"""
        # First try exact match
        if symbol in self.global_symbols:
            return self.global_symbols[symbol]
        
        # Try with file prefix
        for full_name, info in self.global_symbols.items():
            if full_name.endswith(f":{symbol}"):
                return info
        
        return None
    
    def get_import_chain(self, start_file: str, target_file: str) -> Optional[List[str]]:
        """Find import chain from start_file to target_file"""
        # BFS to find shortest path
        from collections import deque
        
        queue = deque([(start_file, [start_file])])
        visited = {start_file}
        
        while queue:
            current, path = queue.popleft()
            
            if current == target_file:
                return path
            
            for imported in self.import_graph.get(current, []):
                if imported not in visited:
                    visited.add(imported)
                    queue.append((imported, path + [imported]))
        
        return None

# ============================================================================
# MCP Server Implementation
# ============================================================================

class IndexMCPServer:
    """MCP Server for structural code indexing"""
    
    def __init__(self):
        self.server = Server("index-server")
        self.indexer = ASTIndexer()
        self.incremental = IncrementalIndexer()
        self.cross_ref = CrossReferenceTracker()
        self.indexes: Dict[str, FileIndex] = {}
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.server.tool()
        async def index_file(file_path: str, language: str = "python") -> TextContent:
            """Create or update index for a file"""
            try:
                # Read file
                path = Path(file_path)
                if not path.exists():
                    return TextContent(text=json.dumps({
                        'error': f'File not found: {file_path}'
                    }))
                
                with open(path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Create index based on language
                if language == "python":
                    index = self.indexer.index_python(code, file_path)
                else:
                    return TextContent(text=json.dumps({
                        'error': f'Language not supported yet: {language}'
                    }))
                
                # Store index
                self.indexes[file_path] = index
                self.incremental.cache[file_path] = index
                self.cross_ref.add_file_index(index)
                
                # Return summary
                return TextContent(text=json.dumps({
                    'file_path': file_path,
                    'language': language,
                    'total_lines': index.total_lines,
                    'total_symbols': len(index.symbols),
                    'total_relationships': len(index.relationships),
                    'complexity': index.complexity_metrics,
                    'index_time': index.index_time,
                    'status': 'success'
                }, indent=2))
                
            except Exception as e:
                logger.error(f"Error indexing file: {e}")
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def get_symbols(file_path: str, symbol_type: Optional[str] = None) -> TextContent:
            """Get symbols from indexed file"""
            if file_path not in self.indexes:
                return TextContent(text=json.dumps({
                    'error': f'File not indexed: {file_path}'
                }))
            
            index = self.indexes[file_path]
            symbols = index.symbols
            
            # Filter by type if specified
            if symbol_type:
                try:
                    type_enum = SymbolType(symbol_type)
                    symbols = {k: v for k, v in symbols.items() if v.type == type_enum}
                except ValueError:
                    return TextContent(text=json.dumps({
                        'error': f'Invalid symbol type: {symbol_type}',
                        'valid_types': [t.value for t in SymbolType]
                    }))
            
            # Convert to serializable format
            result = {
                'file_path': file_path,
                'symbol_count': len(symbols),
                'symbols': {k: v.to_dict() for k, v in symbols.items()}
            }
            
            return TextContent(text=json.dumps(result, indent=2))
        
        @self.server.tool()
        async def find_references(symbol_name: str, scope: str = "global") -> TextContent:
            """Find all references to a symbol"""
            references = self.cross_ref.find_references(symbol_name)
            definition = self.cross_ref.find_definition(symbol_name)
            
            result = {
                'symbol': symbol_name,
                'definition': definition,
                'references': references,
                'total_references': len(references)
            }
            
            return TextContent(text=json.dumps(result, indent=2))
        
        @self.server.tool()
        async def get_call_graph(file_path: str, function_name: Optional[str] = None) -> TextContent:
            """Get call graph for file or specific function"""
            if file_path not in self.indexes:
                return TextContent(text=json.dumps({
                    'error': f'File not indexed: {file_path}'
                }))
            
            index = self.indexes[file_path]
            
            if function_name:
                # Get calls for specific function
                calls = list(index.call_graph.get(function_name, []))
                result = {
                    'function': function_name,
                    'calls': calls,
                    'total_calls': len(calls)
                }
            else:
                # Get entire call graph
                result = {
                    'file_path': file_path,
                    'call_graph': {k: list(v) for k, v in index.call_graph.items()},
                    'total_functions': len(index.call_graph)
                }
            
            return TextContent(text=json.dumps(result, indent=2))
        
        @self.server.tool()
        async def update_index(file_path: str, changes: List[Dict]) -> TextContent:
            """Update index incrementally with changes"""
            try:
                index = self.incremental.update_index(file_path, changes)
                self.indexes[file_path] = index
                
                return TextContent(text=json.dumps({
                    'file_path': file_path,
                    'changes_applied': len(changes),
                    'total_symbols': len(index.symbols),
                    'status': 'success'
                }, indent=2))
                
            except Exception as e:
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def get_complexity(file_path: str) -> TextContent:
            """Get complexity metrics for indexed file"""
            if file_path not in self.indexes:
                return TextContent(text=json.dumps({
                    'error': f'File not indexed: {file_path}'
                }))
            
            index = self.indexes[file_path]
            
            result = {
                'file_path': file_path,
                'metrics': index.complexity_metrics,
                'total_lines': index.total_lines,
                'summary': {
                    'complexity_score': index.complexity_metrics.get('cyclomatic_complexity', 0),
                    'cognitive_load': index.complexity_metrics.get('cognitive_complexity', 0),
                    'maintainability': 'good' if index.complexity_metrics.get('cyclomatic_complexity', 0) < 10 else 'needs attention'
                }
            }
            
            return TextContent(text=json.dumps(result, indent=2))
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        logger.info("Starting IndexServer MCP server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    import asyncio
    
    server = IndexMCPServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()