"""
Execution tracking service for storing app execution data in MongoDB
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import traceback
from contextlib import asynccontextmanager

from ..database import (
    MongoDBClient,
    ExecutionModel,
    ExecutionStepModel,
    ExecutionStatus,
    StepStatus,
    get_mongodb
)


class ExecutionTracker:
    """Service for tracking app executions in MongoDB"""
    
    def __init__(self, mongodb_client: Optional[MongoDBClient] = None):
        self.db = mongodb_client
        
    async def ensure_connected(self):
        """Ensure MongoDB is connected"""
        if not self.db:
            self.db = await get_mongodb()

    @asynccontextmanager
    async def track_execution(
        self,
        app_id: int,
        app_name: str,
        sub_app_id: Optional[int] = None,
        sub_app_name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Context manager for tracking an execution"""
        await self.ensure_connected()
        
        # Create execution record
        execution = ExecutionModel(
            app_id=app_id,
            app_name=app_name,
            sub_app_id=sub_app_id,
            sub_app_name=sub_app_name,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        execution_id = await self.db.create_execution(execution)
        start_time = datetime.now(timezone.utc)
        
        try:
            yield execution_id
            
            # Update execution as completed
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            await self.db.update_execution(execution_id, {
                "status": ExecutionStatus.COMPLETED,
                "completed_at": end_time,
                "duration_ms": duration_ms
            })
            
        except Exception as e:
            # Update execution as failed
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            await self.db.update_execution(execution_id, {
                "status": ExecutionStatus.FAILED,
                "completed_at": end_time,
                "duration_ms": duration_ms,
                "error": str(e)
            })
            raise

    @asynccontextmanager
    async def track_step(
        self,
        execution_id: str,
        step_id: int,
        step_name: str,
        step_version: str = "1.0.0",
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Context manager for tracking a step execution"""
        await self.ensure_connected()
        
        # Create step record
        step = ExecutionStepModel(
            execution_id=execution_id,
            step_id=step_id,
            step_name=step_name,
            step_version=step_version,
            status=StepStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
            input=input_data or {},
            metadata=metadata or {}
        )
        
        await self.db.create_step(step)
        start_time = datetime.now(timezone.utc)
        
        try:
            # Yield a function to capture output
            output_data = {}
            
            def set_output(data: Dict[str, Any]):
                output_data.update(data)
            
            yield set_output
            
            # Update step as completed
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            await self.db.update_step(execution_id, step_id, {
                "status": StepStatus.COMPLETED,
                "completed_at": end_time,
                "duration_ms": duration_ms,
                "output": output_data
            })
            
        except Exception as e:
            # Update step as failed
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            await self.db.update_step(execution_id, step_id, {
                "status": StepStatus.FAILED,
                "completed_at": end_time,
                "duration_ms": duration_ms,
                "error": str(e),
                "output": output_data if output_data else None
            })
            raise

    async def log_artifact(
        self,
        execution_id: str,
        artifact_type: str,
        artifact_name: str,
        content: bytes,
        step_id: Optional[int] = None,
        mime_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an artifact (screenshot, log, etc.)"""
        await self.ensure_connected()
        
        # TODO: Implement GridFS storage for large files
        # For now, we'll just store the metadata
        
        from ..database import ExecutionArtifactModel
        
        artifact = ExecutionArtifactModel(
            execution_id=execution_id,
            step_id=step_id,
            artifact_type=artifact_type,
            artifact_name=artifact_name,
            mime_type=mime_type,
            size_bytes=len(content),
            storage_type="gridfs",  # Will implement GridFS later
            storage_path=f"gridfs://artifacts/{execution_id}/{artifact_name}",
            metadata=metadata or {}
        )
        
        return await self.db.create_artifact(artifact)

    async def get_execution_history(
        self,
        user_id: Optional[str] = None,
        app_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get execution history with optional filters"""
        await self.ensure_connected()
        
        executions = await self.db.list_executions(
            user_id=user_id,
            app_id=app_id,
            limit=limit
        )
        
        results = []
        for execution in executions:
            # Get steps for each execution
            steps = await self.db.list_steps(execution.execution_id)
            
            results.append({
                "execution": execution.dict(),
                "steps": [step.dict() for step in steps]
            })
        
        return results

    async def get_execution_details(self, execution_id: str) -> Dict[str, Any]:
        """Get detailed execution information"""
        await self.ensure_connected()
        
        execution = await self.db.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        steps = await self.db.list_steps(execution_id)
        artifacts = await self.db.list_artifacts(execution_id)
        
        return {
            "execution": execution.dict(),
            "steps": [step.dict() for step in steps],
            "artifacts": [artifact.dict() for artifact in artifacts]
        }


# Global instance
execution_tracker = ExecutionTracker()


async def get_execution_tracker() -> ExecutionTracker:
    """Get execution tracker instance"""
    await execution_tracker.ensure_connected()
    return execution_tracker