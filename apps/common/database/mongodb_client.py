"""
MongoDB client and models for AI Apps Suite
"""
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from bson import ObjectId


class ExecutionStatus(str, Enum):
    """Execution status enum"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Step execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ExecutionModel(BaseModel):
    """Main execution record model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    app_id: int
    app_name: str
    sub_app_id: Optional[int] = None
    sub_app_name: Optional[str] = None
    user_id: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.RUNNING
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ExecutionStepModel(BaseModel):
    """Step execution record model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    execution_id: str
    step_id: int
    step_name: str
    step_version: str
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ExecutionArtifactModel(BaseModel):
    """Execution artifact model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    execution_id: str
    step_id: Optional[int] = None
    artifact_type: str  # screenshot, log, code, report
    artifact_name: str
    mime_type: str
    size_bytes: int
    storage_type: str  # gridfs, s3, local
    storage_path: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MongoDBClient:
    """MongoDB client for AI Apps Suite"""
    
    def __init__(self, connection_string: Optional[str] = None, database: str = "ai_apps"):
        self.connection_string = connection_string or os.getenv(
            "MONGODB_CONNECTION_STRING", 
            "mongodb://localhost:27017"
        )
        self.database_name = database
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        """Connect to MongoDB"""
        if not self.client:
            self.client = AsyncIOMotorClient(
                self.connection_string,
                maxPoolSize=100,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                retryWrites=True,
                w="majority"
            )
            self.db = self.client[self.database_name]
            
            # Create indexes
            await self._create_indexes()

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()

    async def _create_indexes(self):
        """Create database indexes"""
        # Executions collection indexes
        executions = self.db.executions
        await executions.create_index("execution_id", unique=True)
        await executions.create_index([("app_id", 1), ("sub_app_id", 1)])
        await executions.create_index("user_id")
        await executions.create_index("status")
        await executions.create_index([("started_at", -1)])

        # Execution steps collection indexes
        steps = self.db.execution_steps
        await steps.create_index([("execution_id", 1), ("step_id", 1)], unique=True)
        await steps.create_index("execution_id")
        await steps.create_index("status")
        await steps.create_index("step_name")
        await steps.create_index([("started_at", -1)])

        # Artifacts collection indexes
        artifacts = self.db.execution_artifacts
        await artifacts.create_index([("execution_id", 1), ("step_id", 1)])
        await artifacts.create_index("artifact_type")
        await artifacts.create_index([("created_at", -1)])

        # Metrics collection indexes with TTL
        metrics = self.db.execution_metrics
        await metrics.create_index([("execution_id", 1), ("timestamp", 1)])
        await metrics.create_index("timestamp", expireAfterSeconds=30*24*60*60)  # 30 days TTL

    # Execution methods
    async def create_execution(self, execution: ExecutionModel) -> str:
        """Create a new execution record"""
        result = await self.db.executions.insert_one(
            execution.dict(by_alias=True, exclude_unset=True)
        )
        return execution.execution_id

    async def update_execution(self, execution_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an execution record"""
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.db.executions.update_one(
            {"execution_id": execution_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_execution(self, execution_id: str) -> Optional[ExecutionModel]:
        """Get an execution by ID"""
        doc = await self.db.executions.find_one({"execution_id": execution_id})
        return ExecutionModel(**doc) if doc else None

    async def list_executions(
        self, 
        user_id: Optional[str] = None,
        app_id: Optional[int] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 10,
        skip: int = 0
    ) -> List[ExecutionModel]:
        """List executions with filters"""
        query = {}
        if user_id:
            query["user_id"] = user_id
        if app_id:
            query["app_id"] = app_id
        if status:
            query["status"] = status

        cursor = self.db.executions.find(query).sort("started_at", -1).skip(skip).limit(limit)
        return [ExecutionModel(**doc) async for doc in cursor]

    # Step methods
    async def create_step(self, step: ExecutionStepModel) -> bool:
        """Create a new step execution record"""
        result = await self.db.execution_steps.insert_one(
            step.dict(by_alias=True, exclude_unset=True)
        )
        return result.acknowledged

    async def update_step(
        self, 
        execution_id: str, 
        step_id: int, 
        update_data: Dict[str, Any]
    ) -> bool:
        """Update a step execution record"""
        result = await self.db.execution_steps.update_one(
            {"execution_id": execution_id, "step_id": step_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_step(self, execution_id: str, step_id: int) -> Optional[ExecutionStepModel]:
        """Get a step by execution ID and step ID"""
        doc = await self.db.execution_steps.find_one({
            "execution_id": execution_id,
            "step_id": step_id
        })
        return ExecutionStepModel(**doc) if doc else None

    async def list_steps(self, execution_id: str) -> List[ExecutionStepModel]:
        """List all steps for an execution"""
        cursor = self.db.execution_steps.find(
            {"execution_id": execution_id}
        ).sort("step_id", 1)
        return [ExecutionStepModel(**doc) async for doc in cursor]

    # Artifact methods
    async def create_artifact(self, artifact: ExecutionArtifactModel) -> str:
        """Create a new artifact record"""
        result = await self.db.execution_artifacts.insert_one(
            artifact.dict(by_alias=True, exclude_unset=True)
        )
        return str(result.inserted_id)

    async def list_artifacts(
        self, 
        execution_id: str, 
        step_id: Optional[int] = None
    ) -> List[ExecutionArtifactModel]:
        """List artifacts for an execution"""
        query = {"execution_id": execution_id}
        if step_id is not None:
            query["step_id"] = step_id
        
        cursor = self.db.execution_artifacts.find(query).sort("created_at", -1)
        return [ExecutionArtifactModel(**doc) async for doc in cursor]

    # Analytics methods
    async def get_execution_stats(self, app_id: Optional[int] = None) -> Dict[str, Any]:
        """Get execution statistics"""
        match_stage = {}
        if app_id:
            match_stage["app_id"] = app_id

        pipeline = [
            {"$match": match_stage} if match_stage else {"$match": {}},
            {
                "$group": {
                    "_id": "$app_name",
                    "total": {"$sum": 1},
                    "completed": {
                        "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                    },
                    "failed": {
                        "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                    },
                    "running": {
                        "$sum": {"$cond": [{"$eq": ["$status", "running"]}, 1, 0]}
                    },
                    "avg_duration_ms": {"$avg": "$duration_ms"}
                }
            },
            {
                "$project": {
                    "app_name": "$_id",
                    "total": 1,
                    "completed": 1,
                    "failed": 1,
                    "running": 1,
                    "success_rate": {
                        "$cond": [
                            {"$eq": ["$total", 0]},
                            0,
                            {"$divide": ["$completed", "$total"]}
                        ]
                    },
                    "avg_duration_ms": 1
                }
            }
        ]

        cursor = self.db.executions.aggregate(pipeline)
        return [doc async for doc in cursor]


# Global instance
mongodb_client = MongoDBClient()


async def get_mongodb() -> MongoDBClient:
    """Get MongoDB client instance"""
    if not mongodb_client.client:
        await mongodb_client.connect()
    return mongodb_client