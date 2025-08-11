"""
State management service for UI Testing Framework v2
Handles workflow states, session management, and async operations
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from uuid import UUID, uuid4
from enum import Enum

from ..models.database import TaskStatus, WorkflowState, TestSession
from ..services.database import DatabaseManager, WorkflowRepository, SessionRepository
from ..core.events import EventBus

logger = logging.getLogger(__name__)


class StateChangeEvent(str, Enum):
    """State change event types"""
    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_CANCELLED = "workflow.cancelled"
    
    SESSION_CREATED = "session.created"
    SESSION_STARTED = "session.started"
    SESSION_PROGRESS = "session.progress"
    SESSION_COMPLETED = "session.completed"
    SESSION_FAILED = "session.failed"


class WorkflowStep:
    """Represents a single workflow step"""
    
    def __init__(
        self,
        name: str,
        description: str,
        action: Callable,
        timeout: Optional[int] = None,
        retry_count: int = 0,
        required: bool = True,
    ):
        self.name = name
        self.description = description
        self.action = action
        self.timeout = timeout or 300  # 5 minutes default
        self.retry_count = retry_count
        self.required = required
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[Any] = None


class WorkflowDefinition:
    """Defines a complete workflow with steps and configuration"""
    
    def __init__(
        self,
        name: str,
        description: str,
        steps: List[WorkflowStep],
        timeout: Optional[int] = None,
        parallel_execution: bool = False,
    ):
        self.name = name
        self.description = description
        self.steps = steps
        self.timeout = timeout or 1800  # 30 minutes default
        self.parallel_execution = parallel_execution


class WorkflowManager:
    """Manages workflow execution and state tracking"""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        event_bus: Optional[EventBus] = None,
    ):
        self.db_manager = db_manager
        self.event_bus = event_bus
        self.workflow_repo = WorkflowRepository(db_manager)
        self._running_workflows: Dict[str, asyncio.Task] = {}
        self._workflow_locks: Dict[str, asyncio.Lock] = {}
    
    async def create_workflow(
        self,
        workflow_id: str,
        definition: WorkflowDefinition,
        config: Optional[Dict[str, Any]] = None,
    ) -> WorkflowState:
        """Create a new workflow instance"""
        workflow_state = await self.workflow_repo.create_workflow(
            workflow_id=workflow_id,
            workflow_type=definition.name,
            workflow_name=definition.description,
            total_steps=len(definition.steps),
            config=config or {},
        )
        
        if self.event_bus:
            await self.event_bus.emit(StateChangeEvent.WORKFLOW_CREATED, {
                "workflow_id": workflow_id,
                "workflow_type": definition.name,
                "total_steps": len(definition.steps),
            })
        
        logger.info(f"Created workflow: {workflow_id} ({definition.name})")
        return workflow_state
    
    async def start_workflow(
        self,
        workflow_id: str,
        definition: WorkflowDefinition,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Start workflow execution"""
        if workflow_id in self._running_workflows:
            raise ValueError(f"Workflow {workflow_id} is already running")
        
        # Create lock for this workflow
        self._workflow_locks[workflow_id] = asyncio.Lock()
        
        # Start workflow execution task
        task = asyncio.create_task(
            self._execute_workflow(workflow_id, definition, context or {})
        )
        self._running_workflows[workflow_id] = task
        
        # Update workflow state
        await self.workflow_repo.update_workflow_progress(
            workflow_id=workflow_id,
            current_step="started",
            state_data={"status": TaskStatus.RUNNING},
        )
        
        if self.event_bus:
            await self.event_bus.emit(StateChangeEvent.WORKFLOW_STARTED, {
                "workflow_id": workflow_id,
                "context": context,
            })
        
        logger.info(f"Started workflow: {workflow_id}")
    
    async def _execute_workflow(
        self,
        workflow_id: str,
        definition: WorkflowDefinition,
        context: Dict[str, Any],
    ) -> None:
        """Execute workflow steps"""
        try:
            async with self._workflow_locks[workflow_id]:
                start_time = datetime.utcnow()
                
                if definition.parallel_execution:
                    await self._execute_steps_parallel(workflow_id, definition, context)
                else:
                    await self._execute_steps_sequential(workflow_id, definition, context)
                
                # Mark workflow as completed
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                await self.workflow_repo.update_workflow_progress(
                    workflow_id=workflow_id,
                    current_step="completed",
                    completed_steps=len(definition.steps),
                    state_data={
                        "status": TaskStatus.COMPLETED,
                        "duration_seconds": duration,
                        "completed_at": end_time.isoformat(),
                    },
                )
                
                if self.event_bus:
                    await self.event_bus.emit(StateChangeEvent.WORKFLOW_COMPLETED, {
                        "workflow_id": workflow_id,
                        "duration_seconds": duration,
                    })
                
                logger.info(f"Completed workflow: {workflow_id} in {duration:.1f}s")
        
        except Exception as e:
            # Mark workflow as failed
            await self.workflow_repo.update_workflow_progress(
                workflow_id=workflow_id,
                current_step="failed",
                state_data={
                    "status": TaskStatus.FAILED,
                    "error": str(e),
                    "failed_at": datetime.utcnow().isoformat(),
                },
            )
            
            if self.event_bus:
                await self.event_bus.emit(StateChangeEvent.WORKFLOW_FAILED, {
                    "workflow_id": workflow_id,
                    "error": str(e),
                })
            
            logger.error(f"Workflow {workflow_id} failed: {e}")
            raise
        
        finally:
            # Cleanup
            self._running_workflows.pop(workflow_id, None)
            self._workflow_locks.pop(workflow_id, None)
    
    async def _execute_steps_sequential(
        self,
        workflow_id: str,
        definition: WorkflowDefinition,
        context: Dict[str, Any],
    ) -> None:
        """Execute workflow steps sequentially"""
        for i, step in enumerate(definition.steps):
            step_number = i + 1
            
            # Update workflow progress
            await self.workflow_repo.update_workflow_progress(
                workflow_id=workflow_id,
                current_step=step.name,
                completed_steps=i,
                step_info={
                    "step_number": step_number,
                    "step_name": step.name,
                    "step_description": step.description,
                },
            )
            
            # Execute step with retry logic
            step_result = await self._execute_step_with_retry(
                workflow_id, step, context
            )
            
            # Update context with step result
            context[f"step_{step_number}_result"] = step_result
            
            if self.event_bus:
                await self.event_bus.emit(StateChangeEvent.WORKFLOW_STEP_COMPLETED, {
                    "workflow_id": workflow_id,
                    "step_name": step.name,
                    "step_number": step_number,
                    "total_steps": len(definition.steps),
                })
    
    async def _execute_steps_parallel(
        self,
        workflow_id: str,
        definition: WorkflowDefinition,
        context: Dict[str, Any],
    ) -> None:
        """Execute workflow steps in parallel"""
        tasks = []
        
        for i, step in enumerate(definition.steps):
            task = asyncio.create_task(
                self._execute_step_with_retry(workflow_id, step, context)
            )
            tasks.append((i + 1, step, task))
        
        # Wait for all steps to complete
        for step_number, step, task in tasks:
            try:
                step_result = await task
                context[f"step_{step_number}_result"] = step_result
                
                if self.event_bus:
                    await self.event_bus.emit(StateChangeEvent.WORKFLOW_STEP_COMPLETED, {
                        "workflow_id": workflow_id,
                        "step_name": step.name,
                        "step_number": step_number,
                        "total_steps": len(definition.steps),
                    })
            
            except Exception as e:
                if step.required:
                    raise
                logger.warning(f"Optional step {step.name} failed: {e}")
    
    async def _execute_step_with_retry(
        self,
        workflow_id: str,
        step: WorkflowStep,
        context: Dict[str, Any],
    ) -> Any:
        """Execute a single step with retry logic"""
        for attempt in range(step.retry_count + 1):
            try:
                step.start_time = datetime.utcnow()
                
                # Execute step with timeout
                if asyncio.iscoroutinefunction(step.action):
                    result = await asyncio.wait_for(
                        step.action(context),
                        timeout=step.timeout
                    )
                else:
                    result = step.action(context)
                
                step.end_time = datetime.utcnow()
                step.result = result
                
                logger.debug(f"Step {step.name} completed successfully")
                return result
            
            except Exception as e:
                step.error = str(e)
                
                if attempt < step.retry_count:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Step {step.name} failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Step {step.name} failed after {attempt + 1} attempts: {e}")
                    raise
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id not in self._running_workflows:
            return False
        
        task = self._running_workflows[workflow_id]
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Update workflow state
        await self.workflow_repo.update_workflow_progress(
            workflow_id=workflow_id,
            current_step="cancelled",
            state_data={
                "status": TaskStatus.CANCELLED,
                "cancelled_at": datetime.utcnow().isoformat(),
            },
        )
        
        if self.event_bus:
            await self.event_bus.emit(StateChangeEvent.WORKFLOW_CANCELLED, {
                "workflow_id": workflow_id,
            })
        
        logger.info(f"Cancelled workflow: {workflow_id}")
        return True
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status"""
        workflow = await self.workflow_repo.get_workflow(workflow_id)
        if not workflow:
            return None
        
        is_running = workflow_id in self._running_workflows
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status,
            "current_step": workflow.current_step,
            "progress_percentage": workflow.progress_percentage,
            "completed_steps": workflow.completed_steps,
            "total_steps": workflow.total_steps,
            "is_running": is_running,
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "last_activity_at": workflow.last_activity_at.isoformat(),
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "error_count": workflow.error_count,
            "last_error": workflow.last_error,
        }


class SessionStateManager:
    """Manages test session states and lifecycle"""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        event_bus: Optional[EventBus] = None,
    ):
        self.db_manager = db_manager
        self.event_bus = event_bus
        self.session_repo = SessionRepository(db_manager)
        self._session_locks: Dict[UUID, asyncio.Lock] = {}
    
    async def create_session(
        self,
        name: str,
        url: str,
        project_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> TestSession:
        """Create a new test session"""
        session = await self.session_repo.create_session(
            name=name,
            url=url,
            project_id=project_id,
            **kwargs
        )
        
        if self.event_bus:
            await self.event_bus.emit(StateChangeEvent.SESSION_CREATED, {
                "session_id": str(session.id),
                "name": name,
                "url": url,
                "project_id": str(project_id) if project_id else None,
            })
        
        logger.info(f"Created session: {session.id} ({name})")
        return session
    
    async def start_session(
        self,
        session_id: UUID,
        initial_step: str = "initializing",
    ) -> Optional[TestSession]:
        """Start a test session"""
        async with self._get_session_lock(session_id):
            session = await self.session_repo.update_session_status(
                session_id=session_id,
                status=TaskStatus.RUNNING,
                progress_percentage=0,
                current_step=initial_step,
            )
            
            if session and self.event_bus:
                await self.event_bus.emit(StateChangeEvent.SESSION_STARTED, {
                    "session_id": str(session_id),
                    "initial_step": initial_step,
                })
            
            return session
    
    async def update_session_progress(
        self,
        session_id: UUID,
        progress_percentage: int,
        current_step: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[TestSession]:
        """Update session progress"""
        async with self._get_session_lock(session_id):
            session = await self.session_repo.update_session_status(
                session_id=session_id,
                status=TaskStatus.RUNNING,
                progress_percentage=progress_percentage,
                current_step=current_step,
            )
            
            if session and self.event_bus:
                await self.event_bus.emit(StateChangeEvent.SESSION_PROGRESS, {
                    "session_id": str(session_id),
                    "progress_percentage": progress_percentage,
                    "current_step": current_step,
                    "additional_data": additional_data,
                })
            
            return session
    
    async def complete_session(
        self,
        session_id: UUID,
        results: Optional[Dict[str, Any]] = None,
    ) -> Optional[TestSession]:
        """Mark session as completed"""
        async with self._get_session_lock(session_id):
            session = await self.session_repo.update_session_status(
                session_id=session_id,
                status=TaskStatus.COMPLETED,
                progress_percentage=100,
                current_step="completed",
            )
            
            if session and self.event_bus:
                await self.event_bus.emit(StateChangeEvent.SESSION_COMPLETED, {
                    "session_id": str(session_id),
                    "results": results,
                })
            
            return session
    
    async def fail_session(
        self,
        session_id: UUID,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> Optional[TestSession]:
        """Mark session as failed"""
        async with self._get_session_lock(session_id):
            session = await self.session_repo.update_session_status(
                session_id=session_id,
                status=TaskStatus.FAILED,
                current_step="failed",
                error_message=error_message,
            )
            
            if session and self.event_bus:
                await self.event_bus.emit(StateChangeEvent.SESSION_FAILED, {
                    "session_id": str(session_id),
                    "error_message": error_message,
                    "error_details": error_details,
                })
            
            return session
    
    def _get_session_lock(self, session_id: UUID) -> asyncio.Lock:
        """Get or create a lock for a session"""
        if session_id not in self._session_locks:
            self._session_locks[session_id] = asyncio.Lock()
        return self._session_locks[session_id]
    
    async def cleanup_old_locks(self, max_age_hours: int = 24) -> None:
        """Cleanup old session locks"""
        # Simple implementation - could be enhanced with actual session status checks
        if len(self._session_locks) > 1000:  # Arbitrary limit
            self._session_locks.clear()


class StateManager:
    """Main state management service combining workflow and session management"""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        event_bus: Optional[EventBus] = None,
    ):
        self.db_manager = db_manager
        self.event_bus = event_bus
        self.workflow_manager = WorkflowManager(db_manager, event_bus)
        self.session_manager = SessionStateManager(db_manager, event_bus)
    
    async def initialize(self) -> None:
        """Initialize state management components"""
        await self.db_manager.initialize()
        logger.info("State manager initialized")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all state management components"""
        db_health = await self.db_manager.health_check()
        
        return {
            "state_manager": "healthy",
            "database": db_health,
            "running_workflows": len(self.workflow_manager._running_workflows),
            "session_locks": len(self.session_manager._session_locks),
        }
    
    async def cleanup(self) -> None:
        """Cleanup state management resources"""
        # Cancel all running workflows
        for workflow_id in list(self.workflow_manager._running_workflows.keys()):
            await self.workflow_manager.cancel_workflow(workflow_id)
        
        # Cleanup database connections
        await self.db_manager.cleanup()
        
        logger.info("State manager cleaned up")
