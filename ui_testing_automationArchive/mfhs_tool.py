#!/usr/bin/env python3
"""
MEGA FILE HANDLING SYSTEM (MFHS) - Practical Implementation
Handles 10,000+ line single files with limited context windows
Version: 1.0.0
Author: Senior Software Architect (30+ years experience)
"""

import ast
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import textwrap
from enum import Enum

# ==================== DATA MODELS ====================

class ChunkType(Enum):
    """Types of code chunks."""
    IMPORTS = "imports"
    CONSTANTS = "constants"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    SECTION = "section"
    MAIN = "main"
    UNKNOWN = "unknown"

@dataclass
class CodeChunk:
    """Represents a chunk of code."""
    id: str
    type: ChunkType
    name: str
    start_line: int
    end_line: int
    content: str = ""
    summary: str = ""
    dependencies: List[str] = field(default_factory=list)
    size_bytes: int = 0
    size_tokens: int = 0  # Approximate
    
    def __hash__(self):
        return hash(self.id)

@dataclass
class FileIndex:
    """Index of a large file's structure."""
    file_path: str
    total_lines: int
    total_bytes: int
    chunks: Dict[str, CodeChunk] = field(default_factory=dict)
    imports: List[CodeChunk] = field(default_factory=list)
    classes: Dict[str, List[CodeChunk]] = field(default_factory=dict)  # Class -> methods
    functions: List[CodeChunk] = field(default_factory=list)
    sections: List[CodeChunk] = field(default_factory=list)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        data = {
            'file_path': self.file_path,
            'total_lines': self.total_lines,
            'total_bytes': self.total_bytes,
            'chunk_count': len(self.chunks),
            'class_count': len(self.classes),
            'function_count': len(self.functions),
            'chunks': {k: asdict(v) for k, v in self.chunks.items()}
        }
        return json.dumps(data, indent=2)
    
    def get_structure_summary(self) -> str:
        """Get a concise structure summary."""
        lines = [
            f"File: {self.file_path}",
            f"Total: {self.total_lines} lines, {self.total_bytes:,} bytes",
            f"Structure:",
            f"  - Imports: {len(self.imports)} chunks",
            f"  - Classes: {len(self.classes)}",
            f"  - Functions: {len(self.functions)}",
            f"  - Sections: {len(self.sections)}",
            f"  - Total chunks: {len(self.chunks)}"
        ]
        
        # Add class details
        if self.classes:
            lines.append("\nClasses:")
            for class_name, methods in self.classes.items():
                lines.append(f"  - {class_name}: {len(methods)} methods")
        
        return "\n".join(lines)

# ==================== CORE ANALYZER ====================

class FileAnalyzer:
    """Analyzes large Python files and creates structural index."""
    
    def __init__(self):
        self.section_pattern = re.compile(r'^#\s*={3,}.*={3,}\s*$', re.MULTILINE)
        self.class_pattern = re.compile(r'^class\s+(\w+)', re.MULTILINE)
        self.function_pattern = re.compile(r'^def\s+(\w+)', re.MULTILINE)
        
    def analyze_file(self, file_path: str) -> FileIndex:
        """Analyze file and create index."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        index = FileIndex(
            file_path=str(file_path),
            total_lines=len(lines),
            total_bytes=len(content.encode('utf-8'))
        )
        
        # Parse AST for structure
        try:
            tree = ast.parse(content)
            self._analyze_ast(tree, lines, index)
        except SyntaxError as e:
            print(f"Warning: Could not parse AST: {e}")
            # Fall back to regex-based analysis
            self._analyze_with_regex(lines, index)
        
        # Find sections marked with comments
        self._find_sections(lines, index)
        
        # Build dependency graph
        self._build_dependencies(index)
        
        return index
    
    def _analyze_ast(self, tree: ast.AST, lines: List[str], index: FileIndex) -> None:
        """Analyze using AST."""
        # Find imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                chunk = self._create_chunk_from_node(node, lines, ChunkType.IMPORTS, "imports")
                index.imports.append(chunk)
                index.chunks[chunk.id] = chunk
        
        # Find classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_chunk = self._create_chunk_from_node(node, lines, ChunkType.CLASS, node.name)
                index.chunks[class_chunk.id] = class_chunk
                
                # Find methods within class
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_chunk = self._create_chunk_from_node(
                            item, lines, ChunkType.METHOD, f"{node.name}.{item.name}"
                        )
                        index.chunks[method_chunk.id] = method_chunk
                        methods.append(method_chunk)
                
                index.classes[node.name] = methods
                
            elif isinstance(node, ast.FunctionDef):
                # Check if it's a top-level function (not a method)
                is_method = False
                for other_node in ast.walk(tree):
                    if isinstance(other_node, ast.ClassDef):
                        if hasattr(other_node, 'body') and isinstance(other_node.body, list):
                            if node in other_node.body:
                                is_method = True
                                break
                
                if not is_method:
                    func_chunk = self._create_chunk_from_node(node, lines, ChunkType.FUNCTION, node.name)
                    index.functions.append(func_chunk)
                    index.chunks[func_chunk.id] = func_chunk
    
    def _create_chunk_from_node(self, node: ast.AST, lines: List[str], 
                                chunk_type: ChunkType, name: str) -> CodeChunk:
        """Create chunk from AST node."""
        start_line = node.lineno - 1  # AST uses 1-based indexing
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
        
        # Get content
        content_lines = lines[start_line:end_line]
        content = '\n'.join(content_lines)
        
        # Create chunk ID
        chunk_id = f"{chunk_type.value}_{name}_{start_line}"
        
        # Estimate tokens (rough approximation: 1 token per 4 chars)
        size_tokens = len(content) // 4
        
        return CodeChunk(
            id=chunk_id,
            type=chunk_type,
            name=name,
            start_line=start_line,
            end_line=end_line,
            content=content[:500],  # Store preview only
            summary=self._generate_summary(content),
            size_bytes=len(content.encode('utf-8')),
            size_tokens=size_tokens
        )
    
    def _analyze_with_regex(self, lines: List[str], index: FileIndex) -> None:
        """Fallback regex-based analysis."""
        content = '\n'.join(lines)
        
        # Find classes
        for match in self.class_pattern.finditer(content):
            class_name = match.group(1)
            start_line = content[:match.start()].count('\n')
            
            # Find end of class (next class or end of file)
            next_class = self.class_pattern.search(content, match.end())
            if next_class:
                end_line = content[:next_class.start()].count('\n')
            else:
                end_line = len(lines)
            
            chunk = CodeChunk(
                id=f"class_{class_name}_{start_line}",
                type=ChunkType.CLASS,
                name=class_name,
                start_line=start_line,
                end_line=end_line,
                size_bytes=len('\n'.join(lines[start_line:end_line]).encode('utf-8'))
            )
            index.chunks[chunk.id] = chunk
            index.classes[class_name] = []
    
    def _find_sections(self, lines: List[str], index: FileIndex) -> None:
        """Find sections marked with special comments."""
        content = '\n'.join(lines)
        
        for match in self.section_pattern.finditer(content):
            line_num = content[:match.start()].count('\n')
            section_name = lines[line_num].strip('# =')
            
            # Find end of section (next section marker or end)
            next_section = self.section_pattern.search(content, match.end())
            if next_section:
                end_line = content[:next_section.start()].count('\n')
            else:
                end_line = len(lines)
            
            chunk = CodeChunk(
                id=f"section_{section_name}_{line_num}",
                type=ChunkType.SECTION,
                name=section_name,
                start_line=line_num,
                end_line=end_line,
                size_bytes=len('\n'.join(lines[line_num:end_line]).encode('utf-8'))
            )
            index.sections.append(chunk)
            index.chunks[chunk.id] = chunk
    
    def _build_dependencies(self, index: FileIndex) -> None:
        """Build dependency graph between chunks."""
        # Simplified dependency detection
        for chunk_id, chunk in index.chunks.items():
            dependencies = []
            
            # Check for function calls to other chunks
            for other_id, other_chunk in index.chunks.items():
                if other_id != chunk_id and other_chunk.name in chunk.content:
                    dependencies.append(other_id)
            
            chunk.dependencies = dependencies
            index.dependency_graph[chunk_id] = dependencies
    
    def _generate_summary(self, content: str) -> str:
        """Generate concise summary of code chunk."""
        lines = content.splitlines()
        
        # Extract docstring if present
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                # Found docstring
                quote = '"""' if '"""' in line else "'''"
                docstring_lines = []
                for j in range(i, min(i + 10, len(lines))):
                    docstring_lines.append(lines[j])
                    if j > i and quote in lines[j]:
                        break
                return ' '.join(docstring_lines).strip('"\' ')[:200]
        
        # No docstring, return first non-empty line
        for line in lines[:5]:
            if line.strip() and not line.strip().startswith('#'):
                return line.strip()[:200]
        
        return "No summary available"

# ==================== CHUNK LOADER ====================

class ChunkLoader:
    """Loads specific chunks from large files."""
    
    def __init__(self, file_path: str, index: FileIndex):
        self.file_path = Path(file_path)
        self.index = index
        self.cache = {}
        
    def load_chunk(self, chunk_id: str) -> str:
        """Load specific chunk content."""
        if chunk_id in self.cache:
            return self.cache[chunk_id]
        
        if chunk_id not in self.index.chunks:
            raise ValueError(f"Chunk not found: {chunk_id}")
        
        chunk = self.index.chunks[chunk_id]
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines[chunk.start_line:chunk.end_line])
        
        self.cache[chunk_id] = content
        return content
    
    def load_class(self, class_name: str, include_methods: bool = True) -> str:
        """Load entire class with optional methods."""
        if class_name not in self.index.classes:
            raise ValueError(f"Class not found: {class_name}")
        
        # Find class chunk
        class_chunk = None
        for chunk in self.index.chunks.values():
            if chunk.type == ChunkType.CLASS and chunk.name == class_name:
                class_chunk = chunk
                break
        
        if not class_chunk:
            raise ValueError(f"Class chunk not found: {class_name}")
        
        content = self.load_chunk(class_chunk.id)
        
        if include_methods:
            # Add method contents
            for method_chunk in self.index.classes[class_name]:
                content += "\n" + self.load_chunk(method_chunk.id)
        
        return content
    
    def load_function(self, function_name: str) -> str:
        """Load specific function."""
        for chunk in self.index.functions:
            if chunk.name == function_name:
                return self.load_chunk(chunk.id)
        
        raise ValueError(f"Function not found: {function_name}")
    
    def load_section(self, section_name: str) -> str:
        """Load specific section."""
        for chunk in self.index.sections:
            if section_name in chunk.name:
                return self.load_chunk(chunk.id)
        
        raise ValueError(f"Section not found: {section_name}")
    
    def load_lines(self, start: int, end: int) -> str:
        """Load specific line range."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return ''.join(lines[start:end])
    
    def load_with_context(self, chunk_id: str, context_lines: int = 50) -> Dict[str, str]:
        """Load chunk with surrounding context."""
        chunk = self.index.chunks[chunk_id]
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        result = {
            'before': ''.join(lines[max(0, chunk.start_line - context_lines):chunk.start_line]),
            'chunk': ''.join(lines[chunk.start_line:chunk.end_line]),
            'after': ''.join(lines[chunk.end_line:min(len(lines), chunk.end_line + context_lines)])
        }
        
        return result

# ==================== SMART EDITOR ====================

class SmartEditor:
    """Performs targeted edits on large files."""
    
    def __init__(self, file_path: str, index: FileIndex):
        self.file_path = Path(file_path)
        self.index = index
        self.loader = ChunkLoader(file_path, index)
        
    def edit_chunk(self, chunk_id: str, new_content: str) -> bool:
        """Replace specific chunk content."""
        if chunk_id not in self.index.chunks:
            return False
        
        chunk = self.index.chunks[chunk_id]
        
        # Read file
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Replace chunk lines
        new_lines = new_content.splitlines(keepends=True)
        lines[chunk.start_line:chunk.end_line] = new_lines
        
        # Write back
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Update index
        chunk.end_line = chunk.start_line + len(new_lines)
        chunk.content = new_content[:500]
        
        return True
    
    def add_to_class(self, class_name: str, method_code: str) -> bool:
        """Add method to class."""
        if class_name not in self.index.classes:
            return False
        
        # Find class chunk
        class_chunk = None
        for chunk in self.index.chunks.values():
            if chunk.type == ChunkType.CLASS and chunk.name == class_name:
                class_chunk = chunk
                break
        
        if not class_chunk:
            return False
        
        # Read file
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find insertion point (before last line of class)
        insertion_line = class_chunk.end_line - 1
        
        # Indent method code
        indented_code = textwrap.indent(method_code, '    ')
        
        # Insert method
        lines.insert(insertion_line, '\n' + indented_code + '\n')
        
        # Write back
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
    
    def pattern_replace(self, pattern: str, replacement: str, 
                       chunk_filter: Optional[ChunkType] = None) -> int:
        """Replace pattern across file or specific chunk types."""
        count = 0
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if chunk_filter:
            # Replace only in specific chunk types
            for chunk in self.index.chunks.values():
                if chunk.type == chunk_filter:
                    chunk_content = self.loader.load_chunk(chunk.id)
                    new_content, n = re.subn(pattern, replacement, chunk_content)
                    if n > 0:
                        self.edit_chunk(chunk.id, new_content)
                        count += n
        else:
            # Global replace
            new_content, count = re.subn(pattern, replacement, content)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return count

# ==================== MAIN INTERFACE ====================

class MegaFileHandler:
    """Main interface for handling large files."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.analyzer = FileAnalyzer()
        self.index = None
        self.loader = None
        self.editor = None
        
    def analyze(self) -> FileIndex:
        """Analyze file and create index."""
        print(f"Analyzing {self.file_path}...")
        self.index = self.analyzer.analyze_file(str(self.file_path))
        self.loader = ChunkLoader(str(self.file_path), self.index)
        self.editor = SmartEditor(str(self.file_path), self.index)
        
        print(self.index.get_structure_summary())
        return self.index
    
    def load_chunk(self, identifier: str) -> str:
        """Load specific chunk by ID or name."""
        if not self.loader:
            self.analyze()
        
        # Try as chunk ID first
        if identifier in self.index.chunks:
            return self.loader.load_chunk(identifier)
        
        # Try as class name
        if identifier in self.index.classes:
            return self.loader.load_class(identifier)
        
        # Try as function name
        for chunk in self.index.functions:
            if chunk.name == identifier:
                return self.loader.load_function(identifier)
        
        raise ValueError(f"Chunk/class/function not found: {identifier}")
    
    def edit(self, target: str, new_content: str) -> bool:
        """Edit specific target."""
        if not self.editor:
            self.analyze()
        
        # Find target chunk
        for chunk_id, chunk in self.index.chunks.items():
            if target in chunk.name or target == chunk_id:
                return self.editor.edit_chunk(chunk_id, new_content)
        
        return False
    
    def fix_all_bare_excepts(self) -> int:
        """Fix all bare except clauses."""
        if not self.editor:
            self.analyze()
        
        pattern = r'except\s*:\s*\n'
        replacement = 'except Exception as e:\n'
        count = self.editor.pattern_replace(pattern, replacement)
        print(f"Fixed {count} bare except clauses")
        return count
    
    def get_chunk_for_editing(self, target: str, max_tokens: int = 20000) -> Dict[str, Any]:
        """Get optimal chunks for editing a target."""
        if not self.loader:
            self.analyze()
        
        result = {
            'target': target,
            'content': '',
            'context': {},
            'dependencies': [],
            'tokens': 0
        }
        
        # Find target chunk
        target_chunk = None
        for chunk in self.index.chunks.values():
            if target in chunk.name:
                target_chunk = chunk
                break
        
        if not target_chunk:
            raise ValueError(f"Target not found: {target}")
        
        # Load target with context
        context_data = self.loader.load_with_context(target_chunk.id)
        result['content'] = context_data['chunk']
        result['context'] = {
            'before': context_data['before'][-500:],  # Last 500 chars
            'after': context_data['after'][:500]      # First 500 chars
        }
        
        # Load dependencies if space allows
        for dep_id in target_chunk.dependencies[:5]:  # Max 5 dependencies
            if dep_id in self.index.chunks:
                dep_chunk = self.index.chunks[dep_id]
                result['dependencies'].append({
                    'name': dep_chunk.name,
                    'summary': dep_chunk.summary
                })
        
        # Estimate tokens
        total_content = result['content'] + str(result['context']) + str(result['dependencies'])
        result['tokens'] = len(total_content) // 4  # Rough estimate
        
        return result
    
    def save_index(self, output_path: Optional[str] = None) -> str:
        """Save index to JSON file."""
        if not self.index:
            self.analyze()
        
        if not output_path:
            output_path = str(self.file_path) + '.index.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.index.to_json())
        
        print(f"Index saved to {output_path}")
        return output_path
    
    def load_index(self, index_path: str) -> FileIndex:
        """Load saved index."""
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruct index (simplified)
        self.index = FileIndex(
            file_path=data['file_path'],
            total_lines=data['total_lines'],
            total_bytes=data['total_bytes']
        )
        
        # Reconstruct chunks
        for chunk_id, chunk_data in data['chunks'].items():
            chunk = CodeChunk(
                id=chunk_data['id'],
                type=ChunkType(chunk_data['type']),
                name=chunk_data['name'],
                start_line=chunk_data['start_line'],
                end_line=chunk_data['end_line'],
                content=chunk_data.get('content', ''),
                summary=chunk_data.get('summary', ''),
                size_bytes=chunk_data.get('size_bytes', 0),
                size_tokens=chunk_data.get('size_tokens', 0)
            )
            self.index.chunks[chunk_id] = chunk
        
        self.loader = ChunkLoader(self.file_path, self.index)
        self.editor = SmartEditor(self.file_path, self.index)
        
        return self.index

# ==================== CLI INTERFACE ====================

def main():
    """Command-line interface for MFHS."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mfhs_tool.py <command> <file> [options]")
        print("\nCommands:")
        print("  analyze <file>     - Analyze file structure")
        print("  load <file> <target> - Load specific chunk")
        print("  fix-excepts <file> - Fix bare except clauses")
        print("  save-index <file>  - Save file index")
        print("\nExamples:")
        print("  python mfhs_tool.py analyze elements_extractor_no_llm.py")
        print("  python mfhs_tool.py load elements_extractor_no_llm.py ElementsExtractorNoLLM")
        return
    
    command = sys.argv[1]
    
    if command == "analyze" and len(sys.argv) >= 3:
        file_path = sys.argv[2]
        handler = MegaFileHandler(file_path)
        handler.analyze()
        handler.save_index()
        
    elif command == "load" and len(sys.argv) >= 4:
        file_path = sys.argv[2]
        target = sys.argv[3]
        handler = MegaFileHandler(file_path)
        content = handler.load_chunk(target)
        print(f"\n{target}:")
        print("-" * 50)
        print(content[:2000])  # First 2000 chars
        if len(content) > 2000:
            print(f"\n... ({len(content) - 2000} more characters)")
    
    elif command == "fix-excepts" and len(sys.argv) >= 3:
        file_path = sys.argv[2]
        handler = MegaFileHandler(file_path)
        handler.fix_all_bare_excepts()
    
    elif command == "save-index" and len(sys.argv) >= 3:
        file_path = sys.argv[2]
        handler = MegaFileHandler(file_path)
        handler.save_index()
    
    else:
        print(f"Unknown command or missing arguments: {command}")

if __name__ == "__main__":
    main()