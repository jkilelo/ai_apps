"""SQLite-based session memory for short-term storage"""
import sqlite3
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger
from pydantic import BaseModel


class ConversationModel(BaseModel):
    """Conversation data model"""
    id: Optional[int] = None
    task_id: str
    user_input: str
    agent_response: str
    timestamp: Optional[datetime] = None


class ActionModel(BaseModel):
    """Action data model"""
    id: Optional[int] = None
    conversation_id: int
    action_type: str
    action_data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    success: bool = False
    timestamp: Optional[datetime] = None


class PageStateModel(BaseModel):
    """Page state data model"""
    id: Optional[int] = None
    url: str
    dom_snapshot: str
    screenshot_path: Optional[str] = None
    interactive_elements: Dict[str, Any]
    captured_at: Optional[datetime] = None


class SessionMemory:
    """Manages short-term memory using SQLite"""
    
    def __init__(self, db_path: str = ".claude/memory/session.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"Session memory initialized at {self.db_path}")
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Conversations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Actions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    action_type TEXT NOT NULL,
                    action_data TEXT NOT NULL,  -- JSON string
                    result TEXT,  -- JSON string
                    success BOOLEAN DEFAULT FALSE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            
            # Page states table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS page_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    dom_snapshot TEXT NOT NULL,
                    screenshot_path TEXT,
                    interactive_elements TEXT NOT NULL,  -- JSON string
                    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Errors table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id INTEGER,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    recovery_action TEXT,  -- JSON string
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (action_id) REFERENCES actions(id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_task_id ON conversations(task_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_actions_conversation_id ON actions(conversation_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_page_states_url ON page_states(url)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)")
    
    async def store_conversation(self, conversation: ConversationModel) -> int:
        """Store a conversation exchange"""
        loop = asyncio.get_event_loop()
        
        def _store():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO conversations (task_id, user_input, agent_response) VALUES (?, ?, ?)",
                    (conversation.task_id, conversation.user_input, conversation.agent_response)
                )
                return cursor.lastrowid
        
        conversation_id = await loop.run_in_executor(None, _store)
        logger.debug(f"Stored conversation {conversation_id} for task {conversation.task_id}")
        return conversation_id
    
    async def store_action(self, action: ActionModel) -> int:
        """Store an action and its result"""
        loop = asyncio.get_event_loop()
        
        def _store():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """INSERT INTO actions 
                       (conversation_id, action_type, action_data, result, success) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        action.conversation_id,
                        action.action_type,
                        json.dumps(action.action_data),
                        json.dumps(action.result) if action.result else None,
                        action.success
                    )
                )
                return cursor.lastrowid
        
        action_id = await loop.run_in_executor(None, _store)
        logger.debug(f"Stored action {action_id}: {action.action_type}")
        return action_id
    
    async def store_page_state(self, page_state: PageStateModel) -> int:
        """Store page state snapshot"""
        loop = asyncio.get_event_loop()
        
        def _store():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """INSERT INTO page_states 
                       (url, dom_snapshot, screenshot_path, interactive_elements) 
                       VALUES (?, ?, ?, ?)""",
                    (
                        page_state.url,
                        page_state.dom_snapshot,
                        page_state.screenshot_path,
                        json.dumps(page_state.interactive_elements)
                    )
                )
                return cursor.lastrowid
        
        state_id = await loop.run_in_executor(None, _store)
        logger.debug(f"Stored page state {state_id} for URL {page_state.url}")
        return state_id
    
    async def get_recent_conversations(self, limit: int = 10) -> List[ConversationModel]:
        """Retrieve recent conversations"""
        loop = asyncio.get_event_loop()
        
        def _get():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        
        rows = await loop.run_in_executor(None, _get)
        return [ConversationModel(**row) for row in rows]
    
    async def get_task_history(self, task_id: str) -> List[ConversationModel]:
        """Get all conversations for a specific task"""
        loop = asyncio.get_event_loop()
        
        def _get():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM conversations WHERE task_id = ? ORDER BY timestamp",
                    (task_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        
        rows = await loop.run_in_executor(None, _get)
        return [ConversationModel(**row) for row in rows]
    
    async def get_successful_actions(self, action_type: Optional[str] = None, limit: int = 50) -> List[ActionModel]:
        """Get successful actions for learning patterns"""
        loop = asyncio.get_event_loop()
        
        def _get():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                if action_type:
                    cursor = conn.execute(
                        """SELECT * FROM actions 
                           WHERE success = TRUE AND action_type = ? 
                           ORDER BY timestamp DESC LIMIT ?""",
                        (action_type, limit)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM actions WHERE success = TRUE ORDER BY timestamp DESC LIMIT ?",
                        (limit,)
                    )
                
                rows = []
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    # Parse JSON fields
                    row_dict['action_data'] = json.loads(row_dict['action_data'])
                    if row_dict['result']:
                        row_dict['result'] = json.loads(row_dict['result'])
                    rows.append(row_dict)
                return rows
        
        rows = await loop.run_in_executor(None, _get)
        return [ActionModel(**row) for row in rows]
    
    async def get_page_state(self, url: str) -> Optional[PageStateModel]:
        """Get most recent page state for URL"""
        loop = asyncio.get_event_loop()
        
        def _get():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM page_states WHERE url = ? ORDER BY captured_at DESC LIMIT 1",
                    (url,)
                )
                row = cursor.fetchone()
                if row:
                    row_dict = dict(row)
                    row_dict['interactive_elements'] = json.loads(row_dict['interactive_elements'])
                    return row_dict
                return None
        
        row = await loop.run_in_executor(None, _get)
        return PageStateModel(**row) if row else None
    
    async def cleanup_old_data(self, retention_hours: int = 24):
        """Clean up old session data"""
        loop = asyncio.get_event_loop()
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        
        def _cleanup():
            with sqlite3.connect(self.db_path) as conn:
                # Clean old conversations and their actions
                cursor = conn.execute(
                    "DELETE FROM conversations WHERE timestamp < ?",
                    (cutoff_time,)
                )
                conversations_deleted = cursor.rowcount
                
                # Clean old page states
                cursor = conn.execute(
                    "DELETE FROM page_states WHERE captured_at < ?",
                    (cutoff_time,)
                )
                states_deleted = cursor.rowcount
                
                # Clean orphaned actions (should be handled by foreign key cascade)
                conn.execute("DELETE FROM actions WHERE conversation_id NOT IN (SELECT id FROM conversations)")
                
                return conversations_deleted, states_deleted
        
        conv_deleted, states_deleted = await loop.run_in_executor(None, _cleanup)
        logger.info(f"Cleaned up {conv_deleted} conversations and {states_deleted} page states")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        loop = asyncio.get_event_loop()
        
        def _get_stats():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM conversations")
                conversations_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM actions")
                actions_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM page_states")
                page_states_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM actions WHERE success = TRUE")
                successful_actions = cursor.fetchone()[0]
                
                # Database size
                cursor = conn.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0]
                
                return {
                    'conversations': conversations_count,
                    'actions': actions_count,
                    'successful_actions': successful_actions,
                    'page_states': page_states_count,
                    'database_size_bytes': db_size,
                    'success_rate': successful_actions / max(actions_count, 1) * 100
                }
        
        return await loop.run_in_executor(None, _get_stats)
    
    async def search_conversations(self, query: str, limit: int = 20) -> List[ConversationModel]:
        """Search conversations by text content"""
        loop = asyncio.get_event_loop()
        
        def _search():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                # Simple text search (could be enhanced with FTS)
                cursor = conn.execute(
                    """SELECT * FROM conversations 
                       WHERE user_input LIKE ? OR agent_response LIKE ? 
                       ORDER BY timestamp DESC LIMIT ?""",
                    (f'%{query}%', f'%{query}%', limit)
                )
                return [dict(row) for row in cursor.fetchall()]
        
        rows = await loop.run_in_executor(None, _search)
        return [ConversationModel(**row) for row in rows]
    
    def close(self):
        """Close database connection (cleanup)"""
        # SQLite connections are created per operation, so no persistent connection to close
        logger.debug("Session memory closed")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.close()
        except:
            pass