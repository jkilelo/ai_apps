"""
MongoDB Database Connection and Configuration for UI Web Automation Testing
Handles connection to MongoDB and provides comprehensive session management

Each UI session stores the complete web automation testing pipeline results:
1. Browser Setup Result
2. Element Extraction Result
3. AI Enrichment Result
4. Test Generation Result
5. Code Generation Result

Sessions are keyed by URL netloc for efficient lookup and resumption.
"""

import os
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import urlparse
from enum import Enum
from pymongo import MongoClient, ReturnDocument
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, DuplicateKeyError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='../.env')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.getenv('MONGO_LOCAL_URL')

client = MongoClient(mongo_url)
db = client['AI']
collection = db['ui_sessions']

# Create unique index on netloc to prevent duplicates
collection.create_index("netloc", unique=True, sparse=True)


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class PipelineStep(str, Enum):
    """Pipeline step identifiers"""
    BROWSER_SETUP = "browser_setup"
    ELEMENT_EXTRACTION = "element_extraction"
    AI_ENRICHMENT = "ai_enrichment"
    TEST_GENERATION = "test_generation"
    CODE_GENERATION = "code_generation"


class StepStatus(str, Enum):
    """Status of each pipeline step"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"  # Loaded from cache/db


class LoadStrategy(str, Enum):
    """Strategy for loading session data"""
    FRESH = "fresh"  # Always execute fresh
    CACHED = "cached"  # Always use cached if available
    AUTO = "auto"  # Use cached if recent, else fresh


# ============================================================================
# DATA MODELS (Using Pydantic V2)
# ============================================================================

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List


class StepResult(BaseModel):
    """Container for a single pipeline step result using Pydantic v2"""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,  # Automatically convert enums to values
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    step: PipelineStep
    status: StepStatus = StepStatus.NOT_STARTED
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[datetime] = None
    duration: float = 0.0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    @field_validator('step', mode='before')
    @classmethod
    def validate_step(cls, v):
        """Convert string to PipelineStep enum if needed"""
        if isinstance(v, str):
            return PipelineStep(v)
        return v

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        """Convert string to StepStatus enum if needed"""
        if isinstance(v, str):
            return StepStatus(v)
        return v


class UISession(BaseModel):
    """Complete UI testing session with all pipeline steps using Pydantic v2"""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=False,  # Keep enums as objects for internal use
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    # Core fields
    url: str
    netloc: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = None

    # Pipeline steps
    steps: Dict[PipelineStep, StepResult] = Field(default_factory=dict)

    # Metadata
    page_title: Optional[str] = None
    total_elements: int = 0
    interactive_elements: int = 0
    test_scenarios_count: int = 0
    frameworks: List[str] = Field(default_factory=list)
    last_successful_step: Optional[PipelineStep] = None
    is_complete: bool = False

    def model_post_init(self, __context) -> None:
        """Initialize after validation"""
        # Set netloc from URL
        if not self.netloc and self.url:
            self.netloc = urlparse(self.url).netloc

        # Initialize steps if empty
        if not self.steps:
            self.steps = {
                PipelineStep.BROWSER_SETUP: StepResult(step=PipelineStep.BROWSER_SETUP),
                PipelineStep.ELEMENT_EXTRACTION: StepResult(step=PipelineStep.ELEMENT_EXTRACTION),
                PipelineStep.AI_ENRICHMENT: StepResult(step=PipelineStep.AI_ENRICHMENT),
                PipelineStep.TEST_GENERATION: StepResult(step=PipelineStep.TEST_GENERATION),
                PipelineStep.CODE_GENERATION: StepResult(step=PipelineStep.CODE_GENERATION)
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        # Use model_dump with custom serialization
        data = self.model_dump(mode='json')

        # Add MongoDB _id field
        data["_id"] = self.netloc

        # Convert step enums to values for storage
        if "steps" in data:
            steps_dict = {}
            for step_key, step_data in data["steps"].items():
                # Ensure step key is string
                key = step_key.value if hasattr(step_key, 'value') else str(step_key)
                steps_dict[key] = step_data
            data["steps"] = steps_dict

        # Convert last_successful_step enum to value
        if self.last_successful_step:
            data["last_successful_step"] = self.last_successful_step.value

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UISession':
        """Create from MongoDB document"""
        # Remove _id field if present
        data = data.copy()
        data.pop("_id", None)

        # Convert steps dictionary keys from strings to enums
        if "steps" in data and isinstance(data["steps"], dict):
            converted_steps = {}
            for step_key, step_data in data["steps"].items():
                # Convert string key to PipelineStep enum
                try:
                    enum_key = PipelineStep(step_key)
                    # Validate step_data to StepResult
                    if isinstance(step_data, dict):
                        converted_steps[enum_key] = StepResult(**step_data)
                    else:
                        converted_steps[enum_key] = step_data
                except (ValueError, KeyError):
                    logger.warning(f"Unknown step key: {step_key}")
            data["steps"] = converted_steps

        # Convert last_successful_step from string to enum
        if "last_successful_step" in data and isinstance(data["last_successful_step"], str):
            try:
                data["last_successful_step"] = PipelineStep(data["last_successful_step"])
            except ValueError:
                data["last_successful_step"] = None

        # Create instance using Pydantic validation
        return cls.model_validate(data)


# ============================================================================
# CORE DATABASE FUNCTIONS
# ============================================================================

def get_ui_session(url: str, create_if_missing: bool = True) -> Optional[UISession]:
    """
    Get UI session for a URL (keyed by netloc)

    Args:
        url: Full URL to get session for
        create_if_missing: If True, create new session if not exists

    Returns:
        UISession object or None if not found and create_if_missing=False
    """
    try:
        netloc = urlparse(url).netloc
        if not netloc:
            logger.error(f"Invalid URL: {url}")
            return None

        # Try to find existing session
        doc = collection.find_one({"_id": netloc})

        if doc:
            logger.info(f"Found existing session for {netloc}")
            return UISession.from_dict(doc)
        elif create_if_missing:
            logger.info(f"Creating new session for {netloc}")
            session = UISession(url=url)  # Using Pydantic constructor
            save_ui_session(session)
            return session
        else:
            logger.info(f"No session found for {netloc}")
            return None

    except Exception as e:
        logger.error(f"Error getting UI session: {e}")
        return None


def save_ui_session(session: UISession) -> bool:
    """
    Save or update UI session in database

    Args:
        session: UISession object to save

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        session.updated_at = datetime.now()
        doc = session.to_dict()

        # Use replace_one with upsert to handle both insert and update
        result = collection.replace_one(
            {"_id": session.netloc},
            doc,
            upsert=True
        )

        if result.acknowledged:
            logger.info(f"Saved session for {session.netloc} (modified: {result.modified_count}, upserted: {result.upserted_id})")
            return True
        else:
            logger.error(f"Failed to save session for {session.netloc}")
            return False

    except Exception as e:
        logger.error(f"Error saving UI session: {e}")
        return False


def delete_ui_session(url: str) -> bool:
    """
    Delete UI session for a URL

    Args:
        url: URL to delete session for

    Returns:
        True if deleted, False otherwise
    """
    try:
        netloc = urlparse(url).netloc
        result = collection.delete_one({"_id": netloc})

        if result.deleted_count > 0:
            logger.info(f"Deleted session for {netloc}")
            return True
        else:
            logger.warning(f"No session found to delete for {netloc}")
            return False

    except Exception as e:
        logger.error(f"Error deleting UI session: {e}")
        return False


# ============================================================================
# STEP-SPECIFIC SAVE FUNCTIONS
# ============================================================================

def save_step_result(
    url: str,
    step: PipelineStep,
    data: Dict[str, Any],
    status: StepStatus = StepStatus.COMPLETED,
    duration: float = 0.0,
    errors: List[str] = None,
    warnings: List[str] = None
) -> bool:
    """
    Save result for a specific pipeline step

    Args:
        url: URL of the session
        step: Pipeline step to save
        data: Step result data
        status: Step execution status
        duration: Execution duration in seconds
        errors: List of errors encountered
        warnings: List of warnings

    Returns:
        True if saved successfully
    """
    try:
        session = get_ui_session(url, create_if_missing=True)
        if not session:
            return False

        # Update step result
        step_result = session.steps[step]
        step_result.status = status
        step_result.data = data
        step_result.timestamp = datetime.now()
        step_result.duration = duration
        step_result.errors = errors or []
        step_result.warnings = warnings or []

        # Update session metadata based on step
        if step == PipelineStep.BROWSER_SETUP and data:
            session.page_title = data.get("page_title")
            session.session_id = data.get("session_id")

        elif step == PipelineStep.ELEMENT_EXTRACTION and data:
            session.total_elements = data.get("total_elements", 0)
            session.interactive_elements = data.get("interactive_elements", 0)

        elif step == PipelineStep.TEST_GENERATION and data:
            session.test_scenarios_count = data.get("total_scenarios", 0)

        elif step == PipelineStep.CODE_GENERATION and data:
            session.frameworks = data.get("frameworks", [])

        # Update last successful step
        if status == StepStatus.COMPLETED:
            session.last_successful_step = step

            # Check if all steps are complete
            all_complete = all(
                s.status == StepStatus.COMPLETED
                for s in session.steps.values()
            )
            session.is_complete = all_complete

        # Save to database
        return save_ui_session(session)

    except Exception as e:
        logger.error(f"Error saving step result: {e}")
        return False


def save_browser_setup(url: str, browser_result: Dict[str, Any]) -> bool:
    """Save browser setup result"""
    return save_step_result(
        url=url,
        step=PipelineStep.BROWSER_SETUP,
        data=browser_result,
        duration=browser_result.get("duration", 0.0)
    )


def save_element_extraction(url: str, extraction_result: Dict[str, Any]) -> bool:
    """Save element extraction result"""
    return save_step_result(
        url=url,
        step=PipelineStep.ELEMENT_EXTRACTION,
        data=extraction_result,
        duration=extraction_result.get("extraction_time", 0.0)
    )


def save_ai_enrichment(url: str, enrichment_result: Dict[str, Any]) -> bool:
    """Save AI enrichment result"""
    return save_step_result(
        url=url,
        step=PipelineStep.AI_ENRICHMENT,
        data=enrichment_result,
        duration=enrichment_result.get("enrichment_time", 0.0)
    )


def save_test_generation(url: str, test_result: Dict[str, Any]) -> bool:
    """Save test generation result"""
    return save_step_result(
        url=url,
        step=PipelineStep.TEST_GENERATION,
        data=test_result,
        duration=test_result.get("generation_time", 0.0)
    )


def save_code_generation(url: str, code_result: Dict[str, Any]) -> bool:
    """Save code generation result"""
    return save_step_result(
        url=url,
        step=PipelineStep.CODE_GENERATION,
        data=code_result,
        duration=code_result.get("generation_time", 0.0)
    )


# ============================================================================
# STEP-SPECIFIC LOAD FUNCTIONS WITH FALLBACK
# ============================================================================

def load_step_result(
    url: str,
    step: PipelineStep,
    strategy: LoadStrategy = LoadStrategy.AUTO,
    max_age_hours: int = 24
) -> Optional[Dict[str, Any]]:
    """
    Load result for a specific pipeline step with fallback strategy

    Args:
        url: URL of the session
        step: Pipeline step to load
        strategy: Load strategy (FRESH, CACHED, AUTO)
        max_age_hours: Maximum age in hours for AUTO strategy

    Returns:
        Step result data or None if not available
    """
    try:
        if strategy == LoadStrategy.FRESH:
            logger.info(f"FRESH strategy: Skipping cached data for {step.value}")
            return None

        session = get_ui_session(url, create_if_missing=False)
        if not session:
            logger.info(f"No session found for {url}")
            return None

        step_result = session.steps.get(step)
        if not step_result or step_result.status != StepStatus.COMPLETED:
            logger.info(f"Step {step.value} not completed or not found")
            return None

        # Check age for AUTO strategy
        if strategy == LoadStrategy.AUTO and step_result.timestamp:
            age = datetime.now() - step_result.timestamp
            age_hours = age.total_seconds() / 3600

            if age_hours > max_age_hours:
                logger.info(f"Step {step.value} data is {age_hours:.1f} hours old, exceeds max age of {max_age_hours} hours")
                return None

        logger.info(f"Loading cached data for step {step.value}")
        return step_result.data

    except Exception as e:
        logger.error(f"Error loading step result: {e}")
        return None


def load_browser_setup(url: str, strategy: LoadStrategy = LoadStrategy.AUTO) -> Optional[Dict[str, Any]]:
    """Load cached browser setup result"""
    return load_step_result(url, PipelineStep.BROWSER_SETUP, strategy)


def load_element_extraction(url: str, strategy: LoadStrategy = LoadStrategy.AUTO) -> Optional[Dict[str, Any]]:
    """Load cached element extraction result"""
    return load_step_result(url, PipelineStep.ELEMENT_EXTRACTION, strategy)


def load_ai_enrichment(url: str, strategy: LoadStrategy = LoadStrategy.AUTO) -> Optional[Dict[str, Any]]:
    """Load cached AI enrichment result"""
    return load_step_result(url, PipelineStep.AI_ENRICHMENT, strategy)


def load_test_generation(url: str, strategy: LoadStrategy = LoadStrategy.AUTO) -> Optional[Dict[str, Any]]:
    """Load cached test generation result"""
    return load_step_result(url, PipelineStep.TEST_GENERATION, strategy)


def load_code_generation(url: str, strategy: LoadStrategy = LoadStrategy.AUTO) -> Optional[Dict[str, Any]]:
    """Load cached code generation result"""
    return load_step_result(url, PipelineStep.CODE_GENERATION, strategy)


# ============================================================================
# SESSION RECOVERY AND RESUMPTION
# ============================================================================

def get_resume_point(url: str) -> Optional[PipelineStep]:
    """
    Get the next step to resume from for a partially completed session

    Args:
        url: URL to check

    Returns:
        Next step to execute or None if session is complete
    """
    try:
        session = get_ui_session(url, create_if_missing=False)
        if not session:
            return PipelineStep.BROWSER_SETUP

        # If session is complete, no need to resume
        if session.is_complete:
            logger.info(f"Session for {url} is already complete")
            return None

        # Find the first incomplete step
        step_order = [
            PipelineStep.BROWSER_SETUP,
            PipelineStep.ELEMENT_EXTRACTION,
            PipelineStep.AI_ENRICHMENT,
            PipelineStep.TEST_GENERATION,
            PipelineStep.CODE_GENERATION
        ]

        for step in step_order:
            step_result = session.steps.get(step)
            if not step_result or step_result.status != StepStatus.COMPLETED:
                logger.info(f"Resume point for {url}: {step.value}")
                return step

        # All steps complete but is_complete flag not set
        session.is_complete = True
        save_ui_session(session)
        return None

    except Exception as e:
        logger.error(f"Error getting resume point: {e}")
        return PipelineStep.BROWSER_SETUP


def mark_step_in_progress(url: str, step: PipelineStep) -> bool:
    """
    Mark a step as in progress to handle concurrent executions

    Args:
        url: URL of the session
        step: Step to mark as in progress

    Returns:
        True if marked successfully
    """
    try:
        session = get_ui_session(url, create_if_missing=True)
        if not session:
            return False

        session.steps[step].status = StepStatus.IN_PROGRESS
        session.steps[step].timestamp = datetime.now()
        return save_ui_session(session)

    except Exception as e:
        logger.error(f"Error marking step in progress: {e}")
        return False


def mark_step_failed(
    url: str,
    step: PipelineStep,
    error_message: str = None
) -> bool:
    """
    Mark a step as failed

    Args:
        url: URL of the session
        step: Step that failed
        error_message: Optional error message

    Returns:
        True if marked successfully
    """
    try:
        session = get_ui_session(url, create_if_missing=True)
        if not session:
            return False

        step_result = session.steps[step]
        step_result.status = StepStatus.FAILED
        step_result.timestamp = datetime.now()
        if error_message:
            step_result.errors.append(error_message)

        return save_ui_session(session)

    except Exception as e:
        logger.error(f"Error marking step as failed: {e}")
        return False


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def list_all_sessions(
    limit: int = 100,
    skip: int = 0,
    filter_complete: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """
    List all UI sessions with optional filtering

    Args:
        limit: Maximum number of sessions to return
        skip: Number of sessions to skip (for pagination)
        filter_complete: If True, only return complete sessions; if False, only incomplete

    Returns:
        List of session summaries
    """
    try:
        query = {}
        if filter_complete is not None:
            query["is_complete"] = filter_complete

        cursor = collection.find(query).skip(skip).limit(limit)
        sessions = []

        for doc in cursor:
            session_summary = {
                "netloc": doc.get("_id"),
                "url": doc.get("url"),
                "page_title": doc.get("page_title"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
                "is_complete": doc.get("is_complete", False),
                "last_successful_step": doc.get("last_successful_step"),
                "total_elements": doc.get("total_elements", 0),
                "test_scenarios_count": doc.get("test_scenarios_count", 0)
            }
            sessions.append(session_summary)

        logger.info(f"Found {len(sessions)} sessions")
        return sessions

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return []


def get_session_summary(url: str) -> Optional[Dict[str, Any]]:
    """
    Get a summary of a session's current state

    Args:
        url: URL to get summary for

    Returns:
        Session summary or None if not found
    """
    try:
        session = get_ui_session(url, create_if_missing=False)
        if not session:
            return None

        # Calculate completion percentage
        completed_steps = sum(
            1 for s in session.steps.values()
            if s.status == StepStatus.COMPLETED
        )
        total_steps = len(session.steps)
        completion_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0

        # Get step statuses
        step_statuses = {}
        for step in PipelineStep:
            step_result = session.steps.get(step)
            if step_result:
                step_statuses[step.value] = {
                    "status": step_result.status.value if hasattr(step_result.status, 'value') else str(step_result.status),
                    "timestamp": step_result.timestamp,
                    "duration": step_result.duration,
                    "has_data": bool(step_result.data),
                    "errors": len(step_result.errors) if step_result.errors else 0
                }

        return {
            "url": session.url,
            "netloc": session.netloc,
            "page_title": session.page_title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "is_complete": session.is_complete,
            "completion_percentage": completion_percentage,
            "last_successful_step": session.last_successful_step.value if session.last_successful_step else None,
            "total_elements": session.total_elements,
            "interactive_elements": session.interactive_elements,
            "test_scenarios_count": session.test_scenarios_count,
            "frameworks": session.frameworks,
            "step_statuses": step_statuses
        }

    except Exception as e:
        logger.error(f"Error getting session summary: {e}")
        return None


def clear_session_cache(url: str, steps: List[PipelineStep] = None) -> bool:
    """
    Clear cached data for specific steps or entire session

    Args:
        url: URL to clear cache for
        steps: Specific steps to clear, or None to clear all

    Returns:
        True if cleared successfully
    """
    try:
        session = get_ui_session(url, create_if_missing=False)
        if not session:
            logger.warning(f"No session found for {url}")
            return False

        steps_to_clear = steps or list(PipelineStep)

        for step in steps_to_clear:
            if step in session.steps:
                session.steps[step] = StepResult(step=step)  # Using Pydantic constructor
                logger.info(f"Cleared cache for step {step.value}")

        # Reset metadata
        session.is_complete = False
        session.last_successful_step = None

        return save_ui_session(session)

    except Exception as e:
        logger.error(f"Error clearing session cache: {e}")
        return False


def export_session_to_json(url: str, filepath: str = None) -> Optional[str]:
    """
    Export session data to JSON file

    Args:
        url: URL to export
        filepath: Optional filepath, defaults to netloc_timestamp.json

    Returns:
        Filepath if exported successfully, None otherwise
    """
    try:
        session = get_ui_session(url, create_if_missing=False)
        if not session:
            logger.warning(f"No session found for {url}")
            return None

        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"{session.netloc}_{timestamp}.json"

        data = session.to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Exported session to {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Error exporting session: {e}")
        return None


def import_session_from_json(filepath: str, overwrite: bool = False) -> bool:
    """
    Import session data from JSON file

    Args:
        filepath: Path to JSON file
        overwrite: If True, overwrite existing session

    Returns:
        True if imported successfully
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        netloc = data.get("netloc")
        if not netloc:
            logger.error("No netloc found in JSON data")
            return False

        # Check if session exists
        existing = collection.find_one({"_id": netloc})
        if existing and not overwrite:
            logger.warning(f"Session for {netloc} already exists, use overwrite=True to replace")
            return False

        # Create session from data
        session = UISession.from_dict(data)
        return save_ui_session(session)

    except Exception as e:
        logger.error(f"Error importing session: {e}")
        return False


def get_statistics() -> Dict[str, Any]:
    """
    Get statistics about all sessions in the database

    Returns:
        Dictionary with statistics
    """
    try:
        total_sessions = collection.count_documents({})
        complete_sessions = collection.count_documents({"is_complete": True})
        incomplete_sessions = collection.count_documents({"is_complete": False})

        # Get step statistics
        pipeline_steps = list(PipelineStep)
        step_stats = {}

        for step in pipeline_steps:
            step_key = f"steps.{step.value}.status"
            completed = collection.count_documents({step_key: StepStatus.COMPLETED.value})
            failed = collection.count_documents({step_key: StepStatus.FAILED.value})
            in_progress = collection.count_documents({step_key: StepStatus.IN_PROGRESS.value})

            step_stats[step.value] = {
                "completed": completed,
                "failed": failed,
                "in_progress": in_progress
            }

        return {
            "total_sessions": total_sessions,
            "complete_sessions": complete_sessions,
            "incomplete_sessions": incomplete_sessions,
            "completion_rate": (complete_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "step_statistics": step_stats
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {}


