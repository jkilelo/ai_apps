"""
Modern code extractor with type safety and comprehensive extraction capabilities.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from simple_apps_v2.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ExtractedCode:
    """Represents an extracted code block with metadata."""
    
    content: str
    language: str
    source_type: str  # 'json', 'text', 'html', 'xml', 'markdown', etc.
    extraction_method: str  # 'triple_backtick', 'inline', 'indented', etc.
    confidence: float  # 0.0 to 1.0 confidence in extraction accuracy
    context: Dict[str, Any]  # Additional context (line numbers, etc.)
    metadata: Dict[str, Any]  # Additional metadata
    
    def __post_init__(self) -> None:
        """Validate and normalize data after initialization."""
        self.content = self.content.strip()
        self.language = self.language.lower()
        self.confidence = max(0.0, min(1.0, self.confidence))


class GenericCodeExtractor:
    """Modern code extractor with comprehensive extraction capabilities."""
    
    def __init__(self):
        """Initialize the code extractor."""
        self.patterns = self._compile_patterns()
        
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for code extraction."""
        return {
            # Triple backtick code blocks (```language\ncode```)
            'triple_backtick': re.compile(
                r'```(?P<language>\w+)?\n(?P<content>.*?)```', 
                re.DOTALL | re.MULTILINE
            ),
            
            # Single backtick inline code (`code`)
            'single_backtick': re.compile(
                r'`(?P<content>[^`\n]+)`'
            ),
            
            # Indented code blocks (4+ spaces or 1+ tabs)
            'indented': re.compile(
                r'^(?P<indent>[ \t]{4,}|\t+)(?P<content>.+)$',
                re.MULTILINE
            ),
            
            # JSON blocks
            'json': re.compile(
                r'(?P<content>\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
                re.DOTALL
            ),
            
            # XML/HTML blocks
            'xml_html': re.compile(
                r'(?P<content><[^>]+>.*?</[^>]+>)',
                re.DOTALL
            ),
            
            # Python-style comments with code
            'python_comment': re.compile(
                r'#\s*(?P<content>.*?)(?=\n|$)',
                re.MULTILINE
            ),
            
            # SQL queries
            'sql': re.compile(
                r'\b(?P<content>(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b.*?)(?=;|\n\n|\Z)',
                re.DOTALL | re.IGNORECASE
            ),
            
            # Shell commands
            'shell': re.compile(
                r'^[$#]\s*(?P<content>.+)$',
                re.MULTILINE
            ),
        }
    
    def extract(
        self, 
        input_data: Union[str, Dict[str, Any], List[Any]],
        languages: Optional[List[str]] = None,
        max_results: Optional[int] = None
    ) -> List[ExtractedCode]:
        """
        Extract code from various input types.
        
        Args:
            input_data: Input to extract code from
            languages: Filter by specific languages
            max_results: Maximum number of results to return
            
        Returns:
            List of extracted code blocks
        """
        try:
            logger.info(f"Starting code extraction from {type(input_data).__name__}")
            
            # Convert input to string for processing
            text_content = self._normalize_input(input_data)
            
            # Extract code using different methods
            extracted_codes = []
            
            # Method 1: Triple backtick blocks
            extracted_codes.extend(self._extract_triple_backtick(text_content))
            
            # Method 2: JSON blocks
            extracted_codes.extend(self._extract_json_blocks(text_content))
            
            # Method 3: Indented blocks
            extracted_codes.extend(self._extract_indented_blocks(text_content))
            
            # Method 4: Single backtick inline
            extracted_codes.extend(self._extract_single_backtick(text_content))
            
            # Method 5: XML/HTML blocks
            extracted_codes.extend(self._extract_xml_html(text_content))
            
            # Method 6: SQL queries
            extracted_codes.extend(self._extract_sql(text_content))
            
            # Method 7: Shell commands
            extracted_codes.extend(self._extract_shell(text_content))
            
            # Filter by languages if specified
            if languages:
                extracted_codes = [
                    code for code in extracted_codes 
                    if code.language in languages
                ]
            
            # Sort by confidence (highest first)
            extracted_codes.sort(key=lambda x: x.confidence, reverse=True)
            
            # Limit results if specified
            if max_results:
                extracted_codes = extracted_codes[:max_results]
            
            logger.info(f"Extracted {len(extracted_codes)} code blocks")
            return extracted_codes
            
        except Exception as e:
            logger.error(f"Code extraction failed: {e}")
            return []
    
    def _normalize_input(self, input_data: Union[str, Dict[str, Any], List[Any]]) -> str:
        """Normalize input to string format."""
        if isinstance(input_data, str):
            return input_data
        elif isinstance(input_data, (dict, list)):
            return json.dumps(input_data, indent=2)
        else:
            return str(input_data)
    
    def _extract_triple_backtick(self, text: str) -> List[ExtractedCode]:
        """Extract code from triple backtick blocks."""
        codes = []
        
        for match in self.patterns['triple_backtick'].finditer(text):
            language = match.group('language') or 'text'
            content = match.group('content')
            
            code = ExtractedCode(
                content=content,
                language=language,
                source_type='markdown',
                extraction_method='triple_backtick',
                confidence=0.9,
                context={
                    'start': match.start(),
                    'end': match.end(),
                },
                metadata={}
            )
            codes.append(code)
        
        return codes
    
    def _extract_json_blocks(self, text: str) -> List[ExtractedCode]:
        """Extract JSON code blocks."""
        codes = []
        
        for match in self.patterns['json'].finditer(text):
            content = match.group('content')
            
            # Validate JSON
            try:
                json.loads(content)
                confidence = 0.8
            except json.JSONDecodeError:
                confidence = 0.3
            
            code = ExtractedCode(
                content=content,
                language='json',
                source_type='json',
                extraction_method='json_pattern',
                confidence=confidence,
                context={
                    'start': match.start(),
                    'end': match.end(),
                },
                metadata={}
            )
            codes.append(code)
        
        return codes
    
    def _extract_indented_blocks(self, text: str) -> List[ExtractedCode]:
        """Extract indented code blocks."""
        codes = []
        lines = text.split('\n')
        current_block = []
        current_indent = None
        
        for i, line in enumerate(lines):
            match = self.patterns['indented'].match(line)
            if match:
                indent = match.group('indent')
                content_line = match.group('content')
                
                if current_indent is None or indent == current_indent:
                    current_indent = indent
                    current_block.append(content_line)
                else:
                    # Different indentation, finish current block
                    if current_block:
                        self._add_indented_block(codes, current_block, i - len(current_block))
                    current_block = [content_line]
                    current_indent = indent
            else:
                # Non-indented line, finish current block
                if current_block:
                    self._add_indented_block(codes, current_block, i - len(current_block))
                    current_block = []
                    current_indent = None
        
        # Handle final block
        if current_block:
            self._add_indented_block(codes, current_block, len(lines) - len(current_block))
        
        return codes
    
    def _add_indented_block(self, codes: List[ExtractedCode], block: List[str], start_line: int) -> None:
        """Add an indented code block to the results."""
        if len(block) < 2:  # Skip single lines
            return
        
        content = '\n'.join(block)
        language = self._detect_language(content)
        
        code = ExtractedCode(
            content=content,
            language=language,
            source_type='indented',
            extraction_method='indented_block',
            confidence=0.6,
            context={
                'start_line': start_line,
                'end_line': start_line + len(block),
            },
            metadata={}
        )
        codes.append(code)
    
    def _extract_single_backtick(self, text: str) -> List[ExtractedCode]:
        """Extract single backtick inline code."""
        codes = []
        
        for match in self.patterns['single_backtick'].finditer(text):
            content = match.group('content')
            
            # Skip very short or very long inline code
            if len(content) < 3 or len(content) > 100:
                continue
            
            language = self._detect_language(content)
            
            code = ExtractedCode(
                content=content,
                language=language,
                source_type='inline',
                extraction_method='single_backtick',
                confidence=0.4,
                context={
                    'start': match.start(),
                    'end': match.end(),
                },
                metadata={}
            )
            codes.append(code)
        
        return codes
    
    def _extract_xml_html(self, text: str) -> List[ExtractedCode]:
        """Extract XML/HTML blocks."""
        codes = []
        
        for match in self.patterns['xml_html'].finditer(text):
            content = match.group('content')
            
            # Detect if it's HTML or XML
            language = 'html' if '<html' in content.lower() or '<div' in content.lower() else 'xml'
            
            code = ExtractedCode(
                content=content,
                language=language,
                source_type='markup',
                extraction_method='xml_html_pattern',
                confidence=0.7,
                context={
                    'start': match.start(),
                    'end': match.end(),
                },
                metadata={}
            )
            codes.append(code)
        
        return codes
    
    def _extract_sql(self, text: str) -> List[ExtractedCode]:
        """Extract SQL queries."""
        codes = []
        
        for match in self.patterns['sql'].finditer(text):
            content = match.group('content').strip()
            
            code = ExtractedCode(
                content=content,
                language='sql',
                source_type='sql',
                extraction_method='sql_pattern',
                confidence=0.8,
                context={
                    'start': match.start(),
                    'end': match.end(),
                },
                metadata={}
            )
            codes.append(code)
        
        return codes
    
    def _extract_shell(self, text: str) -> List[ExtractedCode]:
        """Extract shell commands."""
        codes = []
        
        for match in self.patterns['shell'].finditer(text):
            content = match.group('content').strip()
            
            code = ExtractedCode(
                content=content,
                language='bash',
                source_type='shell',
                extraction_method='shell_pattern',
                confidence=0.7,
                context={
                    'start': match.start(),
                    'end': match.end(),
                },
                metadata={}
            )
            codes.append(code)
        
        return codes
    
    def _detect_language(self, content: str) -> str:
        """Detect programming language from content."""
        content_lower = content.lower()
        
        # Python indicators
        if any(keyword in content_lower for keyword in ['def ', 'import ', 'from ', 'class ', 'if __name__']):
            return 'python'
        
        # JavaScript indicators
        if any(keyword in content_lower for keyword in ['function ', 'var ', 'let ', 'const ', 'console.log']):
            return 'javascript'
        
        # SQL indicators
        if any(keyword in content_lower for keyword in ['select ', 'insert ', 'update ', 'delete ', 'create table']):
            return 'sql'
        
        # Shell indicators
        if any(keyword in content_lower for keyword in ['echo ', 'cd ', 'ls ', 'mkdir ', 'chmod']):
            return 'bash'
        
        # JSON indicators
        try:
            json.loads(content)
            return 'json'
        except json.JSONDecodeError:
            pass
        
        return 'text'
    
    def extract_from_file(self, file_path: Union[str, Path]) -> List[ExtractedCode]:
        """Extract code from a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return []
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            codes = self.extract(content)
            
            # Add file metadata
            for code in codes:
                code.metadata.update({
                    'source_file': str(path),
                    'file_size': path.stat().st_size,
                    'file_modified': path.stat().st_mtime,
                })
            
            return codes
            
        except Exception as e:
            logger.error(f"Error extracting from file {file_path}: {e}")
            return []
    
    def extract_summary(self, codes: List[ExtractedCode]) -> Dict[str, Any]:
        """Generate summary statistics for extracted codes."""
        if not codes:
            return {}
        
        languages = {}
        methods = {}
        total_chars = 0
        
        for code in codes:
            # Count by language
            languages[code.language] = languages.get(code.language, 0) + 1
            
            # Count by extraction method
            methods[code.extraction_method] = methods.get(code.extraction_method, 0) + 1
            
            # Count characters
            total_chars += len(code.content)
        
        return {
            'total_blocks': len(codes),
            'languages': languages,
            'extraction_methods': methods,
            'total_characters': total_chars,
            'average_confidence': sum(code.confidence for code in codes) / len(codes),
            'highest_confidence': max(code.confidence for code in codes),
            'lowest_confidence': min(code.confidence for code in codes),
        }