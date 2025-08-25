#!/usr/bin/env python3
"""
ChunkServer - Intelligent File Chunking MCP Server (Production-Ready)
Part of MFHS-MCP System for handling massive codebases

This server provides intelligent chunking strategies for processing files
of unlimited size through AST-based, semantic, and line-based chunking.

Version: 2.0.0 - Production Ready
"""

import ast
import hashlib
import json
import logging
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Set, Callable, Awaitable
import numpy as np
from abc import abstractmethod

# Import base server
try:
    from mcp_base import (
        BaseMCPServer,
        ServerConfig,
        ValidationError,
        ProcessingError,
        rate_limit,
        create_json_response
    )
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from mcp_base import (
        BaseMCPServer,
        ServerConfig,
        ValidationError,
        ProcessingError,
        rate_limit,
        create_json_response
    )

# MCP imports with graceful fallback
try:
    from mcp import Server, Tool
    from mcp.types import TextContent, Resource
    MCP_AVAILABLE = True
except ImportError:
    print("Warning: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    MCP_AVAILABLE = False
    TextContent = lambda text: type('TextContent', (), {'text': text})()

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class ChunkStrategy(Enum):
    """Chunking strategies available"""
    LINE_BASED = "line_based"
    AST_BASED = "ast_based"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    SLIDING_WINDOW = "sliding_window"
    FUNCTION_BASED = "function_based"
    CLASS_BASED = "class_based"

class ChunkType(Enum):
    """Types of code chunks"""
    IMPORTS = "imports"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    DOCSTRING = "docstring"
    COMMENT_BLOCK = "comment_block"
    CODE_BLOCK = "code_block"
    TEST = "test"
    MAIN = "main"
    UNKNOWN = "unknown"

@dataclass
class CodeChunk:
    """Represents a single code chunk"""
    id: str
    content: str
    type: ChunkType
    line_start: int
    line_end: int
    size_bytes: int
    size_lines: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    hash: str = field(default="")
    
    def __post_init__(self) -> None:
        """Calculate hash if not provided"""
        if not self.hash:
            self.hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['type'] = self.type.value
        return data

@dataclass
class ChunkingResult:
    """Result of chunking operation"""
    file_path: str
    strategy: ChunkStrategy
    chunks: List[CodeChunk]
    total_lines: int
    total_bytes: int
    processing_time: float
    success: bool = True
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'file_path': self.file_path,
            'strategy': self.strategy.value,
            'chunks': [chunk.to_dict() for chunk in self.chunks],
            'chunk_count': len(self.chunks),
            'total_lines': self.total_lines,
            'total_bytes': self.total_bytes,
            'processing_time': round(self.processing_time, 3),
            'success': self.success,
            'errors': self.errors,
            'metadata': self.metadata
        }

# ============================================================================
# Chunking Strategies
# ============================================================================

class ChunkingEngine:
    """Base class for chunking strategies"""
    
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 0):
        """
        Initialize chunking engine
        
        Args:
            max_chunk_size: Maximum lines per chunk
            overlap: Number of overlapping lines between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = max(0, overlap)
    
    @abstractmethod
    async def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        """Chunk content - must be implemented by subclasses"""
        pass
    
    def _create_chunk(
        self,
        content: str,
        chunk_type: ChunkType,
        line_start: int,
        line_end: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CodeChunk:
        """Create a code chunk"""
        chunk_id = hashlib.md5(
            f"{line_start}:{line_end}:{content[:50]}".encode()
        ).hexdigest()[:8]
        
        return CodeChunk(
            id=chunk_id,
            content=content,
            type=chunk_type,
            line_start=line_start,
            line_end=line_end,
            size_bytes=len(content.encode()),
            size_lines=len(content.splitlines()),
            metadata=metadata or {}
        )

class LineBasedChunker(ChunkingEngine):
    """Simple line-based chunking"""
    
    async def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        """Chunk by lines with optional overlap"""
        lines = content.splitlines(keepends=True)
        chunks = []
        
        i = 0
        while i < len(lines):
            # Calculate chunk boundaries
            start = max(0, i - self.overlap) if i > 0 else i
            end = min(i + self.max_chunk_size, len(lines))
            
            # Create chunk
            chunk_lines = lines[start:end]
            chunk_content = ''.join(chunk_lines)
            
            chunk = self._create_chunk(
                chunk_content,
                ChunkType.CODE_BLOCK,
                start + 1,
                end,
                {'overlap_start': i > 0 and start < i}
            )
            chunks.append(chunk)
            
            # Move to next chunk
            i = end
        
        return chunks

class ASTBasedChunker(ChunkingEngine):
    """AST-based intelligent chunking for Python code"""
    
    async def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        """Chunk based on AST structure"""
        chunks = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"AST parsing failed, falling back to line-based: {e}")
            # Fallback to line-based chunking
            line_chunker = LineBasedChunker(self.max_chunk_size, self.overlap)
            return await line_chunker.chunk(content, file_path)
        
        lines = content.splitlines(keepends=True)
        
        # Extract imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        if imports:
            import_lines = self._get_node_lines(imports, lines)
            if import_lines:
                chunk = self._create_chunk(
                    import_lines,
                    ChunkType.IMPORTS,
                    imports[0].lineno,
                    imports[-1].end_lineno or imports[-1].lineno,
                    {'import_count': len(imports)}
                )
                chunks.append(chunk)
        
        # Extract classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_content = self._get_node_content(node, lines)
                
                # Check if class is too large
                class_lines = class_content.splitlines()
                if len(class_lines) > self.max_chunk_size:
                    # Split class into method chunks
                    chunks.extend(self._chunk_class(node, lines))
                else:
                    chunk = self._create_chunk(
                        class_content,
                        ChunkType.CLASS,
                        node.lineno,
                        node.end_lineno or node.lineno,
                        {
                            'class_name': node.name,
                            'methods': [m.name for m in node.body 
                                       if isinstance(m, ast.FunctionDef)]
                        }
                    )
                    chunks.append(chunk)
        
        # Extract standalone functions
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                func_content = self._get_node_content(node, lines)
                
                chunk = self._create_chunk(
                    func_content,
                    ChunkType.FUNCTION,
                    node.lineno,
                    node.end_lineno or node.lineno,
                    {
                        'function_name': node.name,
                        'is_test': node.name.startswith('test_'),
                        'is_main': node.name == 'main'
                    }
                )
                chunks.append(chunk)
        
        # Sort chunks by line number
        chunks.sort(key=lambda c: c.line_start)
        
        return chunks
    
    def _get_node_content(self, node: ast.AST, lines: List[str]) -> str:
        """Get content for an AST node"""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            start = node.lineno - 1
            end = node.end_lineno if node.end_lineno else node.lineno
            return ''.join(lines[start:end])
        return ""
    
    def _get_node_lines(self, nodes: List[ast.AST], lines: List[str]) -> str:
        """Get combined content for multiple nodes"""
        if not nodes:
            return ""
        
        start = min(n.lineno for n in nodes) - 1
        end = max(n.end_lineno if n.end_lineno else n.lineno for n in nodes)
        return ''.join(lines[start:end])
    
    def _chunk_class(self, class_node: ast.ClassDef, lines: List[str]) -> List[CodeChunk]:
        """Chunk a large class into methods"""
        chunks = []
        
        # Class header and docstring
        header_end = class_node.body[0].lineno - 1 if class_node.body else class_node.lineno
        header_content = ''.join(lines[class_node.lineno - 1:header_end])
        
        if header_content.strip():
            chunk = self._create_chunk(
                header_content,
                ChunkType.CLASS,
                class_node.lineno,
                header_end,
                {'class_name': class_node.name, 'is_header': True}
            )
            chunks.append(chunk)
        
        # Methods
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_content = self._get_node_content(node, lines)
                
                chunk = self._create_chunk(
                    method_content,
                    ChunkType.METHOD,
                    node.lineno,
                    node.end_lineno or node.lineno,
                    {
                        'class_name': class_node.name,
                        'method_name': node.name,
                        'is_private': node.name.startswith('_'),
                        'is_magic': node.name.startswith('__') and node.name.endswith('__')
                    }
                )
                chunks.append(chunk)
        
        return chunks

class SemanticChunker(ChunkingEngine):
    """Semantic-based chunking using patterns and context"""
    
    async def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        """Chunk based on semantic boundaries"""
        chunks = []
        lines = content.splitlines(keepends=True)
        
        # Define semantic boundaries
        section_patterns = [
            (r'^#{1,6}\s+(.+)$', 'markdown_header'),
            (r'^"""[\s\S]*?"""', 'docstring'),
            (r'^\'\'\'[\s\S]*?\'\'\'', 'docstring'),
            (r'^#\s*={3,}.*?$', 'section_separator'),
            (r'^#\s*-{3,}.*?$', 'section_separator'),
            (r'^if\s+__name__\s*==\s*["\']__main__["\']:', 'main_block')
        ]
        
        # Find semantic boundaries
        boundaries = []
        for i, line in enumerate(lines):
            for pattern, boundary_type in section_patterns:
                if re.match(pattern, line.strip()):
                    boundaries.append((i, boundary_type))
                    break
        
        # Create chunks based on boundaries
        prev_boundary = 0
        for boundary_line, boundary_type in boundaries:
            if boundary_line - prev_boundary > 0:
                chunk_content = ''.join(lines[prev_boundary:boundary_line])
                if chunk_content.strip():
                    chunk = self._create_chunk(
                        chunk_content,
                        self._determine_chunk_type(chunk_content),
                        prev_boundary + 1,
                        boundary_line,
                        {'boundary_type': boundary_type}
                    )
                    chunks.append(chunk)
            prev_boundary = boundary_line
        
        # Add remaining content
        if prev_boundary < len(lines):
            chunk_content = ''.join(lines[prev_boundary:])
            if chunk_content.strip():
                chunk = self._create_chunk(
                    chunk_content,
                    self._determine_chunk_type(chunk_content),
                    prev_boundary + 1,
                    len(lines),
                    {}
                )
                chunks.append(chunk)
        
        # Split large chunks
        final_chunks = []
        for chunk in chunks:
            if chunk.size_lines > self.max_chunk_size:
                # Split into smaller chunks
                sub_chunks = await self._split_large_chunk(chunk)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _determine_chunk_type(self, content: str) -> ChunkType:
        """Determine the type of a chunk based on content"""
        content_lower = content.lower()
        
        if 'import ' in content_lower[:100]:
            return ChunkType.IMPORTS
        elif 'class ' in content_lower[:50]:
            return ChunkType.CLASS
        elif 'def ' in content_lower[:50]:
            return ChunkType.FUNCTION
        elif 'def test_' in content_lower:
            return ChunkType.TEST
        elif '"""' in content or "'''" in content:
            return ChunkType.DOCSTRING
        elif content.strip().startswith('#'):
            return ChunkType.COMMENT_BLOCK
        else:
            return ChunkType.CODE_BLOCK
    
    async def _split_large_chunk(self, chunk: CodeChunk) -> List[CodeChunk]:
        """Split a large chunk into smaller ones"""
        lines = chunk.content.splitlines(keepends=True)
        sub_chunks = []
        
        for i in range(0, len(lines), self.max_chunk_size):
            sub_content = ''.join(lines[i:i + self.max_chunk_size])
            sub_chunk = self._create_chunk(
                sub_content,
                chunk.type,
                chunk.line_start + i,
                min(chunk.line_start + i + self.max_chunk_size, chunk.line_end),
                {'parent_chunk': chunk.id, 'part': i // self.max_chunk_size + 1}
            )
            sub_chunks.append(sub_chunk)
        
        return sub_chunks

class HybridChunker(ChunkingEngine):
    """Hybrid chunking combining multiple strategies"""
    
    async def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        """Use multiple strategies and merge results"""
        chunks = []
        
        # Try AST-based first for Python files
        if file_path.endswith('.py'):
            ast_chunker = ASTBasedChunker(self.max_chunk_size, self.overlap)
            try:
                chunks = await ast_chunker.chunk(content, file_path)
                if chunks:
                    return chunks
            except Exception as e:
                logger.warning(f"AST chunking failed: {e}")
        
        # Fallback to semantic chunking
        semantic_chunker = SemanticChunker(self.max_chunk_size, self.overlap)
        try:
            chunks = await semantic_chunker.chunk(content, file_path)
            if chunks:
                return chunks
        except Exception as e:
            logger.warning(f"Semantic chunking failed: {e}")
        
        # Final fallback to line-based
        line_chunker = LineBasedChunker(self.max_chunk_size, self.overlap)
        return await line_chunker.chunk(content, file_path)

# ============================================================================
# Chunk Server Implementation
# ============================================================================

class ChunkServer(BaseMCPServer):
    """
    Production-ready MCP server for intelligent file chunking
    """
    
    def __init__(self, config: Optional[ServerConfig] = None):
        """Initialize chunk server"""
        # Set default config
        default_config: ServerConfig = {
            'name': 'chunk-server',
            'version': '2.0.0',
            'max_request_size': 50_000_000,  # 50MB for large files
            'timeout': 60,  # Longer timeout for large files
            'rate_limit_calls': 50,
            'rate_limit_window': 60,
            'enable_monitoring': True,
            'enable_health_check': True,
            'log_level': 'INFO',
            'cache_ttl': 7200,  # 2 hours for chunk cache
            'max_cache_size': 100
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(default_config)
        
        # Initialize chunking engines
        self.engines = {
            ChunkStrategy.LINE_BASED: LineBasedChunker(),
            ChunkStrategy.AST_BASED: ASTBasedChunker(),
            ChunkStrategy.SEMANTIC: SemanticChunker(),
            ChunkStrategy.HYBRID: HybridChunker()
        }
        
        logger.info("ChunkServer initialized with production configuration")
    
    def _register_tools(self) -> None:
        """Register chunk server specific tools"""
        
        @self.server.tool()
        @rate_limit(max_calls=10, time_window=60)
        async def chunk_file(
            file_path: str,
            strategy: str = "hybrid",
            max_chunk_size: int = 1000,
            overlap: int = 0,
            cache_key: Optional[str] = None
        ) -> TextContent:
            """
            Chunk a file using specified strategy
            
            Args:
                file_path: Path to file to chunk
                strategy: Chunking strategy (line_based, ast_based, semantic, hybrid)
                max_chunk_size: Maximum lines per chunk
                overlap: Number of overlapping lines between chunks
                cache_key: Optional cache key for results
                
            Returns:
                JSON response with chunks
            """
            try:
                # Check cache if key provided
                if cache_key:
                    cached = await self.cache.get(cache_key)
                    if cached:
                        logger.info(f"Cache hit for key: {cache_key}")
                        return TextContent(text=cached)
                
                # Validate inputs
                safe_path = self.validator.validate_file_path(file_path, must_exist=True)
                
                if max_chunk_size <= 0 or max_chunk_size > 10000:
                    raise ValidationError("max_chunk_size must be between 1 and 10000")
                
                if overlap < 0 or overlap >= max_chunk_size:
                    raise ValidationError("overlap must be between 0 and max_chunk_size-1")
                
                # Parse strategy
                try:
                    chunk_strategy = ChunkStrategy(strategy.lower())
                except ValueError:
                    raise ValidationError(
                        f"Invalid strategy. Must be one of: "
                        f"{', '.join(s.value for s in ChunkStrategy)}"
                    )
                
                # Read file
                with open(safe_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check file size
                if len(content) > self.config['max_request_size']:
                    raise ValidationError(
                        f"File too large ({len(content)} bytes). "
                        f"Max: {self.config['max_request_size']} bytes"
                    )
                
                # Get appropriate engine
                engine = self.engines.get(chunk_strategy)
                if not engine:
                    raise ProcessingError(f"No engine for strategy: {chunk_strategy}")
                
                # Configure engine
                engine.max_chunk_size = max_chunk_size
                engine.overlap = overlap
                
                # Process file
                start_time = time.time()
                chunks = await self.process_request(
                    engine.chunk,
                    content,
                    str(safe_path)
                )
                processing_time = time.time() - start_time
                
                # Create result
                result = ChunkingResult(
                    file_path=str(safe_path),
                    strategy=chunk_strategy,
                    chunks=chunks,
                    total_lines=len(content.splitlines()),
                    total_bytes=len(content.encode()),
                    processing_time=processing_time,
                    metadata={
                        'max_chunk_size': max_chunk_size,
                        'overlap': overlap,
                        'avg_chunk_size': sum(c.size_lines for c in chunks) / len(chunks) 
                                         if chunks else 0
                    }
                )
                
                response = create_json_response(result.to_dict())
                
                # Cache if key provided
                if cache_key:
                    await self.cache.set(cache_key, response)
                
                return TextContent(text=response)
                
            except ValidationError as e:
                logger.warning(f"Validation error: {e}")
                return TextContent(text=create_json_response(None, False, str(e)))
            except Exception as e:
                logger.exception("Error chunking file")
                return TextContent(text=create_json_response(None, False, str(e)))
        
        @self.server.tool()
        async def get_chunk(
            file_path: str,
            chunk_id: str
        ) -> TextContent:
            """
            Retrieve a specific chunk by ID
            
            Args:
                file_path: Path to chunked file
                chunk_id: ID of chunk to retrieve
                
            Returns:
                JSON response with chunk content
            """
            try:
                # Try to get from cache
                cache_key = f"{file_path}:{chunk_id}"
                cached = await self.cache.get(cache_key)
                if cached:
                    return TextContent(text=cached)
                
                # Re-chunk file to find specific chunk
                safe_path = self.validator.validate_file_path(file_path, must_exist=True)
                
                with open(safe_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use hybrid strategy by default
                engine = self.engines[ChunkStrategy.HYBRID]
                chunks = await engine.chunk(content, str(safe_path))
                
                # Find requested chunk
                for chunk in chunks:
                    if chunk.id == chunk_id:
                        response = create_json_response(chunk.to_dict())
                        await self.cache.set(cache_key, response)
                        return TextContent(text=response)
                
                raise ProcessingError(f"Chunk not found: {chunk_id}")
                
            except Exception as e:
                logger.exception("Error retrieving chunk")
                return TextContent(text=create_json_response(None, False, str(e)))
        
        @self.server.tool()
        async def analyze_chunks(
            file_path: str,
            strategy: str = "hybrid"
        ) -> TextContent:
            """
            Analyze chunk distribution for a file
            
            Args:
                file_path: Path to file to analyze
                strategy: Chunking strategy to use
                
            Returns:
                JSON response with analysis
            """
            try:
                safe_path = self.validator.validate_file_path(file_path, must_exist=True)
                
                # Parse strategy
                try:
                    chunk_strategy = ChunkStrategy(strategy.lower())
                except ValueError:
                    raise ValidationError(f"Invalid strategy: {strategy}")
                
                with open(safe_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Get chunks
                engine = self.engines[chunk_strategy]
                chunks = await engine.chunk(content, str(safe_path))
                
                # Analyze distribution
                analysis = {
                    'file_path': str(safe_path),
                    'strategy': strategy,
                    'total_chunks': len(chunks),
                    'chunk_types': {},
                    'size_distribution': {
                        'min_lines': min(c.size_lines for c in chunks) if chunks else 0,
                        'max_lines': max(c.size_lines for c in chunks) if chunks else 0,
                        'avg_lines': sum(c.size_lines for c in chunks) / len(chunks) 
                                    if chunks else 0,
                        'total_lines': sum(c.size_lines for c in chunks)
                    },
                    'chunks_by_type': []
                }
                
                # Count by type
                for chunk in chunks:
                    chunk_type = chunk.type.value
                    if chunk_type not in analysis['chunk_types']:
                        analysis['chunk_types'][chunk_type] = 0
                    analysis['chunk_types'][chunk_type] += 1
                
                # List chunks
                for chunk in chunks:
                    analysis['chunks_by_type'].append({
                        'id': chunk.id,
                        'type': chunk.type.value,
                        'lines': f"{chunk.line_start}-{chunk.line_end}",
                        'size': chunk.size_lines
                    })
                
                return TextContent(text=create_json_response(analysis))
                
            except Exception as e:
                logger.exception("Error analyzing chunks")
                return TextContent(text=create_json_response(None, False, str(e)))

# ============================================================================
# Main Entry Point
# ============================================================================

def main() -> None:
    """Main entry point"""
    import asyncio
    
    # Configure server
    config: ServerConfig = {
        'name': 'chunk-server',
        'version': '2.0.0',
        'log_level': 'INFO',
        'enable_monitoring': True,
        'enable_health_check': True
    }
    
    # Create and run server
    server = ChunkServer(config)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()