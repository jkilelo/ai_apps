"""
Session Storage System

This module provides persistent storage for reverse prompting sessions,
supporting multiple backends including SQLite, Redis, and MongoDB.
"""

import asyncio
import json
import pickle
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
import logging

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import motor.motor_asyncio

    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from ..core.models import (
    ReversePromptingSession,
    StateSnapshot,
    EngineConfig,
    CodeArtifact,
    PromptGeneration,
    EvaluationResult,
)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def save_session(self, session: ReversePromptingSession) -> bool:
        """Save a complete session."""
        pass

    @abstractmethod
    async def load_session(
        self, session_id: Union[str, UUID]
    ) -> Optional[ReversePromptingSession]:
        """Load a session by ID."""
        pass

    @abstractmethod
    async def list_sessions(self, limit: int = 50) -> List[ReversePromptingSession]:
        """List recent sessions."""
        pass

    @abstractmethod
    async def save_state_snapshot(self, snapshot: StateSnapshot) -> bool:
        """Save a state snapshot."""
        pass

    @abstractmethod
    async def load_state_snapshots(
        self, session_id: Union[str, UUID]
    ) -> List[StateSnapshot]:
        """Load all state snapshots for a session."""
        pass

    @abstractmethod
    async def delete_session(self, session_id: Union[str, UUID]) -> bool:
        """Delete a session and all its data."""
        pass

    @abstractmethod
    async def cleanup_old_data(self, older_than_days: int = 30) -> int:
        """Clean up old data and return number of records deleted."""
        pass


class SQLiteStorage(StorageBackend):
    """SQLite-based storage backend."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Initialize database
        asyncio.create_task(self._init_db())

    async def _init_db(self):
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # Sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    session_data BLOB NOT NULL,
                    metadata TEXT
                )
            """
            )

            # State snapshots table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS state_snapshots (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    state_type TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    snapshot_data BLOB NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """
            )

            # Create indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions (created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_snapshots_session_id ON state_snapshots (session_id)"
            )

            conn.commit()
            self.logger.info("SQLite database initialized")
        finally:
            conn.close()

    async def save_session(self, session: ReversePromptingSession) -> bool:
        """Save a complete session to SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()

                # Serialize session data
                session_data = pickle.dumps(session.dict())
                metadata = json.dumps(
                    {
                        "strategies_used": [s.value for s in session.strategies_used],
                        "total_prompts": len(session.generated_prompts),
                        "total_evaluations": len(session.evaluations),
                        "best_score": (
                            session.best_result.overall_score
                            if session.best_result
                            else 0.0
                        ),
                    }
                )

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO sessions
                    (id, name, created_at, updated_at, session_data, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        str(session.id),
                        session.name,
                        session.created_at,
                        session.updated_at,
                        session_data,
                        metadata,
                    ),
                )

                conn.commit()
                return True
            finally:
                conn.close()
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
            return False

    async def load_session(
        self, session_id: Union[str, UUID]
    ) -> Optional[ReversePromptingSession]:
        """Load a session from SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT session_data FROM sessions WHERE id = ?", (str(session_id),)
                )

                row = cursor.fetchone()
                if row:
                    session_data = pickle.loads(row[0])
                    return ReversePromptingSession(**session_data)
                return None
            finally:
                conn.close()
        except Exception as e:
            self.logger.error(f"Failed to load session: {e}")
            return None

    async def list_sessions(self, limit: int = 50) -> List[ReversePromptingSession]:
        """List recent sessions from SQLite."""
        sessions = []
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT session_data FROM sessions
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )

                for row in cursor.fetchall():
                    try:
                        session_data = pickle.loads(row[0])
                        sessions.append(ReversePromptingSession(**session_data))
                    except Exception as e:
                        self.logger.warning(f"Failed to deserialize session: {e}")
                        continue
            finally:
                conn.close()
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")

        return sessions

    async def save_state_snapshot(self, snapshot: StateSnapshot) -> bool:
        """Save a state snapshot to SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()

                snapshot_data = pickle.dumps(snapshot.data)

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO state_snapshots
                    (id, session_id, state_type, created_at, snapshot_data)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        str(snapshot.id),
                        str(snapshot.session_id),
                        snapshot.state_type,
                        snapshot.created_at,
                        snapshot_data,
                    ),
                )

                conn.commit()
                return True
            finally:
                conn.close()
        except Exception as e:
            self.logger.error(f"Failed to save state snapshot: {e}")
            return False

    async def load_state_snapshots(
        self, session_id: Union[str, UUID]
    ) -> List[StateSnapshot]:
        """Load all state snapshots for a session from SQLite."""
        snapshots = []
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, state_type, created_at, snapshot_data
                    FROM state_snapshots
                    WHERE session_id = ?
                    ORDER BY created_at ASC
                """,
                    (str(session_id),),
                )

                for row in cursor.fetchall():
                    try:
                        snapshot_data = pickle.loads(row[3])
                        snapshots.append(
                            StateSnapshot(
                                id=UUID(row[0]),
                                session_id=UUID(str(session_id)),
                                state_type=row[1],
                                created_at=row[2],
                                data=snapshot_data,
                            )
                        )
                    except Exception as e:
                        self.logger.warning(f"Failed to deserialize snapshot: {e}")
                        continue
            finally:
                conn.close()
        except Exception as e:
            self.logger.error(f"Failed to load state snapshots: {e}")

        return snapshots

    async def delete_session(self, session_id: Union[str, UUID]) -> bool:
        """Delete a session and all its data from SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()

                # Delete snapshots first (foreign key constraint)
                cursor.execute(
                    "DELETE FROM state_snapshots WHERE session_id = ?",
                    (str(session_id),),
                )

                # Delete session
                cursor.execute("DELETE FROM sessions WHERE id = ?", (str(session_id),))

                conn.commit()
                return True
            finally:
                conn.close()
        except Exception as e:
            self.logger.error(f"Failed to delete session: {e}")
            return False

    async def cleanup_old_data(self, older_than_days: int = 30) -> int:
        """Clean up old data from SQLite."""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        deleted_count = 0

        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()

                # Delete old snapshots
                cursor.execute(
                    "DELETE FROM state_snapshots WHERE created_at < ?", (cutoff_date,)
                )
                deleted_count += cursor.rowcount

                # Delete old sessions
                cursor.execute(
                    "DELETE FROM sessions WHERE created_at < ?", (cutoff_date,)
                )
                deleted_count += cursor.rowcount

                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")

        return deleted_count


class RedisStorage(StorageBackend):
    """Redis-based storage backend."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis not available. Install with: pip install redis")

        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self.logger = logging.getLogger(__name__)

        # Test connection
        try:
            self.redis_client.ping()
            self.logger.info("Redis connection established")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def save_session(self, session: ReversePromptingSession) -> bool:
        """Save a complete session to Redis."""
        try:
            session_key = f"session:{session.id}"
            session_data = pickle.dumps(session.dict())

            # Save session with expiration (30 days default)
            self.redis_client.setex(session_key, 30 * 24 * 3600, session_data)

            # Add to sessions index
            self.redis_client.zadd(
                "sessions:index", {str(session.id): session.created_at.timestamp()}
            )

            return True
        except Exception as e:
            self.logger.error(f"Failed to save session to Redis: {e}")
            return False

    async def load_session(
        self, session_id: Union[str, UUID]
    ) -> Optional[ReversePromptingSession]:
        """Load a session from Redis."""
        try:
            session_key = f"session:{session_id}"
            session_data = self.redis_client.get(session_key)

            if session_data:
                data = pickle.loads(session_data)
                return ReversePromptingSession(**data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to load session from Redis: {e}")
            return None

    async def list_sessions(self, limit: int = 50) -> List[ReversePromptingSession]:
        """List recent sessions from Redis."""
        sessions = []
        try:
            # Get most recent session IDs
            session_ids = self.redis_client.zrevrange("sessions:index", 0, limit - 1)

            for session_id in session_ids:
                session = await self.load_session(session_id.decode("utf-8"))
                if session:
                    sessions.append(session)
        except Exception as e:
            self.logger.error(f"Failed to list sessions from Redis: {e}")

        return sessions

    async def save_state_snapshot(self, snapshot: StateSnapshot) -> bool:
        """Save a state snapshot to Redis."""
        try:
            snapshot_key = f"snapshot:{snapshot.id}"
            snapshot_data = pickle.dumps(snapshot.dict())

            # Save snapshot with expiration
            self.redis_client.setex(
                snapshot_key, 7 * 24 * 3600, snapshot_data
            )  # 7 days

            # Add to session's snapshots index
            session_snapshots_key = f"session:{snapshot.session_id}:snapshots"
            self.redis_client.zadd(
                session_snapshots_key,
                {str(snapshot.id): snapshot.created_at.timestamp()},
            )

            return True
        except Exception as e:
            self.logger.error(f"Failed to save state snapshot to Redis: {e}")
            return False

    async def load_state_snapshots(
        self, session_id: Union[str, UUID]
    ) -> List[StateSnapshot]:
        """Load all state snapshots for a session from Redis."""
        snapshots = []
        try:
            session_snapshots_key = f"session:{session_id}:snapshots"
            snapshot_ids = self.redis_client.zrange(session_snapshots_key, 0, -1)

            for snapshot_id in snapshot_ids:
                snapshot_key = f"snapshot:{snapshot_id.decode('utf-8')}"
                snapshot_data = self.redis_client.get(snapshot_key)

                if snapshot_data:
                    data = pickle.loads(snapshot_data)
                    snapshots.append(StateSnapshot(**data))
        except Exception as e:
            self.logger.error(f"Failed to load state snapshots from Redis: {e}")

        return snapshots

    async def delete_session(self, session_id: Union[str, UUID]) -> bool:
        """Delete a session and all its data from Redis."""
        try:
            # Delete session
            session_key = f"session:{session_id}"
            self.redis_client.delete(session_key)

            # Remove from sessions index
            self.redis_client.zrem("sessions:index", str(session_id))

            # Delete all snapshots
            session_snapshots_key = f"session:{session_id}:snapshots"
            snapshot_ids = self.redis_client.zrange(session_snapshots_key, 0, -1)

            for snapshot_id in snapshot_ids:
                snapshot_key = f"snapshot:{snapshot_id.decode('utf-8')}"
                self.redis_client.delete(snapshot_key)

            self.redis_client.delete(session_snapshots_key)

            return True
        except Exception as e:
            self.logger.error(f"Failed to delete session from Redis: {e}")
            return False

    async def cleanup_old_data(self, older_than_days: int = 30) -> int:
        """Clean up old data from Redis."""
        cutoff_timestamp = (
            datetime.now() - timedelta(days=older_than_days)
        ).timestamp()
        deleted_count = 0

        try:
            # Get old session IDs
            old_session_ids = self.redis_client.zrangebyscore(
                "sessions:index", 0, cutoff_timestamp
            )

            for session_id in old_session_ids:
                if await self.delete_session(session_id.decode("utf-8")):
                    deleted_count += 1

        except Exception as e:
            self.logger.error(f"Failed to cleanup old data from Redis: {e}")

        return deleted_count


class MongoDBStorage(StorageBackend):
    """MongoDB-based storage backend."""

    def __init__(
        self,
        mongo_url: str = "mongodb://localhost:27017",
        database_name: str = "reverse_prompting",
    ):
        if not MONGODB_AVAILABLE:
            raise ImportError("MongoDB not available. Install with: pip install motor")

        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        self.db = self.client[database_name]
        self.sessions_collection = self.db.sessions
        self.snapshots_collection = self.db.state_snapshots
        self.logger = logging.getLogger(__name__)

        # Create indexes
        asyncio.create_task(self._create_indexes())

    async def _create_indexes(self):
        """Create database indexes."""
        try:
            await self.sessions_collection.create_index("created_at")
            await self.snapshots_collection.create_index("session_id")
            await self.snapshots_collection.create_index("created_at")
            self.logger.info("MongoDB indexes created")
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB indexes: {e}")

    async def save_session(self, session: ReversePromptingSession) -> bool:
        """Save a complete session to MongoDB."""
        try:
            session_doc = session.dict()
            session_doc["_id"] = str(session.id)

            await self.sessions_collection.replace_one(
                {"_id": str(session.id)}, session_doc, upsert=True
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to save session to MongoDB: {e}")
            return False

    async def load_session(
        self, session_id: Union[str, UUID]
    ) -> Optional[ReversePromptingSession]:
        """Load a session from MongoDB."""
        try:
            session_doc = await self.sessions_collection.find_one(
                {"_id": str(session_id)}
            )
            if session_doc:
                session_doc.pop("_id", None)  # Remove MongoDB ID
                return ReversePromptingSession(**session_doc)
            return None
        except Exception as e:
            self.logger.error(f"Failed to load session from MongoDB: {e}")
            return None

    async def list_sessions(self, limit: int = 50) -> List[ReversePromptingSession]:
        """List recent sessions from MongoDB."""
        sessions = []
        try:
            cursor = self.sessions_collection.find().sort("created_at", -1).limit(limit)
            async for session_doc in cursor:
                try:
                    session_doc.pop("_id", None)
                    sessions.append(ReversePromptingSession(**session_doc))
                except Exception as e:
                    self.logger.warning(f"Failed to deserialize session: {e}")
                    continue
        except Exception as e:
            self.logger.error(f"Failed to list sessions from MongoDB: {e}")

        return sessions

    async def save_state_snapshot(self, snapshot: StateSnapshot) -> bool:
        """Save a state snapshot to MongoDB."""
        try:
            snapshot_doc = snapshot.dict()
            snapshot_doc["_id"] = str(snapshot.id)

            await self.snapshots_collection.replace_one(
                {"_id": str(snapshot.id)}, snapshot_doc, upsert=True
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to save state snapshot to MongoDB: {e}")
            return False

    async def load_state_snapshots(
        self, session_id: Union[str, UUID]
    ) -> List[StateSnapshot]:
        """Load all state snapshots for a session from MongoDB."""
        snapshots = []
        try:
            cursor = self.snapshots_collection.find(
                {"session_id": str(session_id)}
            ).sort("created_at", 1)

            async for snapshot_doc in cursor:
                try:
                    snapshot_doc.pop("_id", None)
                    snapshots.append(StateSnapshot(**snapshot_doc))
                except Exception as e:
                    self.logger.warning(f"Failed to deserialize snapshot: {e}")
                    continue
        except Exception as e:
            self.logger.error(f"Failed to load state snapshots from MongoDB: {e}")

        return snapshots

    async def delete_session(self, session_id: Union[str, UUID]) -> bool:
        """Delete a session and all its data from MongoDB."""
        try:
            # Delete session
            await self.sessions_collection.delete_one({"_id": str(session_id)})

            # Delete all snapshots
            await self.snapshots_collection.delete_many({"session_id": str(session_id)})

            return True
        except Exception as e:
            self.logger.error(f"Failed to delete session from MongoDB: {e}")
            return False

    async def cleanup_old_data(self, older_than_days: int = 30) -> int:
        """Clean up old data from MongoDB."""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        deleted_count = 0

        try:
            # Delete old snapshots
            snapshots_result = await self.snapshots_collection.delete_many(
                {"created_at": {"$lt": cutoff_date}}
            )
            deleted_count += snapshots_result.deleted_count

            # Delete old sessions
            sessions_result = await self.sessions_collection.delete_many(
                {"created_at": {"$lt": cutoff_date}}
            )
            deleted_count += sessions_result.deleted_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup old data from MongoDB: {e}")

        return deleted_count


class SessionStorage:
    """Main session storage interface that wraps different backends."""

    def __init__(self, config: EngineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize backend based on configuration
        self.backend = self._create_backend()

    def _create_backend(self) -> StorageBackend:
        """Create the appropriate storage backend."""
        storage_type = self.config.storage_backend.lower()

        if storage_type == "sqlite":
            db_path = Path(self.config.storage_path) / "sessions.db"
            return SQLiteStorage(db_path)

        elif storage_type == "redis":
            redis_url = getattr(self.config, "redis_url", "redis://localhost:6379")
            return RedisStorage(redis_url)

        elif storage_type == "mongodb":
            mongo_url = getattr(self.config, "mongo_url", "mongodb://localhost:27017")
            db_name = getattr(self.config, "mongo_database", "reverse_prompting")
            return MongoDBStorage(mongo_url, db_name)

        else:
            # Default to SQLite
            self.logger.warning(
                f"Unknown storage backend '{storage_type}', defaulting to SQLite"
            )
            db_path = Path(self.config.storage_path) / "sessions.db"
            return SQLiteStorage(db_path)

    async def save_session(self, session: ReversePromptingSession) -> bool:
        """Save a complete session."""
        return await self.backend.save_session(session)

    async def load_session(
        self, session_id: Union[str, UUID]
    ) -> Optional[ReversePromptingSession]:
        """Load a session by ID."""
        return await self.backend.load_session(session_id)

    async def list_sessions(self, limit: int = 50) -> List[ReversePromptingSession]:
        """List recent sessions."""
        return await self.backend.list_sessions(limit)

    async def save_state_snapshot(self, snapshot: StateSnapshot) -> bool:
        """Save a state snapshot."""
        return await self.backend.save_state_snapshot(snapshot)

    async def load_state_snapshots(
        self, session_id: Union[str, UUID]
    ) -> List[StateSnapshot]:
        """Load all state snapshots for a session."""
        return await self.backend.load_state_snapshots(session_id)

    async def delete_session(self, session_id: Union[str, UUID]) -> bool:
        """Delete a session and all its data."""
        return await self.backend.delete_session(session_id)

    async def cleanup_old_data(self, older_than_days: int = 30) -> int:
        """Clean up old data and return number of records deleted."""
        return await self.backend.cleanup_old_data(older_than_days)

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            recent_sessions = await self.list_sessions(
                1000
            )  # Get up to 1000 recent sessions

            total_sessions = len(recent_sessions)
            if total_sessions == 0:
                return {"total_sessions": 0}

            total_prompts = sum(len(s.generated_prompts) for s in recent_sessions)
            total_evaluations = sum(len(s.evaluations) for s in recent_sessions)

            success_rates = [
                s.get_success_rate() for s in recent_sessions if s.evaluations
            ]
            avg_success_rate = (
                sum(success_rates) / len(success_rates) if success_rates else 0.0
            )

            best_scores = [
                s.best_result.overall_score for s in recent_sessions if s.best_result
            ]
            avg_best_score = sum(best_scores) / len(best_scores) if best_scores else 0.0

            return {
                "total_sessions": total_sessions,
                "total_prompts": total_prompts,
                "total_evaluations": total_evaluations,
                "average_success_rate": avg_success_rate,
                "average_best_score": avg_best_score,
                "storage_backend": type(self.backend).__name__,
            }
        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}

    async def cleanup(self):
        """Cleanup storage resources."""
        if hasattr(self.backend, "cleanup"):
            await self.backend.cleanup()


# For easy importing
__all__ = ["SessionStorage", "SQLiteStorage", "RedisStorage", "MongoDBStorage"]
