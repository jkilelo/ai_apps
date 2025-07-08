"""
MongoDB client for standalone v1 application
"""
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from bson import ObjectId


class StepStatus(str, Enum):
    """Step execution status enum"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(cls, handler(ObjectId))

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema


class WebAutomationSession(BaseModel):
    """Web automation session model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Step 1: Extract Elements
    extract_elements_input: Optional[str] = None
    extract_elements_output: Optional[List[Dict[str, Any]]] = None
    extract_elements_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 2: Generate Gherkin Tests
    generate_gherkin_input: Optional[str] = None
    generate_gherkin_output: Optional[List[Dict[str, Any]]] = None
    generate_gherkin_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 3: Generate Python Code
    generate_python_input: Optional[str] = None
    generate_python_output: Optional[str] = None
    generate_python_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 4: Execute Python Code
    execute_python_input: Optional[str] = None
    execute_python_output: Optional[str] = None
    execute_python_status: StepStatus = StepStatus.NOT_STARTED

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DataProfilingSession(BaseModel):
    """Data profiling session model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Step 1: Generate Profiling Suggestions
    profiling_suggestions_input: Optional[Dict[str, Any]] = None
    profiling_suggestions_output: Optional[List[Dict[str, Any]]] = None
    profiling_suggestions_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 2: Generate Profiling Test Cases
    profiling_testcases_input: Optional[List[Dict[str, Any]]] = None
    profiling_testcases_output: Optional[List[Dict[str, Any]]] = None
    profiling_testcases_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 3: Generate PySpark Code
    generate_pyspark_input: Optional[List[Dict[str, Any]]] = None
    generate_pyspark_output: Optional[str] = None
    generate_pyspark_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 4: Execute PySpark Code
    execute_pyspark_input: Optional[str] = None
    execute_pyspark_output: Optional[str] = None
    execute_pyspark_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 5: Generate DQ Suggestions
    dq_suggestions_input: Optional[str] = None
    dq_suggestions_output: Optional[List[Dict[str, Any]]] = None
    dq_suggestions_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 6: Generate DQ Tests
    dq_tests_input: Optional[List[Dict[str, Any]]] = None
    dq_tests_output: Optional[List[Dict[str, Any]]] = None
    dq_tests_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 7: Generate PySpark DQ Code
    generate_pyspark_dq_input: Optional[List[Dict[str, Any]]] = None
    generate_pyspark_dq_output: Optional[str] = None
    generate_pyspark_dq_status: StepStatus = StepStatus.NOT_STARTED
    
    # Step 8: Execute PySpark DQ Code
    execute_pyspark_dq_input: Optional[str] = None
    execute_pyspark_dq_output: Optional[str] = None
    execute_pyspark_dq_status: StepStatus = StepStatus.NOT_STARTED

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MongoDBClient:
    """MongoDB client for v1 standalone app"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv(
            "MONGODB_CONNECTION_STRING", 
            "mongodb://ai_apps:ai_apps123@localhost:27017/v1?authSource=admin"
        )
        self.database_name = "v1"  # v1 database as specified
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
        # Web automation sessions
        web_sessions = self.db.web_automation_sessions
        await web_sessions.create_index("session_id", unique=True)
        await web_sessions.create_index([("created_at", -1)])
        
        # Data profiling sessions
        data_sessions = self.db.data_profiling_sessions
        await data_sessions.create_index("session_id", unique=True)
        await data_sessions.create_index([("created_at", -1)])

    # Web Automation methods
    async def create_web_session(self) -> str:
        """Create a new web automation session"""
        session = WebAutomationSession()
        await self.db.web_automation_sessions.insert_one(
            session.dict(by_alias=True, exclude_unset=True)
        )
        return session.session_id

    async def update_web_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a web automation session"""
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.db.web_automation_sessions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_web_session(self, session_id: str) -> Optional[WebAutomationSession]:
        """Get a web automation session by ID"""
        doc = await self.db.web_automation_sessions.find_one({"session_id": session_id})
        return WebAutomationSession(**doc) if doc else None

    async def list_web_sessions(self, limit: int = 10, skip: int = 0) -> List[WebAutomationSession]:
        """List web automation sessions"""
        cursor = self.db.web_automation_sessions.find().sort("created_at", -1).skip(skip).limit(limit)
        return [WebAutomationSession(**doc) async for doc in cursor]

    # Data Profiling methods
    async def create_data_session(self) -> str:
        """Create a new data profiling session"""
        session = DataProfilingSession()
        await self.db.data_profiling_sessions.insert_one(
            session.dict(by_alias=True, exclude_unset=True)
        )
        return session.session_id

    async def update_data_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a data profiling session"""
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.db.data_profiling_sessions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_data_session(self, session_id: str) -> Optional[DataProfilingSession]:
        """Get a data profiling session by ID"""
        doc = await self.db.data_profiling_sessions.find_one({"session_id": session_id})
        return DataProfilingSession(**doc) if doc else None

    async def list_data_sessions(self, limit: int = 10, skip: int = 0) -> List[DataProfilingSession]:
        """List data profiling sessions"""
        cursor = self.db.data_profiling_sessions.find().sort("created_at", -1).skip(skip).limit(limit)
        return [DataProfilingSession(**doc) async for doc in cursor]


# Global instance
mongodb_client = MongoDBClient()


async def get_mongodb() -> MongoDBClient:
    """Get MongoDB client instance"""
    if not mongodb_client.client:
        await mongodb_client.connect()
    return mongodb_client