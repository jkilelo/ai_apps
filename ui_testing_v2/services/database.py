"""
Database engine and session management for UI Testing Framework v2
Async SQLModel operations with PostgreSQL/SQLite support
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from sqlmodel import SQLModel, select, and_, or_, desc, func
from sqlalchemy import text
from sqlalchemy.orm import selectinload

from ..core.config import DatabaseConfig
from ..models.database import (
    Project,
    TestSession,
    ExtractedElement,
    TestCase,
    ExecutionResult,
    WorkflowState,
    UserSession,
    CacheEntry,
    TaskStatus,
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Async database manager with connection pooling and session management"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize database engine and session factory"""
        if self._initialized:
            return
        
        logger.info(f"Initializing database: {self.config.url}")
        
        # Configure engine based on database type
        engine_kwargs = {
            "echo": self.config.echo,
            "future": True,
        }
        
        if self.config.url.startswith("sqlite"):
            # SQLite configuration
            engine_kwargs.update({
                "poolclass": NullPool,
                "connect_args": {"check_same_thread": False},
            })
        elif self.config.url.startswith("postgresql"):
            # PostgreSQL configuration
            engine_kwargs.update({
                "poolclass": QueuePool,
                "pool_size": self.config.pool_size,
                "max_overflow": self.config.max_overflow,
                "pool_pre_ping": True,
                "pool_recycle": 3600,  # 1 hour
            })
        
        self.engine = create_async_engine(self.config.url, **engine_kwargs)
        
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        self._initialized = True
        logger.info("Database manager initialized successfully")
    
    async def create_tables(self) -> None:
        """Create all database tables"""
        if not self._initialized:
            await self.initialize()
        
        logger.info("Creating database tables...")
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully")
    
    async def drop_tables(self) -> None:
        """Drop all database tables"""
        if not self._initialized:
            await self.initialize()
        
        logger.warning("Dropping all database tables...")
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        logger.warning("All database tables dropped")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                # Get basic stats
                project_count = (await session.execute(select(func.count(Project.id)))).scalar()
                session_count = (await session.execute(select(func.count(TestSession.id)))).scalar()
                active_sessions = (await session.execute(
                    select(func.count(TestSession.id))
                    .where(TestSession.status.in_([TaskStatus.PENDING, TaskStatus.RUNNING]))
                )).scalar()
                
                return {
                    "status": "healthy",
                    "database_type": "postgresql" if "postgresql" in self.config.url else "sqlite",
                    "total_projects": project_count,
                    "total_sessions": session_count,
                    "active_sessions": active_sessions,
                    "pool_size": getattr(self.engine.pool, "size", 0) if hasattr(self.engine, "pool") else 0,
                    "checked_out": getattr(self.engine.pool, "checkedout", 0) if hasattr(self.engine, "pool") else 0,
                }
        
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with automatic cleanup"""
        if not self._initialized:
            await self.initialize()
        
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def cleanup(self) -> None:
        """Cleanup database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections cleaned up")


class ProjectRepository:
    """Repository for project operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
    ) -> Project:
        """Create a new project"""
        async with self.db_manager.get_session() as session:
            project = Project(
                name=name,
                description=description,
                settings=settings or {},
                created_by=created_by,
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return project
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID"""
        async with self.db_manager.get_session() as session:
            return await session.get(Project, project_id)
    
    async def get_project_by_name(self, name: str) -> Optional[Project]:
        """Get project by name"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(Project).where(Project.name == name)
            )
            return result.scalar_one_or_none()
    
    async def list_projects(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Project]:
        """List projects with pagination"""
        async with self.db_manager.get_session() as session:
            query = select(Project)
            
            if active_only:
                query = query.where(Project.is_active == True)
            
            query = query.order_by(desc(Project.created_at)).limit(limit).offset(offset)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def update_project(
        self,
        project_id: UUID,
        **updates: Any,
    ) -> Optional[Project]:
        """Update project"""
        async with self.db_manager.get_session() as session:
            project = await session.get(Project, project_id)
            if not project:
                return None
            
            for key, value in updates.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            await session.commit()
            await session.refresh(project)
            return project
    
    async def delete_project(self, project_id: UUID) -> bool:
        """Soft delete project"""
        return await self.update_project(project_id, is_active=False) is not None


class SessionRepository:
    """Repository for test session operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_session(
        self,
        name: str,
        url: str,
        project_id: Optional[UUID] = None,
        description: Optional[str] = None,
        extraction_config: Optional[Dict[str, Any]] = None,
        test_config: Optional[Dict[str, Any]] = None,
        ai_config: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
    ) -> TestSession:
        """Create a new test session"""
        async with self.db_manager.get_session() as session:
            test_session = TestSession(
                name=name,
                url=url,
                project_id=project_id,
                description=description,
                extraction_config=extraction_config or {},
                test_config=test_config or {},
                ai_config=ai_config or {},
                created_by=created_by,
            )
            session.add(test_session)
            await session.commit()
            await session.refresh(test_session)
            return test_session
    
    async def get_session(self, session_id: UUID) -> Optional[TestSession]:
        """Get session by ID"""
        async with self.db_manager.get_session() as session:
            return await session.get(TestSession, session_id)
    
    async def get_session_with_elements(self, session_id: UUID) -> Optional[TestSession]:
        """Get session with related elements"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(TestSession)
                .where(TestSession.id == session_id)
                .options(selectinload(TestSession.extracted_elements))
            )
            return result.scalar_one_or_none()
    
    async def list_sessions(
        self,
        project_id: Optional[UUID] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[TestSession]:
        """List sessions with filters"""
        async with self.db_manager.get_session() as session:
            query = select(TestSession)
            
            conditions = []
            if project_id:
                conditions.append(TestSession.project_id == project_id)
            if status:
                conditions.append(TestSession.status == status)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(desc(TestSession.created_at)).limit(limit).offset(offset)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def update_session_status(
        self,
        session_id: UUID,
        status: TaskStatus,
        progress_percentage: Optional[int] = None,
        current_step: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[TestSession]:
        """Update session status and progress"""
        async with self.db_manager.get_session() as session:
            test_session = await session.get(TestSession, session_id)
            if not test_session:
                return None
            
            test_session.status = status
            
            if progress_percentage is not None:
                test_session.progress_percentage = progress_percentage
            
            if current_step is not None:
                test_session.current_step = current_step
            
            if error_message is not None:
                test_session.error_message = error_message
            
            # Update timing
            if status == TaskStatus.RUNNING and not test_session.started_at:
                from datetime import datetime
                test_session.started_at = datetime.utcnow()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                from datetime import datetime
                if not test_session.completed_at:
                    test_session.completed_at = datetime.utcnow()
                
                if test_session.started_at and test_session.completed_at:
                    duration = test_session.completed_at - test_session.started_at
                    test_session.execution_duration = int(duration.total_seconds())
            
            await session.commit()
            await session.refresh(test_session)
            return test_session


class ElementRepository:
    """Repository for extracted element operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def save_elements(
        self,
        session_id: UUID,
        elements: List[Dict[str, Any]],
    ) -> List[ExtractedElement]:
        """Save multiple extracted elements"""
        async with self.db_manager.get_session() as session:
            element_objects = []
            
            for element_data in elements:
                element = ExtractedElement(
                    session_id=session_id,
                    **element_data
                )
                element_objects.append(element)
                session.add(element)
            
            await session.commit()
            
            # Refresh all objects
            for element in element_objects:
                await session.refresh(element)
            
            return element_objects
    
    async def get_session_elements(
        self,
        session_id: UUID,
        element_type: Optional[str] = None,
        is_clickable: Optional[bool] = None,
    ) -> List[ExtractedElement]:
        """Get elements for a session with filters"""
        async with self.db_manager.get_session() as session:
            query = select(ExtractedElement).where(ExtractedElement.session_id == session_id)
            
            if element_type:
                query = query.where(ExtractedElement.element_type == element_type)
            
            if is_clickable is not None:
                query = query.where(ExtractedElement.is_clickable == is_clickable)
            
            query = query.order_by(ExtractedElement.extraction_timestamp)
            
            result = await session.execute(query)
            return result.scalars().all()


class WorkflowRepository:
    """Repository for workflow state operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_workflow(
        self,
        workflow_id: str,
        workflow_type: str,
        workflow_name: str,
        total_steps: int = 0,
        config: Optional[Dict[str, Any]] = None,
    ) -> WorkflowState:
        """Create a new workflow state"""
        async with self.db_manager.get_session() as session:
            workflow = WorkflowState(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                workflow_name=workflow_name,
                total_steps=total_steps,
                config=config or {},
            )
            session.add(workflow)
            await session.commit()
            await session.refresh(workflow)
            return workflow
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow by ID"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(WorkflowState).where(WorkflowState.workflow_id == workflow_id)
            )
            return result.scalar_one_or_none()
    
    async def update_workflow_progress(
        self,
        workflow_id: str,
        current_step: str,
        completed_steps: Optional[int] = None,
        state_data: Optional[Dict[str, Any]] = None,
        step_info: Optional[Dict[str, Any]] = None,
    ) -> Optional[WorkflowState]:
        """Update workflow progress"""
        async with self.db_manager.get_session() as session:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                return None
            
            workflow.current_step = current_step
            
            if completed_steps is not None:
                workflow.completed_steps = completed_steps
                if workflow.total_steps > 0:
                    workflow.progress_percentage = min(100, int((completed_steps / workflow.total_steps) * 100))
            
            if state_data is not None:
                workflow.state_data.update(state_data)
            
            if step_info is not None:
                workflow.step_history.append({
                    "step": current_step,
                    "timestamp": datetime.utcnow().isoformat(),
                    **step_info
                })
            
            from datetime import datetime
            workflow.last_activity_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(workflow)
            return workflow
