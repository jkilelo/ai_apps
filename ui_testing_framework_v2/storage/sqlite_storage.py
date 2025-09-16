"""
SQLite storage backend for extraction results
Efficient, queryable, and with built-in deduplication
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager

from ..core.models import Element, ExtractionResult, PageCharacteristics


class SQLiteStorage:
    """SQLite-based storage with intelligent querying"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize storage with database path"""
        if db_path is None:
            # Store in script directory by default
            script_dir = Path(__file__).parent.parent
            db_path = script_dir / "data" / "extractions.db"
        
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        with self.connection() as conn:
            conn.executescript("""
                -- Extractions table
                CREATE TABLE IF NOT EXISTS extractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    profile TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration REAL,
                    content_hash TEXT,
                    cache_hit BOOLEAN DEFAULT 0,
                    characteristics JSON,
                    stats JSON,
                    UNIQUE(url, profile, content_hash)
                );
                
                -- Elements table
                CREATE TABLE IF NOT EXISTS elements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    extraction_id INTEGER NOT NULL,
                    selector TEXT NOT NULL,
                    tag_name TEXT NOT NULL,
                    element_type TEXT NOT NULL,
                    text TEXT,
                    attributes JSON,
                    is_visible BOOLEAN DEFAULT 1,
                    is_interactive BOOLEAN DEFAULT 0,
                    interaction_score REAL DEFAULT 0.0,
                    bounding_box JSON,
                    element_hash TEXT,
                    FOREIGN KEY (extraction_id) REFERENCES extractions(id),
                    UNIQUE(extraction_id, element_hash)
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_url ON extractions(url);
                CREATE INDEX IF NOT EXISTS idx_profile ON extractions(profile);
                CREATE INDEX IF NOT EXISTS idx_content_hash ON extractions(content_hash);
                CREATE INDEX IF NOT EXISTS idx_timestamp ON extractions(timestamp);
                CREATE INDEX IF NOT EXISTS idx_element_type ON elements(element_type);
                CREATE INDEX IF NOT EXISTS idx_interaction_score ON elements(interaction_score);
                CREATE INDEX IF NOT EXISTS idx_element_hash ON elements(element_hash);
                
                -- View for common queries
                CREATE VIEW IF NOT EXISTS recent_extractions AS
                SELECT 
                    e.*,
                    COUNT(el.id) as element_count
                FROM extractions e
                LEFT JOIN elements el ON e.id = el.extraction_id
                GROUP BY e.id
                ORDER BY e.timestamp DESC
                LIMIT 100;
            """)
            conn.commit()
    
    def save_extraction(self, result: ExtractionResult) -> int:
        """Save extraction result to database"""
        with self.connection() as conn:
            # Check for duplicate based on content hash
            if result.content_hash:
                existing = conn.execute(
                    "SELECT id FROM extractions WHERE url = ? AND profile = ? AND content_hash = ?",
                    (result.url, result.profile, result.content_hash)
                ).fetchone()
                
                if existing:
                    return existing["id"]
            
            # Insert extraction
            cursor = conn.execute("""
                INSERT INTO extractions (url, profile, timestamp, duration, content_hash, cache_hit, characteristics, stats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.url,
                result.profile,
                result.timestamp.isoformat(),
                result.duration,
                result.content_hash,
                result.cache_hit,
                json.dumps(result.characteristics.__dict__) if result.characteristics else None,
                json.dumps(result.stats())
            ))
            
            extraction_id = cursor.lastrowid
            
            # Insert elements
            for element in result.elements:
                conn.execute("""
                    INSERT OR IGNORE INTO elements 
                    (extraction_id, selector, tag_name, element_type, text, attributes, 
                     is_visible, is_interactive, interaction_score, bounding_box, element_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    extraction_id,
                    element.selector,
                    element.tag_name,
                    element.element_type.value,
                    element.text,
                    json.dumps(element.attributes),
                    element.is_visible,
                    element.is_interactive,
                    element.interaction_score,
                    json.dumps(element.bounding_box) if element.bounding_box else None,
                    element.hash()
                ))
            
            conn.commit()
            return extraction_id
    
    def get_extraction(self, extraction_id: int) -> Optional[ExtractionResult]:
        """Get extraction by ID"""
        with self.connection() as conn:
            # Get extraction
            row = conn.execute(
                "SELECT * FROM extractions WHERE id = ?", (extraction_id,)
            ).fetchone()
            
            if not row:
                return None
            
            # Get elements
            element_rows = conn.execute(
                "SELECT * FROM elements WHERE extraction_id = ?", (extraction_id,)
            ).fetchall()
            
            elements = []
            for erow in element_rows:
                elements.append(Element(
                    selector=erow["selector"],
                    tag_name=erow["tag_name"],
                    element_type=erow["element_type"],
                    text=erow["text"],
                    attributes=json.loads(erow["attributes"]) if erow["attributes"] else {},
                    is_visible=bool(erow["is_visible"]),
                    is_interactive=bool(erow["is_interactive"]),
                    interaction_score=erow["interaction_score"],
                    bounding_box=json.loads(erow["bounding_box"]) if erow["bounding_box"] else None
                ))
            
            # Create result
            characteristics = None
            if row["characteristics"]:
                char_data = json.loads(row["characteristics"])
                characteristics = PageCharacteristics(**char_data)
            
            return ExtractionResult(
                url=row["url"],
                profile=row["profile"],
                elements=elements,
                timestamp=datetime.fromisoformat(row["timestamp"]),
                duration=row["duration"],
                characteristics=characteristics,
                cache_hit=bool(row["cache_hit"]),
                content_hash=row["content_hash"]
            )
    
    def get_latest(self, url: str, profile: str) -> Optional[ExtractionResult]:
        """Get latest extraction for URL and profile"""
        with self.connection() as conn:
            row = conn.execute("""
                SELECT id FROM extractions 
                WHERE url = ? AND profile = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (url, profile)).fetchone()
            
            if row:
                return self.get_extraction(row["id"])
            return None
    
    def query_extractions(self, 
                         url: Optional[str] = None,
                         profile: Optional[str] = None,
                         since: Optional[datetime] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Query extractions with filters"""
        with self.connection() as conn:
            query = "SELECT * FROM recent_extractions WHERE 1=1"
            params = []
            
            if url:
                query += " AND url = ?"
                params.append(url)
            
            if profile:
                query += " AND profile = ?"
                params.append(profile)
            
            if since:
                query += " AND timestamp >= ?"
                params.append(since.isoformat())
            
            query += f" LIMIT {limit}"
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def query_elements(self,
                      element_type: Optional[str] = None,
                      min_interaction_score: Optional[float] = None,
                      interactive_only: bool = False,
                      limit: int = 1000) -> List[Dict[str, Any]]:
        """Query elements directly"""
        with self.connection() as conn:
            query = "SELECT e.*, ex.url, ex.profile FROM elements e JOIN extractions ex ON e.extraction_id = ex.id WHERE 1=1"
            params = []
            
            if element_type:
                query += " AND e.element_type = ?"
                params.append(element_type)
            
            if min_interaction_score is not None:
                query += " AND e.interaction_score >= ?"
                params.append(min_interaction_score)
            
            if interactive_only:
                query += " AND e.is_interactive = 1"
            
            query += f" LIMIT {limit}"
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        with self.connection() as conn:
            stats = {}
            
            # Total extractions
            stats["total_extractions"] = conn.execute(
                "SELECT COUNT(*) as count FROM extractions"
            ).fetchone()["count"]
            
            # Total elements
            stats["total_elements"] = conn.execute(
                "SELECT COUNT(*) as count FROM elements"
            ).fetchone()["count"]
            
            # Unique URLs
            stats["unique_urls"] = conn.execute(
                "SELECT COUNT(DISTINCT url) as count FROM extractions"
            ).fetchone()["count"]
            
            # Profile usage
            profile_stats = conn.execute("""
                SELECT profile, COUNT(*) as count 
                FROM extractions 
                GROUP BY profile
            """).fetchall()
            stats["profiles"] = {row["profile"]: row["count"] for row in profile_stats}
            
            # Database size
            stats["db_size_mb"] = Path(self.db_path).stat().st_size / (1024 * 1024)
            
            return stats
    
    def cleanup_old_data(self, days: int = 30):
        """Remove data older than specified days"""
        with self.connection() as conn:
            cutoff = datetime.now().timestamp() - (days * 86400)
            
            # Delete old extractions (cascade deletes elements)
            conn.execute(
                "DELETE FROM extractions WHERE timestamp < datetime(?, 'unixepoch')",
                (cutoff,)
            )
            
            # Vacuum to reclaim space
            conn.execute("VACUUM")
            conn.commit()
    
    def export_to_json(self, extraction_id: int, output_path: Path):
        """Export extraction to JSON for compatibility"""
        result = self.get_extraction(extraction_id)
        if result:
            data = {
                "url": result.url,
                "profile": result.profile,
                "timestamp": result.timestamp.isoformat(),
                "duration": result.duration,
                "stats": result.stats(),
                "elements": [e.to_dict() for e in result.elements]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)