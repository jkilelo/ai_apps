#!/usr/bin/env python3
"""
ChunkServer - MCP Server for Intelligent File Chunking
Part of MFHS-MCP: The Ultimate Massive File Handling System
Version: 2.0.0
Protocol: MCP v2025.08
"""

import asyncio
import ast
import hashlib
import json
import logging
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# MCP SDK imports (using FastMCP for enhanced capabilities)
try:
    from mcp import Server, Tool, Resource
    from mcp.types import TextContent, ImageContent, EmbeddedResource
    MCP_AVAILABLE = True
except ImportError:
    print("Installing MCP SDK...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp import Server, Tool, Resource
    from mcp.types import TextContent, ImageContent, EmbeddedResource
    MCP_AVAILABLE = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== DATA MODELS ====================

class ChunkStrategy(Enum):
    """Chunking strategies for different scenarios."""
    AST_BASED = "ast_based"
    SEMANTIC = "semantic"
    SLIDING_WINDOW = "sliding_window"
    FUNCTION_BASED = "function_based"
    CLASS_BASED = "class_based"
    SECTION_BASED = "section_based"
    HYBRID = "hybrid"
    QUANTUM = "quantum"  # Novel: Quantum superposition chunking

class ChunkGranularity(Enum):
    """Granularity levels for chunking."""
    ULTRA_FINE = 50    # 50 lines
    FINE = 100         # 100 lines
    MEDIUM = 500       # 500 lines
    COARSE = 1000      # 1000 lines
    ULTRA_COARSE = 5000  # 5000 lines
    ADAPTIVE = -1      # Adaptive based on content

@dataclass
class ChunkMetadata:
    """Metadata for each chunk."""
    id: str
    strategy: ChunkStrategy
    start_line: int
    end_line: int
    start_char: int
    end_char: int
    language: str
    ast_type: Optional[str] = None
    semantic_type: Optional[str] = None
    dependencies: List[str] = None
    imports: List[str] = None
    exports: List[str] = None
    complexity_score: float = 0.0
    token_count: int = 0
    hash: str = ""
    parent_chunk: Optional[str] = None
    child_chunks: List[str] = None
    context_before: str = ""
    context_after: str = ""
    summary: str = ""
    embeddings: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['strategy'] = self.strategy.value
        return data

@dataclass
class CodeChunk:
    """Represents a chunk of code."""
    metadata: ChunkMetadata
    content: str
    ast_node: Optional[Any] = None
    tokens: List[str] = None
    
    def get_size(self) -> int:
        """Get chunk size in bytes."""
        return len(self.content.encode('utf-8'))
    
    def get_lines(self) -> int:
        """Get number of lines."""
        return self.content.count('\n') + 1

# ==================== CHUNKING ENGINES ====================

class ASTChunker:
    """AST-based chunking using Tree-sitter."""
    
    def __init__(self):
        self.parser = Parser()
        self.parser.set_language(Language(tspython.language(), "python"))
        
    def chunk(self, code: str, max_chunk_size: int = 1000) -> List[CodeChunk]:
        """Chunk code based on AST."""
        tree = self.parser.parse(bytes(code, "utf8"))
        chunks = []
        
        # Traverse AST and create chunks
        def traverse(node, depth=0):
            if node.type in ['class_definition', 'function_definition']:
                chunk = self._create_chunk_from_node(node, code)
                if chunk.get_lines() <= max_chunk_size:
                    chunks.append(chunk)
                else:
                    # Recursively chunk large nodes
                    for child in node.children:
                        traverse(child, depth + 1)
            else:
                for child in node.children:
                    traverse(child, depth + 1)
        
        traverse(tree.root_node)
        return chunks
    
    def _create_chunk_from_node(self, node, code: str) -> CodeChunk:
        """Create chunk from AST node."""
        start_byte = node.start_byte
        end_byte = node.end_byte
        content = code[start_byte:end_byte]
        
        # Calculate line numbers
        lines_before = code[:start_byte].count('\n')
        lines_in_chunk = content.count('\n')
        
        metadata = ChunkMetadata(
            id=hashlib.md5(content.encode()).hexdigest()[:16],
            strategy=ChunkStrategy.AST_BASED,
            start_line=lines_before + 1,
            end_line=lines_before + lines_in_chunk + 1,
            start_char=start_byte,
            end_char=end_byte,
            language="python",
            ast_type=node.type,
            token_count=len(content.split()),
            hash=hashlib.sha256(content.encode()).hexdigest()
        )
        
        return CodeChunk(metadata=metadata, content=content, ast_node=node)

class SemanticChunker:
    """Semantic-based chunking using meaning and context."""
    
    def __init__(self):
        self.section_patterns = [
            re.compile(r'^#\s*={3,}.*={3,}\s*$', re.MULTILINE),
            re.compile(r'^#\s*-{3,}.*-{3,}\s*$', re.MULTILINE),
            re.compile(r'^#\s*#{2,}\s+\w+', re.MULTILINE),  # Markdown headers
        ]
        
    def chunk(self, code: str, max_chunk_size: int = 1000) -> List[CodeChunk]:
        """Chunk based on semantic boundaries."""
        chunks = []
        lines = code.splitlines()
        
        # Find semantic boundaries
        boundaries = self._find_boundaries(code)
        boundaries.append(len(lines))  # Add end of file
        
        start = 0
        for boundary in boundaries:
            if boundary - start > 0:
                chunk_lines = lines[start:boundary]
                chunk_content = '\n'.join(chunk_lines)
                
                metadata = ChunkMetadata(
                    id=hashlib.md5(chunk_content.encode()).hexdigest()[:16],
                    strategy=ChunkStrategy.SEMANTIC,
                    start_line=start + 1,
                    end_line=boundary,
                    start_char=len('\n'.join(lines[:start])),
                    end_char=len('\n'.join(lines[:boundary])),
                    language="python",
                    semantic_type=self._identify_semantic_type(chunk_content),
                    token_count=len(chunk_content.split()),
                    hash=hashlib.sha256(chunk_content.encode()).hexdigest()
                )
                
                chunks.append(CodeChunk(metadata=metadata, content=chunk_content))
                start = boundary
        
        return chunks
    
    def _find_boundaries(self, code: str) -> List[int]:
        """Find semantic boundaries in code."""
        boundaries = []
        lines = code.splitlines()
        
        for i, line in enumerate(lines):
            # Check for section markers
            for pattern in self.section_patterns:
                if pattern.match(line):
                    boundaries.append(i)
                    break
            
            # Check for class/function definitions
            if line.strip().startswith('class ') or line.strip().startswith('def '):
                boundaries.append(i)
        
        return sorted(list(set(boundaries)))
    
    def _identify_semantic_type(self, content: str) -> str:
        """Identify semantic type of chunk."""
        if 'import' in content[:100]:
            return "imports"
        elif 'class' in content[:100]:
            return "class_definition"
        elif 'def' in content[:100]:
            return "function_definition"
        elif re.search(r'^\s*#.*test', content, re.IGNORECASE):
            return "test"
        elif re.search(r'^\s*""".*"""', content, re.DOTALL):
            return "documentation"
        else:
            return "code_block"

class QuantumChunker:
    """Novel: Quantum superposition chunking - processes multiple chunking strategies simultaneously."""
    
    def __init__(self):
        self.ast_chunker = ASTChunker()
        self.semantic_chunker = SemanticChunker()
        
    def chunk(self, code: str, max_chunk_size: int = 1000) -> List[CodeChunk]:
        """Create quantum superposition of chunks."""
        # Get chunks from multiple strategies
        ast_chunks = self.ast_chunker.chunk(code, max_chunk_size)
        semantic_chunks = self.semantic_chunker.chunk(code, max_chunk_size)
        
        # Create superposition (combine and deduplicate)
        quantum_chunks = self._create_superposition(ast_chunks, semantic_chunks)
        
        # Collapse wavefunction (select optimal chunks)
        optimal_chunks = self._collapse_wavefunction(quantum_chunks)
        
        return optimal_chunks
    
    def _create_superposition(self, *chunk_lists) -> List[CodeChunk]:
        """Create superposition of chunks from multiple strategies."""
        all_chunks = []
        chunk_map = {}
        
        for chunks in chunk_lists:
            for chunk in chunks:
                key = (chunk.metadata.start_line, chunk.metadata.end_line)
                if key not in chunk_map:
                    chunk_map[key] = []
                chunk_map[key].append(chunk)
        
        # Merge overlapping chunks
        for key, chunks in chunk_map.items():
            if len(chunks) == 1:
                all_chunks.append(chunks[0])
            else:
                # Merge metadata from multiple strategies
                merged = self._merge_chunks(chunks)
                all_chunks.append(merged)
        
        return sorted(all_chunks, key=lambda c: c.metadata.start_line)
    
    def _merge_chunks(self, chunks: List[CodeChunk]) -> CodeChunk:
        """Merge multiple chunks into quantum chunk."""
        base_chunk = chunks[0]
        
        # Update metadata to reflect quantum nature
        base_chunk.metadata.strategy = ChunkStrategy.QUANTUM
        base_chunk.metadata.complexity_score = sum(
            c.metadata.complexity_score for c in chunks
        ) / len(chunks)
        
        return base_chunk
    
    def _collapse_wavefunction(self, chunks: List[CodeChunk]) -> List[CodeChunk]:
        """Collapse quantum chunks to optimal set."""
        # Use scoring algorithm to select best chunks
        scored_chunks = []
        for chunk in chunks:
            score = self._calculate_chunk_score(chunk)
            scored_chunks.append((score, chunk))
        
        # Sort by score and remove overlaps
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        final_chunks = []
        covered_lines = set()
        
        for score, chunk in scored_chunks:
            chunk_lines = set(range(chunk.metadata.start_line, chunk.metadata.end_line + 1))
            if not chunk_lines & covered_lines:
                final_chunks.append(chunk)
                covered_lines.update(chunk_lines)
        
        return sorted(final_chunks, key=lambda c: c.metadata.start_line)
    
    def _calculate_chunk_score(self, chunk: CodeChunk) -> float:
        """Calculate quality score for chunk."""
        score = 0.0
        
        # Prefer semantic boundaries
        if chunk.metadata.semantic_type:
            score += 10.0
        
        # Prefer AST nodes
        if chunk.metadata.ast_type:
            score += 10.0
        
        # Prefer medium-sized chunks
        lines = chunk.get_lines()
        if 50 <= lines <= 200:
            score += 5.0
        elif 200 < lines <= 500:
            score += 3.0
        
        # Penalize very small or very large chunks
        if lines < 10:
            score -= 5.0
        elif lines > 1000:
            score -= 10.0
        
        return score

# ==================== MCP SERVER ====================

class ChunkServer(Server):
    """MCP Server for intelligent file chunking."""
    
    def __init__(self):
        super().__init__("chunk-server")
        self.ast_chunker = ASTChunker()
        self.semantic_chunker = SemanticChunker()
        self.quantum_chunker = QuantumChunker()
        self.chunks_cache = {}
        
        # Register tools
        self.register_tools()
        
        # Register resources
        self.register_resources()
    
    def register_tools(self):
        """Register MCP tools."""
        
        @self.tool()
        async def chunk_file(
            file_path: str,
            strategy: str = "quantum",
            max_chunk_size: int = 1000,
            language: str = "python"
        ) -> Dict[str, Any]:
            """
            Chunk a file using specified strategy.
            
            Args:
                file_path: Path to file to chunk
                strategy: Chunking strategy (ast_based, semantic, quantum)
                max_chunk_size: Maximum lines per chunk
                language: Programming language
            
            Returns:
                Chunking results with metadata
            """
            try:
                # Read file
                file_path = Path(file_path)
                if not file_path.exists():
                    return {"error": f"File not found: {file_path}"}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Select chunker
                if strategy == "ast_based":
                    chunker = self.ast_chunker
                elif strategy == "semantic":
                    chunker = self.semantic_chunker
                else:  # quantum or default
                    chunker = self.quantum_chunker
                
                # Perform chunking
                chunks = chunker.chunk(content, max_chunk_size)
                
                # Cache results
                cache_key = f"{file_path}:{strategy}:{max_chunk_size}"
                self.chunks_cache[cache_key] = chunks
                
                # Return results
                return {
                    "file": str(file_path),
                    "strategy": strategy,
                    "total_chunks": len(chunks),
                    "total_lines": content.count('\n') + 1,
                    "chunks": [
                        {
                            "id": chunk.metadata.id,
                            "lines": f"{chunk.metadata.start_line}-{chunk.metadata.end_line}",
                            "size": chunk.get_size(),
                            "type": chunk.metadata.semantic_type or chunk.metadata.ast_type,
                            "preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
                        }
                        for chunk in chunks
                    ]
                }
                
            except Exception as e:
                logger.error(f"Error chunking file: {e}")
                return {"error": str(e)}
        
        @self.tool()
        async def get_chunk(
            file_path: str,
            chunk_id: str
        ) -> Dict[str, Any]:
            """
            Get specific chunk by ID.
            
            Args:
                file_path: Path to file
                chunk_id: Chunk identifier
            
            Returns:
                Chunk content and metadata
            """
            # Look for chunk in cache
            for key, chunks in self.chunks_cache.items():
                if key.startswith(str(file_path)):
                    for chunk in chunks:
                        if chunk.metadata.id == chunk_id:
                            return {
                                "id": chunk_id,
                                "content": chunk.content,
                                "metadata": chunk.metadata.to_dict()
                            }
            
            return {"error": f"Chunk not found: {chunk_id}"}
        
        @self.tool()
        async def get_chunk_context(
            file_path: str,
            chunk_id: str,
            context_lines: int = 50
        ) -> Dict[str, Any]:
            """
            Get chunk with surrounding context.
            
            Args:
                file_path: Path to file
                chunk_id: Chunk identifier
                context_lines: Lines of context before/after
            
            Returns:
                Chunk with context
            """
            # Find chunk
            chunk_result = await self.get_chunk(file_path, chunk_id)
            if "error" in chunk_result:
                return chunk_result
            
            # Read file for context
            file_path = Path(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            metadata = chunk_result["metadata"]
            start_line = metadata["start_line"] - 1  # Convert to 0-indexed
            end_line = metadata["end_line"]
            
            # Get context
            context_start = max(0, start_line - context_lines)
            context_end = min(len(lines), end_line + context_lines)
            
            return {
                "id": chunk_id,
                "content": chunk_result["content"],
                "context_before": ''.join(lines[context_start:start_line]),
                "context_after": ''.join(lines[end_line:context_end]),
                "metadata": metadata
            }
        
        @self.tool()
        async def analyze_chunks(
            file_path: str
        ) -> Dict[str, Any]:
            """
            Analyze chunk distribution and statistics.
            
            Args:
                file_path: Path to file
            
            Returns:
                Chunk analysis and statistics
            """
            # Find chunks in cache
            chunks = None
            for key, cached_chunks in self.chunks_cache.items():
                if key.startswith(str(file_path)):
                    chunks = cached_chunks
                    break
            
            if not chunks:
                # Chunk file first
                result = await self.chunk_file(file_path)
                if "error" in result:
                    return result
                
                # Get chunks from cache
                for key, cached_chunks in self.chunks_cache.items():
                    if key.startswith(str(file_path)):
                        chunks = cached_chunks
                        break
            
            # Analyze chunks
            total_lines = sum(c.get_lines() for c in chunks)
            total_size = sum(c.get_size() for c in chunks)
            
            type_distribution = {}
            for chunk in chunks:
                chunk_type = chunk.metadata.semantic_type or chunk.metadata.ast_type or "unknown"
                type_distribution[chunk_type] = type_distribution.get(chunk_type, 0) + 1
            
            size_distribution = {
                "small (<50 lines)": sum(1 for c in chunks if c.get_lines() < 50),
                "medium (50-200 lines)": sum(1 for c in chunks if 50 <= c.get_lines() <= 200),
                "large (200-500 lines)": sum(1 for c in chunks if 200 < c.get_lines() <= 500),
                "very large (>500 lines)": sum(1 for c in chunks if c.get_lines() > 500)
            }
            
            return {
                "file": str(file_path),
                "total_chunks": len(chunks),
                "total_lines": total_lines,
                "total_size": total_size,
                "average_chunk_size": total_size // len(chunks) if chunks else 0,
                "average_chunk_lines": total_lines // len(chunks) if chunks else 0,
                "type_distribution": type_distribution,
                "size_distribution": size_distribution,
                "strategies_used": list(set(c.metadata.strategy.value for c in chunks))
            }
    
    def register_resources(self):
        """Register MCP resources."""
        
        @self.resource("chunks/{file_path}")
        async def get_file_chunks(file_path: str) -> Resource:
            """Get all chunks for a file."""
            # Implementation here
            pass

# ==================== MAIN ====================

async def main():
    """Run ChunkServer."""
    server = ChunkServer()
    
    # Start server
    await server.start()
    
    logger.info("ChunkServer started successfully")
    logger.info("Ready to chunk massive files with quantum efficiency")
    
    # Keep server running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down ChunkServer")
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())