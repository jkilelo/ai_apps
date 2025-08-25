#!/usr/bin/env python3
"""
VectorServer - Semantic Search MCP Server
Part of MFHS-MCP System for handling massive codebases

Provides semantic code understanding through embeddings, similarity search,
and context-aware retrieval using vector databases.
"""

import json
import logging
import sys
import time
import hashlib
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from collections import defaultdict
import pickle
import re

# MCP Server SDK imports
try:
    from mcp import Server, Tool
    from mcp.types import TextContent, Resource
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Vector database imports (with fallbacks)
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available. Install with: pip install faiss-cpu")

try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMER_AVAILABLE = True
except ImportError:
    TRANSFORMER_AVAILABLE = False
    logging.warning("SentenceTransformers not available. Install with: pip install sentence-transformers")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VectorServer")

# ============================================================================
# Data Models
# ============================================================================

class EmbeddingType(Enum):
    """Types of embeddings"""
    CODE = "code"
    COMMENT = "comment"
    DOCSTRING = "docstring"
    FUNCTION_SIGNATURE = "function_signature"
    CLASS_DEFINITION = "class_definition"
    SEMANTIC_BLOCK = "semantic_block"
    AST_PATH = "ast_path"

@dataclass
class CodeEmbedding:
    """Represents an embedded code fragment"""
    id: str
    text: str
    embedding: Optional[np.ndarray]
    type: EmbeddingType
    file_path: str
    line_start: int
    line_end: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'text': self.text[:100] + '...' if len(self.text) > 100 else self.text,
            'type': self.type.value,
            'file_path': self.file_path,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'metadata': self.metadata
        }

@dataclass
class SearchResult:
    """Search result with similarity score"""
    embedding: CodeEmbedding
    score: float
    context: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'score': float(self.score),
            'embedding': self.embedding.to_dict(),
            'context': self.context
        }

# ============================================================================
# Embedding Generators
# ============================================================================

class Code2VecEmbedder:
    """Generate embeddings using Code2Vec approach"""
    
    def __init__(self):
        self.path_vocab = {}
        self.token_vocab = {}
        self.embedding_dim = 128
    
    def embed_ast_paths(self, ast_paths: List[str]) -> np.ndarray:
        """Convert AST paths to embeddings"""
        # Simple implementation - in production would use trained model
        vectors = []
        for path in ast_paths:
            # Hash path to vector
            hash_val = int(hashlib.md5(path.encode()).hexdigest(), 16)
            np.random.seed(hash_val % 2**32)
            vec = np.random.randn(self.embedding_dim)
            vectors.append(vec)
        
        if vectors:
            return np.mean(vectors, axis=0)
        return np.zeros(self.embedding_dim)

class TransformerEmbedder:
    """Generate embeddings using transformer models"""
    
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        if TRANSFORMER_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
            except:
                # Fallback to general model
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                self.embedding_dim = 384
        else:
            self.model = None
            self.embedding_dim = 384
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if self.model:
            return self.model.encode(text)
        else:
            # Fallback: simple hash-based embedding
            hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
            np.random.seed(hash_val % 2**32)
            return np.random.randn(self.embedding_dim)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        if self.model:
            return self.model.encode(texts)
        else:
            return np.array([self.embed_text(t) for t in texts])

class HybridEmbedder:
    """Combine multiple embedding strategies"""
    
    def __init__(self):
        self.transformer = TransformerEmbedder()
        self.code2vec = Code2VecEmbedder()
        self.cache = {}
    
    def embed(self, text: str, type: EmbeddingType, ast_paths: Optional[List[str]] = None) -> np.ndarray:
        """Generate hybrid embedding"""
        
        # Check cache
        cache_key = hashlib.md5(f"{text}{type.value}".encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        embeddings = []
        
        # Transformer embedding
        trans_emb = self.transformer.embed_text(text)
        embeddings.append(trans_emb)
        
        # Code2Vec embedding if AST paths provided
        if ast_paths:
            ast_emb = self.code2vec.embed_ast_paths(ast_paths)
            # Resize to match transformer dimension
            ast_emb_resized = np.pad(ast_emb, (0, len(trans_emb) - len(ast_emb)))[:len(trans_emb)]
            embeddings.append(ast_emb_resized)
        
        # Combine embeddings
        if len(embeddings) > 1:
            result = np.mean(embeddings, axis=0)
        else:
            result = embeddings[0]
        
        # Cache result
        self.cache[cache_key] = result
        
        return result

# ============================================================================
# Vector Database
# ============================================================================

class VectorDatabase:
    """Vector database for similarity search"""
    
    def __init__(self, dimension: int = 384, use_faiss: bool = True):
        self.dimension = dimension
        self.embeddings: Dict[str, CodeEmbedding] = {}
        self.vectors: List[np.ndarray] = []
        self.ids: List[str] = []
        
        # Initialize index
        if use_faiss and FAISS_AVAILABLE:
            # Use FAISS for efficient similarity search
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            self.use_faiss = True
        else:
            # Fallback to numpy
            self.index = None
            self.use_faiss = False
    
    def add(self, embedding: CodeEmbedding):
        """Add embedding to database"""
        if embedding.embedding is None:
            return
        
        # Normalize for cosine similarity
        vec = embedding.embedding
        vec = vec / (np.linalg.norm(vec) + 1e-10)
        
        # Store
        self.embeddings[embedding.id] = embedding
        self.vectors.append(vec)
        self.ids.append(embedding.id)
        
        # Add to index
        if self.use_faiss:
            self.index.add(np.array([vec]).astype('float32'))
    
    def search(self, query_vector: np.ndarray, k: int = 10, threshold: float = 0.0) -> List[SearchResult]:
        """Search for similar embeddings"""
        if not self.vectors:
            return []
        
        # Normalize query
        query_vector = query_vector / (np.linalg.norm(query_vector) + 1e-10)
        
        if self.use_faiss:
            # FAISS search
            scores, indices = self.index.search(
                np.array([query_vector]).astype('float32'), 
                min(k, len(self.vectors))
            )
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and score >= threshold:
                    embedding_id = self.ids[idx]
                    results.append(SearchResult(
                        embedding=self.embeddings[embedding_id],
                        score=float(score)
                    ))
        else:
            # Numpy fallback
            vectors_array = np.array(self.vectors)
            scores = np.dot(vectors_array, query_vector)
            
            # Get top k
            top_indices = np.argsort(scores)[::-1][:k]
            
            results = []
            for idx in top_indices:
                score = scores[idx]
                if score >= threshold:
                    embedding_id = self.ids[idx]
                    results.append(SearchResult(
                        embedding=self.embeddings[embedding_id],
                        score=float(score)
                    ))
        
        return results
    
    def save(self, path: str):
        """Save database to disk"""
        data = {
            'embeddings': self.embeddings,
            'vectors': self.vectors,
            'ids': self.ids,
            'dimension': self.dimension
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        if self.use_faiss:
            faiss.write_index(self.index, f"{path}.faiss")
    
    def load(self, path: str):
        """Load database from disk"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.embeddings = data['embeddings']
        self.vectors = data['vectors']
        self.ids = data['ids']
        self.dimension = data['dimension']
        
        if self.use_faiss and Path(f"{path}.faiss").exists():
            self.index = faiss.read_index(f"{path}.faiss")

# ============================================================================
# Semantic Analyzer
# ============================================================================

class SemanticAnalyzer:
    """Analyze code semantics for better embeddings"""
    
    def __init__(self):
        self.embedder = HybridEmbedder()
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for code analysis"""
        return {
            'function': re.compile(r'def\s+(\w+)\s*\([^)]*\):'),
            'class': re.compile(r'class\s+(\w+)(?:\([^)]*\))?:'),
            'import': re.compile(r'(?:from\s+[\w.]+\s+)?import\s+[\w.,\s]+'),
            'docstring': re.compile(r'"""([^"]*)"""'),
            'comment': re.compile(r'#\s*(.*)$', re.MULTILINE),
            'decorator': re.compile(r'@\w+(?:\([^)]*\))?'),
        }
    
    def extract_semantic_blocks(self, code: str) -> List[Dict]:
        """Extract semantic blocks from code"""
        blocks = []
        lines = code.split('\n')
        
        # Extract functions
        for match in self.patterns['function'].finditer(code):
            start_line = code[:match.start()].count('\n')
            # Find end of function (simple heuristic)
            indent_level = len(match.group()) - len(match.group().lstrip())
            end_line = start_line + 1
            
            for i in range(start_line + 1, len(lines)):
                if lines[i] and not lines[i].startswith(' ' * (indent_level + 1)):
                    end_line = i
                    break
            
            blocks.append({
                'type': EmbeddingType.FUNCTION_SIGNATURE,
                'text': '\n'.join(lines[start_line:end_line]),
                'line_start': start_line,
                'line_end': end_line,
                'name': match.group(1)
            })
        
        # Extract classes
        for match in self.patterns['class'].finditer(code):
            start_line = code[:match.start()].count('\n')
            blocks.append({
                'type': EmbeddingType.CLASS_DEFINITION,
                'text': lines[start_line],
                'line_start': start_line,
                'line_end': start_line + 1,
                'name': match.group(1)
            })
        
        # Extract docstrings
        for match in self.patterns['docstring'].finditer(code):
            start_line = code[:match.start()].count('\n')
            end_line = code[:match.end()].count('\n')
            blocks.append({
                'type': EmbeddingType.DOCSTRING,
                'text': match.group(1),
                'line_start': start_line,
                'line_end': end_line
            })
        
        return blocks
    
    def generate_embeddings(self, code: str, file_path: str) -> List[CodeEmbedding]:
        """Generate embeddings for code"""
        embeddings = []
        
        # Extract semantic blocks
        blocks = self.extract_semantic_blocks(code)
        
        for block in blocks:
            # Generate unique ID
            block_id = hashlib.md5(
                f"{file_path}:{block['line_start']}:{block['text'][:50]}".encode()
            ).hexdigest()
            
            # Generate embedding
            vector = self.embedder.embed(
                block['text'],
                block['type']
            )
            
            # Create embedding object
            embedding = CodeEmbedding(
                id=block_id,
                text=block['text'],
                embedding=vector,
                type=block['type'],
                file_path=file_path,
                line_start=block['line_start'],
                line_end=block['line_end'],
                metadata=block.get('metadata', {})
            )
            
            embeddings.append(embedding)
        
        return embeddings

# ============================================================================
# Context Builder
# ============================================================================

class ContextBuilder:
    """Build context around search results"""
    
    def __init__(self, context_lines: int = 5):
        self.context_lines = context_lines
        self.file_cache = {}
    
    def get_context(self, result: SearchResult) -> str:
        """Get context around search result"""
        file_path = result.embedding.file_path
        
        # Load file if not cached
        if file_path not in self.file_cache:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.file_cache[file_path] = f.readlines()
            except:
                return ""
        
        lines = self.file_cache.get(file_path, [])
        if not lines:
            return ""
        
        # Get context lines
        start = max(0, result.embedding.line_start - self.context_lines)
        end = min(len(lines), result.embedding.line_end + self.context_lines)
        
        context_lines = lines[start:end]
        return ''.join(context_lines)
    
    def build_rag_context(self, results: List[SearchResult], max_tokens: int = 2000) -> str:
        """Build RAG context from search results"""
        context_parts = []
        token_count = 0
        
        for result in results:
            # Get context
            context = self.get_context(result)
            
            # Estimate tokens (rough: 1 token ≈ 4 chars)
            estimated_tokens = len(context) // 4
            
            if token_count + estimated_tokens > max_tokens:
                break
            
            # Add to context
            context_parts.append(f"""
# From {result.embedding.file_path} (lines {result.embedding.line_start}-{result.embedding.line_end})
# Similarity: {result.score:.3f}
{context}
""")
            token_count += estimated_tokens
        
        return '\n'.join(context_parts)

# ============================================================================
# MCP Server Implementation
# ============================================================================

class VectorMCPServer:
    """MCP Server for semantic code search"""
    
    def __init__(self):
        self.server = Server("vector-server")
        self.database = VectorDatabase()
        self.analyzer = SemanticAnalyzer()
        self.context_builder = ContextBuilder()
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.server.tool()
        async def embed_file(file_path: str) -> TextContent:
            """Generate and store embeddings for a file"""
            try:
                # Read file
                path = Path(file_path)
                if not path.exists():
                    return TextContent(text=json.dumps({
                        'error': f'File not found: {file_path}'
                    }))
                
                with open(path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Generate embeddings
                start_time = time.time()
                embeddings = self.analyzer.generate_embeddings(code, file_path)
                
                # Store in database
                for embedding in embeddings:
                    self.database.add(embedding)
                
                elapsed = time.time() - start_time
                
                return TextContent(text=json.dumps({
                    'file_path': file_path,
                    'embeddings_generated': len(embeddings),
                    'total_embeddings': len(self.database.embeddings),
                    'processing_time': elapsed,
                    'status': 'success'
                }, indent=2))
                
            except Exception as e:
                logger.error(f"Error embedding file: {e}")
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def search(query: str, k: int = 10, threshold: float = 0.5) -> TextContent:
            """Search for similar code using semantic search"""
            try:
                # Generate query embedding
                query_vector = self.analyzer.embedder.embed(
                    query,
                    EmbeddingType.CODE
                )
                
                # Search
                results = self.database.search(query_vector, k, threshold)
                
                # Format results
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        'score': result.score,
                        'file': result.embedding.file_path,
                        'lines': f"{result.embedding.line_start}-{result.embedding.line_end}",
                        'type': result.embedding.type.value,
                        'preview': result.embedding.text[:200] + '...' if len(result.embedding.text) > 200 else result.embedding.text
                    })
                
                return TextContent(text=json.dumps({
                    'query': query,
                    'results_count': len(results),
                    'results': formatted_results
                }, indent=2))
                
            except Exception as e:
                logger.error(f"Search error: {e}")
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def search_with_context(query: str, k: int = 5, max_context_tokens: int = 2000) -> TextContent:
            """Search and return results with context for RAG"""
            try:
                # Generate query embedding
                query_vector = self.analyzer.embedder.embed(
                    query,
                    EmbeddingType.CODE
                )
                
                # Search
                results = self.database.search(query_vector, k, threshold=0.3)
                
                # Build RAG context
                context = self.context_builder.build_rag_context(results, max_context_tokens)
                
                return TextContent(text=json.dumps({
                    'query': query,
                    'results_count': len(results),
                    'context': context,
                    'sources': [
                        {
                            'file': r.embedding.file_path,
                            'lines': f"{r.embedding.line_start}-{r.embedding.line_end}",
                            'score': r.score
                        }
                        for r in results
                    ]
                }, indent=2))
                
            except Exception as e:
                logger.error(f"Search error: {e}")
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def find_similar(file_path: str, line_start: int, line_end: int, k: int = 5) -> TextContent:
            """Find code similar to a specific section"""
            try:
                # Read the specific section
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if line_start < 1 or line_end > len(lines):
                    return TextContent(text=json.dumps({
                        'error': 'Invalid line range'
                    }))
                
                # Extract text
                text = ''.join(lines[line_start-1:line_end])
                
                # Generate embedding
                query_vector = self.analyzer.embedder.embed(
                    text,
                    EmbeddingType.CODE
                )
                
                # Search
                results = self.database.search(query_vector, k + 1)  # +1 to exclude self
                
                # Filter out self
                results = [r for r in results if not (
                    r.embedding.file_path == file_path and
                    r.embedding.line_start == line_start - 1
                )][:k]
                
                # Format results
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        'score': result.score,
                        'file': result.embedding.file_path,
                        'lines': f"{result.embedding.line_start}-{result.embedding.line_end}",
                        'type': result.embedding.type.value,
                        'preview': result.embedding.text[:200] + '...'
                    })
                
                return TextContent(text=json.dumps({
                    'source': {
                        'file': file_path,
                        'lines': f"{line_start}-{line_end}"
                    },
                    'similar_code': formatted_results
                }, indent=2))
                
            except Exception as e:
                logger.error(f"Error finding similar code: {e}")
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def save_database(path: str) -> TextContent:
            """Save vector database to disk"""
            try:
                self.database.save(path)
                
                return TextContent(text=json.dumps({
                    'path': path,
                    'embeddings_saved': len(self.database.embeddings),
                    'status': 'success'
                }))
                
            except Exception as e:
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def load_database(path: str) -> TextContent:
            """Load vector database from disk"""
            try:
                self.database.load(path)
                
                return TextContent(text=json.dumps({
                    'path': path,
                    'embeddings_loaded': len(self.database.embeddings),
                    'status': 'success'
                }))
                
            except Exception as e:
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        logger.info("Starting VectorServer MCP server...")
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
    
    server = VectorMCPServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()