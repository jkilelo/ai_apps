"""
MongoDB-like JSON file service for maintaining app state
"""

import json
import os
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path

class MongoDBService:
    """Service to handle JSON-based database operations"""
    
    def __init__(self, db_file: str = "mongo_db.json"):
        self.db_file = Path(__file__).parent / db_file
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database file exists with proper structure"""
        if not self.db_file.exists():
            default_structure = {
                "profiling_sessions": {},
                "dq_sessions": {},
                "ui_sessions": {}
            }
            self._write_db(default_structure)
    
    def _read_db(self) -> Dict:
        """Read the entire database"""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default structure if file is corrupted or missing
            default_structure = {
                "profiling_sessions": {},
                "dq_sessions": {},
                "ui_sessions": {}
            }
            self._write_db(default_structure)
            return default_structure
    
    def _write_db(self, data: Dict):
        """Write the entire database"""
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _create_session_key(self, database: str, table: str) -> str:
        """Create a session key from database and table"""
        return f"{database}.{table}"
    
    def _create_session_data(self, session_type: str, key: str, data: Dict) -> Dict:
        """Create session data with metadata"""
        return {
            "key": key,
            "session_type": session_type,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "data": data
        }
    
    # Profiling Session Methods
    def get_profiling_session(self, database: str, table: str) -> Optional[Dict]:
        """Get profiling session data"""
        db = self._read_db()
        session_key = self._create_session_key(database, table)
        return db["profiling_sessions"].get(session_key)
    
    def save_profiling_session(self, database: str, table: str, step: str, data: Dict):
        """Save profiling session data for a specific step"""
        db = self._read_db()
        session_key = self._create_session_key(database, table)
        
        if session_key not in db["profiling_sessions"]:
            db["profiling_sessions"][session_key] = self._create_session_data(
                "profiling", session_key, {}
            )
        
        # Update specific step data
        db["profiling_sessions"][session_key]["data"][step] = {
            "step_data": data,
            "timestamp": datetime.now().isoformat()
        }
        db["profiling_sessions"][session_key]["updated_at"] = datetime.now().isoformat()
        
        self._write_db(db)
    
    def clear_profiling_session(self, database: str, table: str):
        """Clear profiling session data"""
        db = self._read_db()
        session_key = self._create_session_key(database, table)
        
        if session_key in db["profiling_sessions"]:
            del db["profiling_sessions"][session_key]
            self._write_db(db)
    
    # Data Quality Session Methods
    def get_dq_session(self, database: str, table: str) -> Optional[Dict]:
        """Get data quality session data"""
        db = self._read_db()
        session_key = self._create_session_key(database, table)
        return db["dq_sessions"].get(session_key)
    
    def save_dq_session(self, database: str, table: str, step: str, data: Dict):
        """Save data quality session data for a specific step"""
        db = self._read_db()
        session_key = self._create_session_key(database, table)
        
        if session_key not in db["dq_sessions"]:
            db["dq_sessions"][session_key] = self._create_session_data(
                "dq", session_key, {}
            )
        
        # Update specific step data
        db["dq_sessions"][session_key]["data"][step] = {
            "step_data": data,
            "timestamp": datetime.now().isoformat()
        }
        db["dq_sessions"][session_key]["updated_at"] = datetime.now().isoformat()
        
        self._write_db(db)
    
    def clear_dq_session(self, database: str, table: str):
        """Clear data quality session data"""
        db = self._read_db()
        session_key = self._create_session_key(database, table)
        
        if session_key in db["dq_sessions"]:
            del db["dq_sessions"][session_key]
            self._write_db(db)
    
    # UI Session Methods
    def get_ui_session(self, url: str) -> Optional[Dict]:
        """Get UI session data"""
        db = self._read_db()
        return db["ui_sessions"].get(url)
    
    def save_ui_session(self, url: str, step: str, data: Dict):
        """Save UI session data for a specific step"""
        db = self._read_db()
        
        if url not in db["ui_sessions"]:
            db["ui_sessions"][url] = self._create_session_data(
                "ui", url, {}
            )
        
        # Update specific step data
        db["ui_sessions"][url]["data"][step] = {
            "step_data": data,
            "timestamp": datetime.now().isoformat()
        }
        db["ui_sessions"][url]["updated_at"] = datetime.now().isoformat()
        
        self._write_db(db)
    
    def clear_ui_session(self, url: str):
        """Clear UI session data"""
        db = self._read_db()
        
        if url in db["ui_sessions"]:
            del db["ui_sessions"][url]
            self._write_db(db)
    
    # General Methods
    def get_all_sessions(self) -> Dict:
        """Get all sessions"""
        return self._read_db()
    
    def get_session_summary(self) -> Dict:
        """Get a summary of all sessions"""
        db = self._read_db()
        return {
            "profiling_sessions_count": len(db["profiling_sessions"]),
            "dq_sessions_count": len(db["dq_sessions"]),
            "ui_sessions_count": len(db["ui_sessions"]),
            "total_sessions": len(db["profiling_sessions"]) + len(db["dq_sessions"]) + len(db["ui_sessions"])
        }
    
    def clear_all_sessions(self):
        """Clear all sessions"""
        default_structure = {
            "profiling_sessions": {},
            "dq_sessions": {},
            "ui_sessions": {}
        }
        self._write_db(default_structure)

# Global instance
mongo_service = MongoDBService()
