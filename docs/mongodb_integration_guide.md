# MongoDB Integration Guide

This guide explains how to integrate MongoDB tracking into existing and new apps in the AI Apps Suite.

## Quick Start

### 1. Environment Setup

Add MongoDB connection string to your `.env` file:

```env
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=ai_apps
```

### 2. Basic Integration

For any app execution, wrap your workflow with the execution tracker:

```python
from apps.common.services.execution_tracker import get_execution_tracker

async def your_app_workflow(input_data):
    tracker = await get_execution_tracker()
    
    # Track the main execution
    async with tracker.track_execution(
        app_id=1,  # Your app ID from apps_map.json
        app_name="your_app_name",
        user_id=user_id,  # Optional user identifier
        metadata={"any": "additional", "info": "here"}
    ) as execution_id:
        
        # Track individual steps
        async with tracker.track_step(
            execution_id=execution_id,
            step_id=1,
            step_name="step_name_from_apps_map",
            input_data=input_data
        ) as set_output:
            
            # Your step logic here
            result = await process_step(input_data)
            
            # Set the output for MongoDB storage
            set_output(result)
```

## Integration Patterns

### 1. FastAPI Router Integration

Example for UI Web Auto Testing element extraction:

```python
from fastapi import APIRouter, BackgroundTasks, Request
from apps.common.services.execution_tracker import get_execution_tracker

router = APIRouter()

@router.post("/process")
async def process_data(
    request: YourRequestModel,
    background_tasks: BackgroundTasks,
    req: Request
):
    # Get user info if available
    user_id = getattr(req.state, "user_id", None)
    
    # Get tracker
    tracker = await get_execution_tracker()
    
    # Create execution
    async with tracker.track_execution(
        app_id=2,
        app_name="ui_web_auto_testing",
        user_id=user_id,
        metadata={
            "endpoint": req.url.path,
            "ip_address": req.client.host
        }
    ) as execution_id:
        
        # Add background task with execution_id
        background_tasks.add_task(
            process_in_background,
            execution_id=execution_id,
            data=request.dict()
        )
        
        return {"execution_id": execution_id, "status": "started"}
```

### 2. Background Task Pattern

```python
async def process_in_background(execution_id: str, data: dict):
    tracker = await get_execution_tracker()
    
    try:
        # Step 1
        async with tracker.track_step(
            execution_id=execution_id,
            step_id=1,
            step_name="data_extraction",
            input_data=data
        ) as set_output:
            
            result = await extract_data(data)
            set_output(result)
        
        # Step 2
        async with tracker.track_step(
            execution_id=execution_id,
            step_id=2,
            step_name="data_processing",
            input_data=result
        ) as set_output:
            
            processed = await process_data(result)
            set_output(processed)
            
    except Exception as e:
        # Errors are automatically tracked
        logger.error(f"Background task failed: {e}")
        raise
```

### 3. Artifact Storage

Store screenshots, logs, or other artifacts:

```python
# Store a screenshot
await tracker.log_artifact(
    execution_id=execution_id,
    step_id=1,
    artifact_type="screenshot",
    artifact_name="page_screenshot.png",
    content=screenshot_bytes,
    mime_type="image/png",
    metadata={
        "url": "https://example.com",
        "timestamp": datetime.utcnow().isoformat()
    }
)

# Store generated code
await tracker.log_artifact(
    execution_id=execution_id,
    step_id=2,
    artifact_type="code",
    artifact_name="generated_test.py",
    content=code_content.encode(),
    mime_type="text/x-python",
    metadata={
        "language": "python",
        "framework": "pytest"
    }
)
```

## API Endpoints

### 1. Execution History Endpoint

Add to your router:

```python
@router.get("/history")
async def get_execution_history(
    req: Request,
    limit: int = 10,
    app_id: Optional[int] = None
):
    user_id = getattr(req.state, "user_id", None)
    tracker = await get_execution_tracker()
    
    history = await tracker.get_execution_history(
        user_id=user_id,
        app_id=app_id,
        limit=limit
    )
    
    return {"history": history, "count": len(history)}
```

### 2. Execution Details Endpoint

```python
@router.get("/execution/{execution_id}")
async def get_execution_details(execution_id: str):
    tracker = await get_execution_tracker()
    
    try:
        details = await tracker.get_execution_details(execution_id)
        return details
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## Migration Steps

### For Existing Apps

1. **Identify App Structure**
   - Find app_id and sub_app_id from `apps_map.json`
   - List all steps and their dependencies

2. **Update Routers**
   - Add execution tracking to main endpoints
   - Pass execution_id to background tasks

3. **Update Step Functions**
   - Wrap each step with `track_step`
   - Call `set_output` with results

4. **Test Integration**
   - Run the example script: `python examples/mongodb_integration_example.py`
   - Verify data in MongoDB

### For New Apps

1. **Design Schema First**
   - Define input/output structures
   - Plan step dependencies

2. **Implement with Tracking**
   - Use tracking from the start
   - Follow patterns above

3. **Add History Endpoints**
   - Include execution history API
   - Add detail retrieval endpoints

## Best Practices

### 1. Consistent Naming
- Use exact step names from `apps_map.json`
- Keep app_id and sub_app_id consistent

### 2. Error Handling
- Let context managers handle errors
- Don't catch exceptions within `track_step`

### 3. Output Structure
- Always call `set_output` even with empty results
- Use consistent field names across steps

### 4. Metadata Usage
- Add relevant context (user agent, IP, etc.)
- Include performance metrics when available

### 5. Artifact Management
- Store large files as artifacts, not in output
- Use appropriate artifact types
- Add descriptive metadata

## Monitoring Queries

### Check Recent Failures
```javascript
db.executions.find({
  status: "failed",
  started_at: { $gte: new Date(Date.now() - 24*60*60*1000) }
}).sort({ started_at: -1 })
```

### Get App Performance
```javascript
db.executions.aggregate([
  { $match: { app_name: "ui_web_auto_testing" } },
  { $group: {
    _id: null,
    avg_duration: { $avg: "$duration_ms" },
    success_rate: {
      $avg: { $cond: [{ $eq: ["$status", "completed"] }, 1, 0] }
    }
  }}
])
```

### Find Long-Running Steps
```javascript
db.execution_steps.find({
  duration_ms: { $gt: 30000 }  // > 30 seconds
}).sort({ duration_ms: -1 }).limit(10)
```

## Troubleshooting

### Connection Issues
- Verify MongoDB is running: `mongosh --eval "db.adminCommand('ping')"`
- Check connection string in `.env`
- Ensure network connectivity

### Missing Data
- Verify `set_output` is called
- Check step_id matches apps_map.json
- Look for errors in execution record

### Performance Issues
- Check indexes exist: `db.executions.getIndexes()`
- Monitor connection pool usage
- Consider increasing pool size in config

## Next Steps

1. Install MongoDB locally or use MongoDB Atlas
2. Update `.env` with connection details
3. Run example script to test connection
4. Integrate into one app as a pilot
5. Roll out to all apps incrementally