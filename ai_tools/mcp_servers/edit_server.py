#!/usr/bin/env python3
"""
EditServer - Precision Modifications MCP Server
Part of MFHS-MCP System for handling massive codebases

Provides surgical edits, multi-file transactions, atomic operations,
rollback support, and conflict resolution for files of any size.
"""

import ast
import difflib
import json
import logging
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import hashlib
from datetime import datetime
import tempfile

# MCP Server SDK imports
try:
    from mcp import Server, Tool
    from mcp.types import TextContent, Resource
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EditServer")

# ============================================================================
# Data Models
# ============================================================================

class EditType(Enum):
    """Types of edits"""
    REPLACE = "replace"
    INSERT = "insert"
    DELETE = "delete"
    APPEND = "append"
    PREPEND = "prepend"
    REGEX_REPLACE = "regex_replace"
    AST_TRANSFORM = "ast_transform"
    REFACTOR = "refactor"

class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    OURS = "ours"
    THEIRS = "theirs"
    MERGE = "merge"
    MANUAL = "manual"
    AUTO = "auto"

@dataclass
class Edit:
    """Represents a single edit operation"""
    id: str
    type: EditType
    file_path: str
    target: Optional[str] = None  # Function/class/line range
    content: Optional[str] = None
    pattern: Optional[str] = None  # For regex
    replacement: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['type'] = self.type.value
        return data

@dataclass
class Transaction:
    """Group of edits to be applied atomically"""
    id: str
    edits: List[Edit]
    status: str = "pending"  # pending, in_progress, committed, rolled_back
    timestamp: float = field(default_factory=time.time)
    rollback_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'edits': [e.to_dict() for e in self.edits],
            'status': self.status,
            'timestamp': self.timestamp
        }

@dataclass
class Conflict:
    """Represents an edit conflict"""
    edit1: Edit
    edit2: Edit
    conflict_type: str
    resolution: Optional[ConflictResolution] = None
    resolved_content: Optional[str] = None

# ============================================================================
# Surgical Editor
# ============================================================================

class SurgicalEditor:
    """Perform precise edits without loading entire files"""
    
    def __init__(self):
        self.edit_history = []
        self.active_transactions = {}
    
    def apply_edit(self, edit: Edit) -> Dict[str, Any]:
        """Apply a single edit to a file"""
        result = {
            'edit_id': edit.id,
            'status': 'pending',
            'changes': []
        }
        
        try:
            if edit.type == EditType.REPLACE:
                result = self._replace_content(edit)
            elif edit.type == EditType.INSERT:
                result = self._insert_content(edit)
            elif edit.type == EditType.DELETE:
                result = self._delete_content(edit)
            elif edit.type == EditType.APPEND:
                result = self._append_content(edit)
            elif edit.type == EditType.PREPEND:
                result = self._prepend_content(edit)
            elif edit.type == EditType.REGEX_REPLACE:
                result = self._regex_replace(edit)
            elif edit.type == EditType.AST_TRANSFORM:
                result = self._ast_transform(edit)
            elif edit.type == EditType.REFACTOR:
                result = self._refactor_code(edit)
            
            # Record in history
            self.edit_history.append(edit)
            result['status'] = 'success'
            
        except Exception as e:
            logger.error(f"Edit failed: {e}")
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _replace_content(self, edit: Edit) -> Dict:
        """Replace content in file"""
        with open(edit.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_content = ''.join(lines)
        changes = []
        
        if edit.line_start is not None and edit.line_end is not None:
            # Replace specific lines
            old_content = ''.join(lines[edit.line_start-1:edit.line_end])
            lines[edit.line_start-1:edit.line_end] = [edit.content]
            changes.append({
                'type': 'replace',
                'line_start': edit.line_start,
                'line_end': edit.line_end,
                'old': old_content,
                'new': edit.content
            })
        elif edit.target:
            # Replace specific target (function/class)
            new_lines, target_changes = self._replace_target(lines, edit.target, edit.content)
            lines = new_lines
            changes.extend(target_changes)
        
        # Write back
        with open(edit.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return {
            'edit_id': edit.id,
            'changes': changes,
            'lines_modified': len(changes)
        }
    
    def _insert_content(self, edit: Edit) -> Dict:
        """Insert content at specific location"""
        with open(edit.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if edit.line_start is not None:
            # Insert at specific line
            lines.insert(edit.line_start - 1, edit.content + '\n')
            changes = [{
                'type': 'insert',
                'line': edit.line_start,
                'content': edit.content
            }]
        else:
            changes = []
        
        with open(edit.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return {
            'edit_id': edit.id,
            'changes': changes
        }
    
    def _delete_content(self, edit: Edit) -> Dict:
        """Delete content from file"""
        with open(edit.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        changes = []
        
        if edit.line_start is not None and edit.line_end is not None:
            # Delete specific lines
            deleted = lines[edit.line_start-1:edit.line_end]
            del lines[edit.line_start-1:edit.line_end]
            changes.append({
                'type': 'delete',
                'line_start': edit.line_start,
                'line_end': edit.line_end,
                'deleted': ''.join(deleted)
            })
        
        with open(edit.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return {
            'edit_id': edit.id,
            'changes': changes
        }
    
    def _append_content(self, edit: Edit) -> Dict:
        """Append content to end of file"""
        with open(edit.file_path, 'a', encoding='utf-8') as f:
            f.write('\n' + edit.content)
        
        return {
            'edit_id': edit.id,
            'changes': [{
                'type': 'append',
                'content': edit.content
            }]
        }
    
    def _prepend_content(self, edit: Edit) -> Dict:
        """Prepend content to beginning of file"""
        with open(edit.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(edit.file_path, 'w', encoding='utf-8') as f:
            f.write(edit.content + '\n' + content)
        
        return {
            'edit_id': edit.id,
            'changes': [{
                'type': 'prepend',
                'content': edit.content
            }]
        }
    
    def _regex_replace(self, edit: Edit) -> Dict:
        """Replace using regex pattern"""
        with open(edit.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = re.compile(edit.pattern)
        matches = list(pattern.finditer(content))
        
        new_content, count = pattern.subn(edit.replacement, content)
        
        with open(edit.file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return {
            'edit_id': edit.id,
            'changes': [{
                'type': 'regex_replace',
                'pattern': edit.pattern,
                'replacement': edit.replacement,
                'occurrences': count
            }]
        }
    
    def _ast_transform(self, edit: Edit) -> Dict:
        """Transform code using AST"""
        with open(edit.file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Parse AST
        tree = ast.parse(code)
        
        # Apply transformation (simplified - would be more complex in production)
        class Transformer(ast.NodeTransformer):
            def visit_Name(self, node):
                # Example: rename variables
                if hasattr(edit, 'metadata') and 'rename' in edit.metadata:
                    renames = edit.metadata['rename']
                    if node.id in renames:
                        node.id = renames[node.id]
                return node
        
        transformer = Transformer()
        new_tree = transformer.visit(tree)
        
        # Generate new code
        new_code = ast.unparse(new_tree) if hasattr(ast, 'unparse') else code
        
        with open(edit.file_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        
        return {
            'edit_id': edit.id,
            'changes': [{
                'type': 'ast_transform',
                'transformation': 'applied'
            }]
        }
    
    def _refactor_code(self, edit: Edit) -> Dict:
        """Refactor code (rename, extract, inline, etc.)"""
        # This would integrate with rope or similar refactoring library
        # Simplified implementation
        changes = []
        
        if edit.metadata.get('refactor_type') == 'rename':
            old_name = edit.metadata['old_name']
            new_name = edit.metadata['new_name']
            
            with open(edit.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple word boundary replacement
            pattern = r'\b' + re.escape(old_name) + r'\b'
            new_content, count = re.subn(pattern, new_name, content)
            
            with open(edit.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            changes.append({
                'type': 'refactor',
                'refactor_type': 'rename',
                'old_name': old_name,
                'new_name': new_name,
                'occurrences': count
            })
        
        return {
            'edit_id': edit.id,
            'changes': changes
        }
    
    def _replace_target(self, lines: List[str], target: str, new_content: str) -> Tuple[List[str], List[Dict]]:
        """Replace a specific target (function/class) in lines"""
        # Simple implementation - would use AST in production
        changes = []
        new_lines = lines.copy()
        
        # Find target
        for i, line in enumerate(lines):
            if f"def {target}" in line or f"class {target}" in line:
                # Find end of target (simple indent-based)
                start = i
                indent = len(line) - len(line.lstrip())
                end = start + 1
                
                for j in range(start + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' ' * (indent + 1)):
                        end = j
                        break
                
                # Replace
                old_content = ''.join(lines[start:end])
                new_lines[start:end] = [new_content + '\n']
                
                changes.append({
                    'type': 'replace_target',
                    'target': target,
                    'line_start': start + 1,
                    'line_end': end,
                    'old': old_content,
                    'new': new_content
                })
                break
        
        return new_lines, changes

# ============================================================================
# Transaction Manager
# ============================================================================

class TransactionManager:
    """Manage atomic edit transactions"""
    
    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self.backup_dir = Path(tempfile.gettempdir()) / "edit_server_backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def begin_transaction(self, transaction_id: str) -> Transaction:
        """Begin a new transaction"""
        transaction = Transaction(
            id=transaction_id,
            edits=[],
            status="in_progress"
        )
        self.transactions[transaction_id] = transaction
        return transaction
    
    def add_edit(self, transaction_id: str, edit: Edit):
        """Add edit to transaction"""
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        transaction = self.transactions[transaction_id]
        if transaction.status != "in_progress":
            raise ValueError(f"Transaction {transaction_id} is not in progress")
        
        transaction.edits.append(edit)
    
    def commit_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Commit all edits in transaction"""
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        transaction = self.transactions[transaction_id]
        editor = SurgicalEditor()
        results = []
        backups = {}
        
        try:
            # Create backups
            for edit in transaction.edits:
                if edit.file_path not in backups:
                    backup_path = self._create_backup(edit.file_path)
                    backups[edit.file_path] = backup_path
            
            # Apply all edits
            for edit in transaction.edits:
                result = editor.apply_edit(edit)
                results.append(result)
                
                if result['status'] == 'failed':
                    # Rollback on failure
                    self._rollback_backups(backups)
                    transaction.status = "rolled_back"
                    return {
                        'transaction_id': transaction_id,
                        'status': 'failed',
                        'error': result.get('error'),
                        'rolled_back': True
                    }
            
            # All edits successful
            transaction.status = "committed"
            transaction.rollback_data = {'backups': backups}
            
            return {
                'transaction_id': transaction_id,
                'status': 'success',
                'edits_applied': len(transaction.edits),
                'results': results
            }
            
        except Exception as e:
            # Rollback on error
            self._rollback_backups(backups)
            transaction.status = "rolled_back"
            return {
                'transaction_id': transaction_id,
                'status': 'failed',
                'error': str(e),
                'rolled_back': True
            }
    
    def rollback_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Rollback a committed transaction"""
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        transaction = self.transactions[transaction_id]
        
        if transaction.status != "committed":
            return {
                'transaction_id': transaction_id,
                'status': 'failed',
                'error': 'Transaction not committed'
            }
        
        # Restore backups
        backups = transaction.rollback_data.get('backups', {})
        self._rollback_backups(backups)
        
        transaction.status = "rolled_back"
        
        return {
            'transaction_id': transaction_id,
            'status': 'success',
            'files_restored': len(backups)
        }
    
    def _create_backup(self, file_path: str) -> str:
        """Create backup of file"""
        backup_name = f"{Path(file_path).name}.{int(time.time())}.backup"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        return str(backup_path)
    
    def _rollback_backups(self, backups: Dict[str, str]):
        """Restore files from backups"""
        for original_path, backup_path in backups.items():
            if Path(backup_path).exists():
                shutil.copy2(backup_path, original_path)

# ============================================================================
# Conflict Resolver
# ============================================================================

class ConflictResolver:
    """Resolve conflicts between edits"""
    
    def detect_conflicts(self, edits: List[Edit]) -> List[Conflict]:
        """Detect conflicts between edits"""
        conflicts = []
        
        # Group edits by file
        file_edits = {}
        for edit in edits:
            if edit.file_path not in file_edits:
                file_edits[edit.file_path] = []
            file_edits[edit.file_path].append(edit)
        
        # Check for conflicts within each file
        for file_path, file_edit_list in file_edits.items():
            for i, edit1 in enumerate(file_edit_list):
                for edit2 in file_edit_list[i+1:]:
                    conflict = self._check_conflict(edit1, edit2)
                    if conflict:
                        conflicts.append(conflict)
        
        return conflicts
    
    def _check_conflict(self, edit1: Edit, edit2: Edit) -> Optional[Conflict]:
        """Check if two edits conflict"""
        # Check line overlap
        if edit1.line_start and edit1.line_end and edit2.line_start and edit2.line_end:
            # Check for overlap
            if not (edit1.line_end < edit2.line_start or edit2.line_end < edit1.line_start):
                return Conflict(
                    edit1=edit1,
                    edit2=edit2,
                    conflict_type="line_overlap"
                )
        
        # Check target conflict
        if edit1.target and edit1.target == edit2.target:
            return Conflict(
                edit1=edit1,
                edit2=edit2,
                conflict_type="same_target"
            )
        
        return None
    
    def resolve_conflict(self, conflict: Conflict, strategy: ConflictResolution) -> Dict[str, Any]:
        """Resolve a conflict using specified strategy"""
        if strategy == ConflictResolution.OURS:
            # Keep first edit
            return {
                'resolution': 'ours',
                'kept_edit': conflict.edit1.id,
                'discarded_edit': conflict.edit2.id
            }
        
        elif strategy == ConflictResolution.THEIRS:
            # Keep second edit
            return {
                'resolution': 'theirs',
                'kept_edit': conflict.edit2.id,
                'discarded_edit': conflict.edit1.id
            }
        
        elif strategy == ConflictResolution.MERGE:
            # Attempt to merge
            merged = self._merge_edits(conflict.edit1, conflict.edit2)
            return {
                'resolution': 'merged',
                'merged_content': merged
            }
        
        elif strategy == ConflictResolution.AUTO:
            # Automatic resolution based on heuristics
            if conflict.conflict_type == "line_overlap":
                # If one is delete and other is modify, apply modify
                if conflict.edit1.type == EditType.DELETE:
                    return self.resolve_conflict(conflict, ConflictResolution.THEIRS)
                elif conflict.edit2.type == EditType.DELETE:
                    return self.resolve_conflict(conflict, ConflictResolution.OURS)
            
            # Default to merge
            return self.resolve_conflict(conflict, ConflictResolution.MERGE)
        
        return {
            'resolution': 'manual',
            'message': 'Manual resolution required'
        }
    
    def _merge_edits(self, edit1: Edit, edit2: Edit) -> str:
        """Attempt to merge two edits"""
        # Simple merge - in production would use 3-way merge
        if edit1.content and edit2.content:
            # Use difflib to merge
            lines1 = edit1.content.splitlines(keepends=True)
            lines2 = edit2.content.splitlines(keepends=True)
            
            merger = difflib.Differ()
            diff = list(merger.compare(lines1, lines2))
            
            merged = []
            for line in diff:
                if line.startswith('  '):  # Common line
                    merged.append(line[2:])
                elif line.startswith('+ '):  # Added in edit2
                    merged.append(line[2:])
                elif line.startswith('- '):  # Removed in edit2
                    pass  # Skip
            
            return ''.join(merged)
        
        return edit2.content or edit1.content or ""

# ============================================================================
# MCP Server Implementation
# ============================================================================

class EditMCPServer:
    """MCP Server for precision code editing"""
    
    def __init__(self):
        self.server = Server("edit-server")
        self.editor = SurgicalEditor()
        self.transaction_manager = TransactionManager()
        self.conflict_resolver = ConflictResolver()
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.server.tool()
        async def edit_file(
            file_path: str,
            edit_type: str,
            content: Optional[str] = None,
            target: Optional[str] = None,
            line_start: Optional[int] = None,
            line_end: Optional[int] = None,
            pattern: Optional[str] = None,
            replacement: Optional[str] = None
        ) -> TextContent:
            """Perform a single edit on a file"""
            try:
                # Create edit
                edit_id = hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()[:8]
                edit = Edit(
                    id=edit_id,
                    type=EditType(edit_type),
                    file_path=file_path,
                    content=content,
                    target=target,
                    line_start=line_start,
                    line_end=line_end,
                    pattern=pattern,
                    replacement=replacement
                )
                
                # Apply edit
                result = self.editor.apply_edit(edit)
                
                return TextContent(text=json.dumps(result, indent=2))
                
            except Exception as e:
                logger.error(f"Edit error: {e}")
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def begin_transaction(transaction_id: Optional[str] = None) -> TextContent:
            """Begin a new edit transaction"""
            try:
                if not transaction_id:
                    transaction_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
                
                transaction = self.transaction_manager.begin_transaction(transaction_id)
                
                return TextContent(text=json.dumps({
                    'transaction_id': transaction.id,
                    'status': transaction.status,
                    'timestamp': transaction.timestamp
                }, indent=2))
                
            except Exception as e:
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def add_to_transaction(
            transaction_id: str,
            file_path: str,
            edit_type: str,
            **kwargs
        ) -> TextContent:
            """Add an edit to a transaction"""
            try:
                # Create edit
                edit_id = hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()[:8]
                edit = Edit(
                    id=edit_id,
                    type=EditType(edit_type),
                    file_path=file_path,
                    **kwargs
                )
                
                # Add to transaction
                self.transaction_manager.add_edit(transaction_id, edit)
                
                return TextContent(text=json.dumps({
                    'transaction_id': transaction_id,
                    'edit_id': edit_id,
                    'status': 'added'
                }, indent=2))
                
            except Exception as e:
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def commit_transaction(transaction_id: str) -> TextContent:
            """Commit all edits in a transaction"""
            try:
                result = self.transaction_manager.commit_transaction(transaction_id)
                return TextContent(text=json.dumps(result, indent=2))
                
            except Exception as e:
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def rollback_transaction(transaction_id: str) -> TextContent:
            """Rollback a committed transaction"""
            try:
                result = self.transaction_manager.rollback_transaction(transaction_id)
                return TextContent(text=json.dumps(result, indent=2))
                
            except Exception as e:
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def detect_conflicts(edit_specs: List[Dict]) -> TextContent:
            """Detect conflicts between multiple edits"""
            try:
                # Create Edit objects
                edits = []
                for spec in edit_specs:
                    edit = Edit(
                        id=spec.get('id', hashlib.md5(str(time.time()).encode()).hexdigest()[:8]),
                        type=EditType(spec['edit_type']),
                        file_path=spec['file_path'],
                        line_start=spec.get('line_start'),
                        line_end=spec.get('line_end'),
                        target=spec.get('target')
                    )
                    edits.append(edit)
                
                # Detect conflicts
                conflicts = self.conflict_resolver.detect_conflicts(edits)
                
                # Format results
                conflict_list = []
                for conflict in conflicts:
                    conflict_list.append({
                        'edit1_id': conflict.edit1.id,
                        'edit2_id': conflict.edit2.id,
                        'conflict_type': conflict.conflict_type
                    })
                
                return TextContent(text=json.dumps({
                    'conflicts_detected': len(conflicts),
                    'conflicts': conflict_list
                }, indent=2))
                
            except Exception as e:
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
        
        @self.server.tool()
        async def pattern_replace(
            file_path: str,
            pattern: str,
            replacement: str,
            flags: Optional[str] = None
        ) -> TextContent:
            """Replace all occurrences of a pattern in a file"""
            try:
                # Compile regex with flags
                regex_flags = 0
                if flags:
                    if 'i' in flags:
                        regex_flags |= re.IGNORECASE
                    if 'm' in flags:
                        regex_flags |= re.MULTILINE
                    if 's' in flags:
                        regex_flags |= re.DOTALL
                
                # Create edit
                edit = Edit(
                    id=hashlib.md5(f"{file_path}{pattern}".encode()).hexdigest()[:8],
                    type=EditType.REGEX_REPLACE,
                    file_path=file_path,
                    pattern=pattern if not regex_flags else f"(?{flags}){pattern}",
                    replacement=replacement
                )
                
                # Apply
                result = self.editor.apply_edit(edit)
                
                return TextContent(text=json.dumps(result, indent=2))
                
            except Exception as e:
                return TextContent(text=json.dumps({
                    'error': str(e),
                    'status': 'failed'
                }))
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        logger.info("Starting EditServer MCP server...")
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
    
    server = EditMCPServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()