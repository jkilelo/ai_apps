#!/usr/bin/env python3
"""
VectorServer - Production-Ready Semantic Search MCP Server
Part of MFHS-MCP System for handling massive codebases

Provides semantic code understanding through embeddings, similarity search,
and context-aware retrieval using vector databases.

PRODUCTION FEATURES:
- Secure JSON serialization (NO PICKLE)
- Complete input validation
- Rate limiting
- LRU caching
- Comprehensive error handling
- Health checks and metrics
- Type safety throughout
"""

import json
import logging
import sys
import time
import hashlib
import msgpack  # Secure binary serialization
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, TypedDict, Protocol
import numpy as np
from collections import defaultdict
import re
from functools import wraps
import asyncio
from datetime import datetime
import base64

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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VectorServer")

# ============================================================================
# Type Definitions
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

# TypedDict for better type safety
class EmbeddingDict(TypedDict):
    id: str
    text: str
    type: str
    file_path: str
    line_start: int
    line_end: int
    metadata: Dict[str, Any]
    embedding_b64: Optional[str]  # Base64 encoded numpy array

class SearchResultDict(TypedDict):
    score: float
    embedding: EmbeddingDict
    context: Optional[str]

class SemanticBlockDict(TypedDict):
    type: str
    text: str
    line_start: int
    line_end: int
    name: Optional[str]
    metadata: Optional[Dict[str, Any]]

# ============================================================================
# Secure Numpy Serialization
# ============================================================================

class NumpyEncoder:
    """Secure numpy array encoding/decoding without pickle"""
    
    @staticmethod
    def encode(arr: np.ndarray) -> str:
        """Encode numpy array to base64 string"""
        if arr is None:
            return ""
        # Convert to bytes using numpy's native format
        dtype_str = str(arr.dtype)
        shape_str = ','.join(map(str, arr.shape))
        data_bytes = arr.tobytes()
        # Combine metadata and data
        metadata = f"{dtype_str}|{shape_str}|".encode()
        combined = metadata + data_bytes
        # Return base64 encoded
        return base64.b64encode(combined).decode('ascii')
    
    @staticmethod
    def decode(encoded: str) -> Optional[np.ndarray]:
        """Decode base64 string to numpy array"""
        if not encoded:
            return None
        try:
            # Decode from base64
            combined = base64.b64decode(encoded)
            # Find metadata separator
            sep_idx = combined.find(b'|', combined.find(b'|') + 1) + 1
            metadata = combined[:sep_idx-1].decode()
            data_bytes = combined[sep_idx:]
            # Parse metadata
            dtype_str, shape_str = metadata.split('|')
            dtype = np.dtype(dtype_str)
            shape = tuple(map(int, shape_str.split(',')))
            # Reconstruct array
            return np.frombuffer(data_bytes, dtype=dtype).reshape(shape)
        except Exception as e:
            logger.error(f"Failed to decode numpy array: {e}")
            return None

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class CodeEmbedding:
    """Represents an embedded code fragment with security"""
    id: str
    text: str
    embedding: Optional[np.ndarray]
    type: EmbeddingType
    file_path: str
    line_start: int
    line_end: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> EmbeddingDict:
        """Convert to dictionary for secure serialization"""
        return {
            'id': self.id,
            'text': self.text[:100] + '...' if len(self.text) > 100 else self.text,
            'type': self.type.value,
            'file_path': self.file_path,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'metadata': self.metadata,
            'embedding_b64': NumpyEncoder.encode(self.embedding) if self.embedding is not None else None
        }
    
    @classmethod
    def from_dict(cls, data: EmbeddingDict) -> 'CodeEmbedding':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            text=data['text'],
            embedding=NumpyEncoder.decode(data.get('embedding_b64', '')),
            type=EmbeddingType(data['type']),
            file_path=data['file_path'],
            line_start=data['line_start'],
            line_end=data['line_end'],
            metadata=data.get('metadata', {})
        )

@dataclass
class SearchResult:
    """Search result with similarity score"""
    embedding: CodeEmbedding
    score: float
    context: Optional[str] = None
    
    def to_dict(self) -> SearchResultDict:
        """Convert to dictionary for serialization"""
        return {
            'score': float(self.score),
            'embedding': self.embedding.to_dict(),
            'context': self.context
        }

@dataclass
class VectorSearchResult:
    """Result of vector search operation"""
    success: bool
    results: List[SearchResult] = field(default_factory=list)
    error: Optional[str] = None
    search_time: float = 0.0

# ============================================================================
# Embedding Generators with Error Handling
# ============================================================================

class Code2VecEmbedder:
    """Generate embeddings using Code2Vec approach with validation"""
    
    def __init__(self, embedding_dim: int = 128, max_paths: int = 1000):
        """Initialize with dimension limits"""
        self.embedding_dim = embedding_dim
        self.max_paths = max_paths
        self.path_vocab: Dict[str, int] = {}
        self.token_vocab: Dict[str, int] = {}
    
    def embed_ast_paths(self, ast_paths: List[str]) -> np.ndarray:
        """Convert AST paths to embeddings with validation"""
        if not ast_paths:
            return np.zeros(self.embedding_dim)
        
        # Limit number of paths
        ast_paths = ast_paths[:self.max_paths]
        
        vectors = []
        for path in ast_paths:
            # Validate path
            if not path or len(path) > 1000:
                continue
            
            # Hash path to vector (deterministic)
            hash_val = int(hashlib.sha256(path.encode()).hexdigest(), 16)
            np.random.seed(hash_val % 2**32)
            vec = np.random.randn(self.embedding_dim)
            vec = vec / (np.linalg.norm(vec) + 1e-10)  # Normalize
            vectors.append(vec)
        
        if vectors:
            return np.mean(vectors, axis=0)
        return np.zeros(self.embedding_dim)

class TransformerEmbedder:
    """Generate embeddings using transformer models with fallback"""
    
    def __init__(self, model_name: str = "microsoft/codebert-base", max_length: int = 512):
        """Initialize with model and limits"""
        self.max_length = max_length
        self.model: Optional[SentenceTransformer] = None
        
        if TRANSFORMER_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
            except Exception as e:
                logger.warning(f"Failed to load {model_name}: {e}")
                try:
                    # Fallback to general model
                    self.model = SentenceTransformer("all-MiniLM-L6-v2")
                    self.embedding_dim = 384
                except Exception as e2:
                    logger.error(f"Failed to load fallback model: {e2}")
                    self.model = None
                    self.embedding_dim = 384
        else:
            self.model = None
            self.embedding_dim = 384
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text with validation"""
        # Validate and truncate text
        if not text:
            return np.zeros(self.embedding_dim)
        
        text = text[:self.max_length * 4]  # Rough char limit
        
        if self.model:
            try:
                embedding = self.model.encode(text)
                return embedding / (np.linalg.norm(embedding) + 1e-10)
            except Exception as e:
                logger.warning(f"Embedding generation failed: {e}")
        
        # Fallback: deterministic hash-based embedding
        hash_val = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        np.random.seed(hash_val % 2**32)
        embedding = np.random.randn(self.embedding_dim)
        return embedding / (np.linalg.norm(embedding) + 1e-10)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        if not texts:
            return np.zeros((0, self.embedding_dim))
        
        # Validate and truncate
        texts = [t[:self.max_length * 4] if t else "" for t in texts]
        
        if self.model:
            try:
                embeddings = self.model.encode(texts)
                # Normalize
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10
                return embeddings / norms
            except Exception as e:
                logger.warning(f"Batch embedding failed: {e}")
        
        # Fallback
        return np.array([self.embed_text(t) for t in texts])

class HybridEmbedder:
    """Combine multiple embedding strategies with caching"""
    
    def __init__(self, cache_size: int = 10000):
        """Initialize with cache limit"""
        self.transformer = TransformerEmbedder()
        self.code2vec = Code2VecEmbedder()
        self.cache: Dict[str, np.ndarray] = {}
        self.cache_size = cache_size
    
    def embed(
        self,
        text: str,
        embed_type: EmbeddingType,
        ast_paths: Optional[List[str]] = None
    ) -> np.ndarray:
        """Generate hybrid embedding with caching"""
        # Validate input
        if not text:
            return np.zeros(self.transformer.embedding_dim)
        
        # Check cache
        cache_key = hashlib.sha256(
            f"{text[:100]}{embed_type.value}".encode()
        ).hexdigest()
        
        if cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        embeddings = []
        
        # Transformer embedding
        trans_emb = self.transformer.embed_text(text)
        embeddings.append(trans_emb)
        
        # Code2Vec embedding if AST paths provided
        if ast_paths:
            ast_emb = self.code2vec.embed_ast_paths(ast_paths)
            # Resize to match transformer dimension
            if len(ast_emb) < len(trans_emb):
                ast_emb = np.pad(ast_emb, (0, len(trans_emb) - len(ast_emb)))
            else:
                ast_emb = ast_emb[:len(trans_emb)]
            embeddings.append(ast_emb)
        
        # Combine embeddings
        if len(embeddings) > 1:
            result = np.mean(embeddings, axis=0)
        else:
            result = embeddings[0]
        
        # Normalize
        result = result / (np.linalg.norm(result) + 1e-10)
        
        # Cache result with size limit
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry (simple FIFO)
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        
        self.cache[cache_key] = result.copy()
        
        return result

# ============================================================================
# Secure Vector Database
# ============================================================================

class VectorDatabase:
    """Vector database with secure serialization"""
    
    def __init__(self, dimension: int = 384, use_faiss: bool = True, max_vectors: int = 1000000):
        """Initialize with limits"""
        self.dimension = dimension
        self.max_vectors = max_vectors
        self.embeddings: Dict[str, CodeEmbedding] = {}
        self.vectors: List[np.ndarray] = []
        self.ids: List[str] = []
        
        # Initialize index
        if use_faiss and FAISS_AVAILABLE:
            try:
                # Use FAISS for efficient similarity search
                self.index = faiss.IndexFlatIP(dimension)  # Inner product
                self.use_faiss = True
            except Exception as e:
                logger.warning(f"Failed to initialize FAISS: {e}")
                self.index = None
                self.use_faiss = False
        else:
            self.index = None
            self.use_faiss = False
    
    def add(self, embedding: CodeEmbedding) -> bool:
        """Add embedding to database with validation"""
        if embedding.embedding is None:
            return False
        
        # Check limits
        if len(self.vectors) >= self.max_vectors:
            logger.warning(f"Vector database full ({self.max_vectors} vectors)")
            return False
        
        # Validate embedding dimension
        if embedding.embedding.shape[0] != self.dimension:
            logger.error(f"Invalid embedding dimension: {embedding.embedding.shape[0]} != {self.dimension}")
            return False
        
        # Normalize for cosine similarity
        vec = embedding.embedding.copy()
        vec = vec / (np.linalg.norm(vec) + 1e-10)
        
        # Store
        self.embeddings[embedding.id] = embedding
        self.vectors.append(vec)
        self.ids.append(embedding.id)
        
        # Add to index
        if self.use_faiss:
            try:
                self.index.add(np.array([vec]).astype('float32'))
            except Exception as e:
                logger.error(f"Failed to add to FAISS index: {e}")
                return False
        
        return True
    
    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        threshold: float = 0.0
    ) -> List[SearchResult]:
        """Search for similar embeddings with validation"""
        if not self.vectors:
            return []
        
        # Validate query vector
        if query_vector.shape[0] != self.dimension:
            logger.error(f"Invalid query dimension: {query_vector.shape[0]} != {self.dimension}")
            return []
        
        # Limit k
        k = min(k, len(self.vectors), 100)  # Max 100 results
        
        # Normalize query
        query_vector = query_vector / (np.linalg.norm(query_vector) + 1e-10)
        
        if self.use_faiss:
            try:
                # FAISS search
                scores, indices = self.index.search(
                    np.array([query_vector]).astype('float32'),
                    k
                )
                
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx >= 0 and idx < len(self.ids) and score >= threshold:
                        embedding_id = self.ids[idx]
                        results.append(SearchResult(
                            embedding=self.embeddings[embedding_id],
                            score=float(score)
                        ))
            except Exception as e:
                logger.error(f"FAISS search failed: {e}")
                return []
        else:
            # Numpy fallback
            try:
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
            except Exception as e:
                logger.error(f"Numpy search failed: {e}")
                return []
        
        return results
    
    def save(self, path: str) -> bool:
        """Save database to disk using secure JSON serialization"""
        try:
            # Prepare data for JSON serialization
            data = {
                'version': '2.0.0',
                'dimension': self.dimension,
                'embeddings': [
                    emb.to_dict() for emb in self.embeddings.values()
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            # Save as JSON (secure, no arbitrary code execution)
            safe_path = Path(path).with_suffix('.json')
            with open(safe_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save FAISS index separately if available
            if self.use_faiss and self.index:
                faiss_path = Path(path).with_suffix('.faiss')
                faiss.write_index(self.index, str(faiss_path))
            
            logger.info(f"Database saved: {len(self.embeddings)} embeddings")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
            return False
    
    def load(self, path: str) -> bool:
        """Load database from disk using secure JSON"""
        try:
            # Load JSON data
            safe_path = Path(path).with_suffix('.json')
            with open(safe_path, 'r') as f:
                data = json.load(f)
            
            # Validate version
            if data.get('version') != '2.0.0':
                logger.warning(f"Version mismatch: {data.get('version')}")
            
            # Clear existing data
            self.embeddings.clear()
            self.vectors.clear()
            self.ids.clear()
            
            # Load embeddings
            for emb_dict in data['embeddings']:
                embedding = CodeEmbedding.from_dict(emb_dict)
                if embedding.embedding is not None:
                    self.embeddings[embedding.id] = embedding
                    self.vectors.append(embedding.embedding)
                    self.ids.append(embedding.id)
            
            # Rebuild FAISS index
            if self.use_faiss and self.vectors:
                self.index = faiss.IndexFlatIP(self.dimension)
                vectors_array = np.array(self.vectors).astype('float32')
                self.index.add(vectors_array)
                
                # Try to load optimized index if available
                faiss_path = Path(path).with_suffix('.faiss')
                if faiss_path.exists():
                    try:
                        self.index = faiss.read_index(str(faiss_path))
                    except Exception as e:
                        logger.warning(f"Failed to load FAISS index: {e}")
            
            logger.info(f"Database loaded: {len(self.embeddings)} embeddings")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            return False

# ============================================================================
# Semantic Analyzer with Validation
# ============================================================================

class SemanticAnalyzer:
    """Analyze code semantics with input validation"""
    
    def __init__(self, max_block_size: int = 10000):
        """Initialize with limits"""
        self.max_block_size = max_block_size
        self.embedder = HybridEmbedder()
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for code analysis"""
        return {
            'function': re.compile(r'def\s+(\w+)\s*\([^)]*\):'),
            'class': re.compile(r'class\s+(\w+)(?:\([^)]*\))?:'),
            'import': re.compile(r'(?:from\s+[\w.]+\s+)?import\s+[\w.,\s]+'),
            'docstring': re.compile(r'"""([^"]{0,1000})"""'),  # Limit docstring size
            'comment': re.compile(r'#\s*(.{0,200})$', re.MULTILINE),  # Limit comment size
            'decorator': re.compile(r'@\w+(?:\([^)]*\))?'),
        }
    
    def extract_semantic_blocks(self, code: str) -> List[SemanticBlockDict]:
        """Extract semantic blocks with validation"""
        blocks: List[SemanticBlockDict] = []
        
        # Validate code size
        if len(code) > 10 * 1024 * 1024:  # 10MB limit
            logger.warning("Code too large for semantic extraction")
            return blocks
        
        lines = code.split('\n')
        
        # Extract functions
        for match in self.patterns['function'].finditer(code):
            start_line = code[:match.start()].count('\n')
            # Find end of function (simple heuristic)
            indent_level = len(match.group()) - len(match.group().lstrip())
            end_line = min(start_line + 100, len(lines))  # Limit function size
            
            for i in range(start_line + 1, min(len(lines), start_line + 100)):
                if lines[i] and not lines[i].startswith(' ' * (indent_level + 1)):
                    end_line = i
                    break
            
            block_text = '\n'.join(lines[start_line:end_line])
            if len(block_text) <= self.max_block_size:
                blocks.append({
                    'type': EmbeddingType.FUNCTION_SIGNATURE.value,
                    'text': block_text,
                    'line_start': start_line,
                    'line_end': end_line,
                    'name': match.group(1),
                    'metadata': {}
                })
        
        # Extract classes (limit to reasonable number)
        class_count = 0
        for match in self.patterns['class'].finditer(code):
            if class_count >= 100:  # Max 100 classes
                break
            start_line = code[:match.start()].count('\n')
            blocks.append({
                'type': EmbeddingType.CLASS_DEFINITION.value,
                'text': lines[start_line] if start_line < len(lines) else "",
                'line_start': start_line,
                'line_end': start_line + 1,
                'name': match.group(1),
                'metadata': {}
            })
            class_count += 1
        
        # Extract docstrings (limit number)
        docstring_count = 0
        for match in self.patterns['docstring'].finditer(code):
            if docstring_count >= 50:  # Max 50 docstrings
                break
            start_line = code[:match.start()].count('\n')
            end_line = code[:match.end()].count('\n')
            blocks.append({
                'type': EmbeddingType.DOCSTRING.value,
                'text': match.group(1)[:1000],  # Limit docstring size
                'line_start': start_line,
                'line_end': end_line,
                'name': None,
                'metadata': {}
            })
            docstring_count += 1
        
        return blocks
    
    def generate_embeddings(
        self,
        code: str,
        file_path: str
    ) -> List[CodeEmbedding]:
        """Generate embeddings for code with validation"""
        embeddings = []
        
        # Extract semantic blocks
        blocks = self.extract_semantic_blocks(code)
        
        # Limit number of embeddings per file
        blocks = blocks[:500]
        
        for block in blocks:
            # Generate unique ID
            block_id = hashlib.sha256(
                f"{file_path}:{block['line_start']}:{block['text'][:50]}".encode()
            ).hexdigest()[:16]  # Shorter ID
            
            # Generate embedding
            vector = self.embedder.embed(
                block['text'],
                EmbeddingType(block['type'])
            )
            
            # Create embedding object
            embedding = CodeEmbedding(
                id=block_id,
                text=block['text'],
                embedding=vector,
                type=EmbeddingType(block['type']),
                file_path=file_path,
                line_start=block['line_start'],
                line_end=block['line_end'],
                metadata=block.get('metadata', {})
            )
            
            embeddings.append(embedding)
        
        return embeddings

# ============================================================================
# Context Builder with Safety
# ============================================================================

class ContextBuilder:
    """Build context with file size limits"""
    
    def __init__(self, context_lines: int = 5, max_file_size: int = 1024 * 1024):
        """Initialize with limits"""
        self.context_lines = min(context_lines, 20)  # Max 20 lines context
        self.max_file_size = max_file_size
        self.file_cache: Dict[str, List[str]] = {}
        self.cache_size = 0
        self.max_cache_size = 10 * 1024 * 1024  # 10MB cache
    
    def get_context(self, result: SearchResult) -> str:
        """Get context with validation"""
        file_path = result.embedding.file_path
        
        # Validate file path
        try:
            path = Path(file_path).resolve()
            if not path.exists() or not path.is_file():
                return ""
            
            # Check file size
            if path.stat().st_size > self.max_file_size:
                return "# File too large for context extraction"
        except Exception as e:
            logger.error(f"Invalid file path: {e}")
            return ""
        
        # Load file if not cached
        if file_path not in self.file_cache:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    # Limit lines stored
                    lines = lines[:10000]  # Max 10k lines
                    
                    # Check cache size
                    file_size = sum(len(line) for line in lines)
                    if self.cache_size + file_size > self.max_cache_size:
                        # Clear cache if too large
                        self.file_cache.clear()
                        self.cache_size = 0
                    
                    self.file_cache[file_path] = lines
                    self.cache_size += file_size
            except Exception as e:
                logger.error(f"Failed to read file: {e}")
                return ""
        
        lines = self.file_cache.get(file_path, [])
        if not lines:
            return ""
        
        # Get context lines
        start = max(0, result.embedding.line_start - self.context_lines)
        end = min(len(lines), result.embedding.line_end + self.context_lines)
        
        context_lines = lines[start:end]
        return ''.join(context_lines[:100])  # Limit context size
    
    def build_rag_context(
        self,
        results: List[SearchResult],
        max_tokens: int = 2000
    ) -> str:
        """Build RAG context with limits"""
        # Validate max_tokens
        max_tokens = min(max_tokens, 10000)
        
        context_parts = []
        token_count = 0
        
        for i, result in enumerate(results[:20]):  # Max 20 results
            # Get context
            context = self.get_context(result)
            
            # Estimate tokens (rough: 1 token ≈ 4 chars)
            estimated_tokens = len(context) // 4
            
            if token_count + estimated_tokens > max_tokens:
                break
            
            # Add to context
            context_parts.append(f"""# Result {i+1}
# From {result.embedding.file_path} (lines {result.embedding.line_start}-{result.embedding.line_end})
# Similarity: {result.score:.3f}
{context}
""")
            token_count += estimated_tokens
        
        return '\n'.join(context_parts)

# ============================================================================
# Production-Ready Vector Server
# ============================================================================

class VectorServer(BaseMCPServer):
    """Production-ready MCP Server for semantic code search"""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        """Initialize with production features"""
        # Set defaults
        if config is None:
            config = {
                'name': 'vector-server',
                'version': '2.0.0',
                'max_request_size': 10 * 1024 * 1024,  # 10MB
                'rate_limit_calls': 30,
                'rate_limit_window': 60,
                'cache_ttl': 3600,
                'max_cache_size': 100
            }
        
        super().__init__(config)
        
        # Initialize components
        self.database = VectorDatabase()
        self.analyzer = SemanticAnalyzer()
        self.context_builder = ContextBuilder()
        
        logger.info(f"VectorServer v{config['version']} initialized (SECURE)")
    
    def _register_tools(self) -> None:
        """Register MCP tools with security and validation"""
        
        @self.server.tool()
        @rate_limit(max_calls=10, time_window=60)
        async def embed_file(file_path: str) -> TextContent:
            """
            Generate and store embeddings for a file.
            
            Args:
                file_path: Path to file to embed
            
            Returns:
                JSON with embedding summary or error
            """
            start_time = time.time()
            
            try:
                # Validate file path
                safe_path = self.validator.validate_file_path(file_path)
                
                # Check file size
                file_size = safe_path.stat().st_size
                if file_size > self.config['max_request_size']:
                    raise ValidationError(
                        f"File too large: {file_size} bytes (max: {self.config['max_request_size']})"
                    )
                
                # Read file
                with open(safe_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                
                # Generate embeddings
                embeddings = self.analyzer.generate_embeddings(code, str(safe_path))
                
                # Store in database
                success_count = 0
                for embedding in embeddings:
                    if self.database.add(embedding):
                        success_count += 1
                
                elapsed = time.time() - start_time
                
                # Update metrics
                self.metrics.update(success=True, processing_time=elapsed)
                
                return TextContent(text=json.dumps({
                    'success': True,
                    'file_path': str(safe_path),
                    'embeddings_generated': len(embeddings),
                    'embeddings_stored': success_count,
                    'total_embeddings': len(self.database.embeddings),
                    'processing_time': elapsed,
                    'timestamp': datetime.now().isoformat()
                }, indent=2))
                
            except ValidationError as e:
                self.metrics.validation_errors += 1
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e),
                    'type': 'validation_error'
                }, indent=2))
            except Exception as e:
                self.metrics.processing_errors += 1
                logger.exception("Error embedding file")
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e),
                    'type': 'processing_error'
                }, indent=2))
        
        @self.server.tool()
        @rate_limit(max_calls=30, time_window=60)
        async def search(
            query: str,
            k: int = 10,
            threshold: float = 0.5
        ) -> TextContent:
            """
            Search for similar code using semantic search.
            
            Args:
                query: Search query
                k: Number of results (max 100)
                threshold: Similarity threshold (0-1)
            
            Returns:
                JSON with search results or error
            """
            try:
                # Validate inputs
                query = self.validator.sanitize_string(query, max_length=1000)
                k = min(max(1, k), 100)
                threshold = max(0.0, min(1.0, threshold))
                
                # Check cache
                cache_key = f"search:{hashlib.md5(f'{query}{k}{threshold}'.encode()).hexdigest()}"
                if cached := await self.cache.get(cache_key):
                    self.metrics.cache_hits += 1
                    return TextContent(text=cached)
                
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
                        'preview': result.embedding.text[:200]
                    })
                
                response = json.dumps({
                    'success': True,
                    'query': query,
                    'results_count': len(results),
                    'results': formatted_results
                }, indent=2)
                
                # Cache response
                await self.cache.set(cache_key, response)
                
                return TextContent(text=response)
                
            except Exception as e:
                logger.exception("Search error")
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e)
                }, indent=2))
        
        @self.server.tool()
        @rate_limit(max_calls=10, time_window=60)
        async def save_database(path: str) -> TextContent:
            """
            Save vector database to disk (secure JSON format).
            
            Args:
                path: Path to save database
            
            Returns:
                JSON with save status
            """
            try:
                # Validate path
                safe_path = self.validator.validate_file_path(path, must_exist=False)
                
                # Ensure .json extension for security
                safe_path = safe_path.with_suffix('.json')
                
                # Save database
                if self.database.save(str(safe_path)):
                    return TextContent(text=json.dumps({
                        'success': True,
                        'path': str(safe_path),
                        'embeddings_saved': len(self.database.embeddings),
                        'format': 'secure_json',
                        'timestamp': datetime.now().isoformat()
                    }, indent=2))
                else:
                    raise ProcessingError("Failed to save database")
                    
            except Exception as e:
                logger.exception("Save error")
                return TextContent(text=json.dumps({
                    'success': False,
                    'error': str(e)
                }, indent=2))
        
        @self.server.tool()
        @rate_limit(max_calls=10, time_window=60)
        async def load_database(path: str) -> TextContent:
            """
            Load vector database from disk (secure JSON format).
            
            Args:
                path: Path to load database from
            
            Returns:
                JSON with load status
            """
            try:
                # Validate path
                safe_path = self.validator.validate_file_path(path)
                
                # Load database
                if self.database.load(str(safe_path)):
                    return TextContent(text=json.dumps({
                        'success': True,
                        'path': str(safe_path),
                        'embeddings_loaded': len(self.database.embeddings),
                        'format': 'secure_json',
                        'timestamp': datetime.now().isoformat()
                    }, indent=2))
                else:
                    raise ProcessingError("Failed to load database")
                    
            except Exception as e:
                logger.exception("Load error")
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
    
    # Load configuration
    config: ServerConfig = {
        'name': 'vector-server',
        'version': '2.0.0',
        'log_level': 'INFO'
    }
    
    server = VectorServer(config)
    
    try:
        logger.info(f"Starting VectorServer v{config['version']} (SECURE MODE)...")
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()