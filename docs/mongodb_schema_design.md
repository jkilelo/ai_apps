# MongoDB Schema Design for AI Apps Suite

## Overview

This document describes the MongoDB schema design for storing execution states, inputs, outputs, and metadata for all apps in the AI Apps Suite.

## Collections

### 1. `executions` Collection

Stores the main execution records for each app/sub-app run.

```json
{
  "_id": ObjectId,
  "execution_id": "uuid-v4",
  "app_id": 1,
  "app_name": "data_quality",
  "sub_app_id": 1,
  "sub_app_name": "dq_profiling",
  "user_id": "user_identifier",
  "status": "completed|running|failed|cancelled",
  "started_at": ISODate("2024-01-01T00:00:00Z"),
  "completed_at": ISODate("2024-01-01T00:05:00Z"),
  "duration_ms": 300000,
  "error": null,
  "metadata": {
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "version": "1.0.0",
    "environment": "production"
  },
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:05:00Z")
}
```

**Indexes:**
- `execution_id` (unique)
- `app_id, sub_app_id` (compound)
- `user_id`
- `status`
- `started_at` (descending)

### 2. `execution_steps` Collection

Stores individual step executions within a workflow.

```json
{
  "_id": ObjectId,
  "execution_id": "parent-execution-uuid",
  "step_id": 1,
  "step_name": "element_extraction_using_python_playwright",
  "step_version": "1.0.0",
  "status": "completed|running|failed|skipped",
  "started_at": ISODate("2024-01-01T00:00:00Z"),
  "completed_at": ISODate("2024-01-01T00:01:00Z"),
  "duration_ms": 60000,
  "input": {
    "web_page_url": "https://example.com"
  },
  "output": {
    "extracted_elements": [
      {
        "id": "elem_1",
        "type": "button",
        "selector": "#submit-button",
        "text": "Submit",
        "attributes": {
          "class": "btn btn-primary",
          "disabled": false
        }
      }
    ]
  },
  "error": null,
  "retry_count": 0,
  "metadata": {
    "memory_usage_mb": 256,
    "cpu_usage_percent": 45.2
  }
}
```

**Indexes:**
- `execution_id, step_id` (compound, unique)
- `execution_id`
- `status`
- `step_name`
- `started_at` (descending)

### 3. `app_configurations` Collection

Stores app and sub-app configuration history.

```json
{
  "_id": ObjectId,
  "app_id": 1,
  "app_name": "ui_web_auto_testing",
  "sub_app_id": null,
  "sub_app_name": null,
  "version": "1.0.0",
  "configuration": {
    "steps": [
      {
        "id": 1,
        "name": "element_extraction_using_python_playwright",
        "input": [...],
        "output": [...],
        "depends_on": []
      }
    ],
    "description": "Automated testing framework for web applications.",
    "settings": {
      "timeout_seconds": 300,
      "max_retries": 3
    }
  },
  "active": true,
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "created_by": "admin"
}
```

**Indexes:**
- `app_id, sub_app_id, version` (compound, unique)
- `active`

### 4. `execution_artifacts` Collection

Stores large artifacts like screenshots, logs, generated code, etc.

```json
{
  "_id": ObjectId,
  "execution_id": "parent-execution-uuid",
  "step_id": 1,
  "artifact_type": "screenshot|log|code|report",
  "artifact_name": "page_screenshot.png",
  "mime_type": "image/png",
  "size_bytes": 1048576,
  "storage_type": "gridfs|s3|local",
  "storage_path": "gridfs://artifacts/uuid",
  "metadata": {
    "width": 1920,
    "height": 1080,
    "format": "PNG"
  },
  "created_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**
- `execution_id, step_id` (compound)
- `artifact_type`
- `created_at` (descending)

### 5. `execution_metrics` Collection

Time-series collection for performance metrics.

```json
{
  "_id": ObjectId,
  "execution_id": "parent-execution-uuid",
  "timestamp": ISODate("2024-01-01T00:00:00Z"),
  "metrics": {
    "memory_usage_mb": 512,
    "cpu_usage_percent": 75.5,
    "network_bytes_sent": 1024,
    "network_bytes_received": 2048,
    "active_threads": 10
  }
}
```

**Indexes:**
- `execution_id, timestamp` (compound)
- `timestamp` (descending, TTL index for 30 days)

## Schema Design Principles

### 1. Separation of Concerns
- **executions**: High-level execution tracking
- **execution_steps**: Detailed step-by-step progress
- **execution_artifacts**: Large file storage references
- **execution_metrics**: Performance monitoring

### 2. Flexibility
- JSON schema allows for varying input/output structures
- Metadata fields for extensibility
- Version tracking for configuration changes

### 3. Performance Optimization
- Appropriate indexes for common queries
- GridFS integration for large artifacts
- TTL indexes for automatic cleanup of old metrics

### 4. Data Relationships
```
executions (1) ← → (n) execution_steps
     ↓                      ↓
     └──────────┬──────────┘
                ↓
        execution_artifacts
                ↓
        execution_metrics
```

## Common Queries

### Get Latest Executions for a User
```javascript
db.executions.find({
  user_id: "user123"
}).sort({ started_at: -1 }).limit(10)
```

### Get All Steps for an Execution
```javascript
db.execution_steps.find({
  execution_id: "uuid-123"
}).sort({ step_id: 1 })
```

### Get Failed Executions in Last 24 Hours
```javascript
db.executions.find({
  status: "failed",
  started_at: { $gte: new Date(Date.now() - 24*60*60*1000) }
})
```

### Aggregate Success Rate by App
```javascript
db.executions.aggregate([
  {
    $group: {
      _id: "$app_name",
      total: { $sum: 1 },
      successful: {
        $sum: { $cond: [{ $eq: ["$status", "completed"] }, 1, 0] }
      }
    }
  },
  {
    $project: {
      app_name: "$_id",
      success_rate: { $divide: ["$successful", "$total"] }
    }
  }
])
```

## Data Retention Policy

1. **executions**: Keep for 1 year
2. **execution_steps**: Keep for 6 months
3. **execution_artifacts**: Keep for 3 months
4. **execution_metrics**: Keep for 30 days (auto-expire with TTL)
5. **app_configurations**: Keep indefinitely

## Migration from Current System

1. Create indexes before data migration
2. Batch insert historical data if available
3. Implement dual-write during transition period
4. Verify data integrity before switching over

## Security Considerations

1. Enable MongoDB authentication
2. Use role-based access control (RBAC)
3. Encrypt sensitive data fields
4. Enable audit logging
5. Regular backups with encryption

## Connection Configuration

```python
# Example MongoDB connection configuration
MONGODB_CONFIG = {
    "connection_string": "mongodb://username:password@localhost:27017/ai_apps",
    "database": "ai_apps",
    "options": {
        "maxPoolSize": 100,
        "minPoolSize": 10,
        "maxIdleTimeMS": 30000,
        "retryWrites": True,
        "w": "majority"
    }
}
```

## Future Enhancements

1. **Sharding Strategy**: For horizontal scaling
   - Shard key: `execution_id` for even distribution
   
2. **Change Streams**: For real-time updates
   - Monitor execution status changes
   - Trigger notifications on failures

3. **Aggregation Pipelines**: For analytics
   - Daily/weekly/monthly reports
   - Performance trends
   - User activity patterns

4. **Full-Text Search**: On execution logs and outputs
   - Index error messages
   - Search generated code snippets