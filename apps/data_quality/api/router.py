"""
Data Quality API Router
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np

# Import our profiler and spark generator
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_quality.enhanced_profiler import EnhancedMLProfiler
from data_quality.spark_generator import SparkProfilerGenerator

# Router setup
router = APIRouter(prefix="/api/data-quality", tags=["data-quality"])

# WebSocket manager for real-time monitoring
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except:
                self.disconnect(session_id)

manager = ConnectionManager()

# Pydantic models
class DataSourceConfig(BaseModel):
    id: str
    name: str
    type: str = Field(..., pattern="^(database|file|streaming|api)$")
    connection: Dict[str, Any]

class ProfileOptions(BaseModel):
    include_ml: bool = True
    sample_size: Optional[int] = None
    columns: Optional[List[str]] = None
    quality_dimensions: List[str] = ["completeness", "validity", "uniqueness", "consistency", "timeliness"]

class ProfileRequest(BaseModel):
    data_source: DataSourceConfig
    options: ProfileOptions = ProfileOptions()

class QualityRule(BaseModel):
    rule_id: str
    rule_name: str
    rule_type: str
    dimension: str
    column_name: str
    description: str
    sql_expression: str
    pyspark_code: str
    python_code: str
    threshold: Optional[float] = None
    severity: str
    enabled: bool
    business_context: Optional[str] = None
    error_message: Optional[str] = None
    suggested_action: Optional[str] = None

class RuleGenerationRequest(BaseModel):
    profile_data: Dict[str, Any]
    options: Dict[str, Any] = {"auto_detect": True, "sensitivity": "medium"}

class RuleExecutionRequest(BaseModel):
    rules: List[QualityRule]
    data_source: DataSourceConfig

class MonitoringRequest(BaseModel):
    data_source: DataSourceConfig
    rules: List[QualityRule]
    interval_seconds: int = 30

class SparkGenerationRequest(BaseModel):
    table_name: str
    schema: Dict[str, Any]
    profiling_config: Optional[Dict[str, Any]] = None

# Mock data generation for demo
def generate_mock_data(table_name: str, num_rows: int = 10000) -> pd.DataFrame:
    """Generate mock data for demonstration"""
    np.random.seed(42)
    
    if table_name == "customers":
        return pd.DataFrame({
            "customer_id": range(1, num_rows + 1),
            "email": [f"user{i}@example.com" for i in range(num_rows)],
            "age": np.random.randint(18, 80, num_rows),
            "registration_date": pd.date_range("2020-01-01", periods=num_rows, freq="H"),
            "country": np.random.choice(["USA", "UK", "Canada", "Australia"], num_rows),
            "total_spent": np.random.exponential(100, num_rows),
            "is_active": np.random.choice([True, False], num_rows, p=[0.8, 0.2])
        })
    elif table_name == "transactions":
        return pd.DataFrame({
            "transaction_id": range(1, num_rows + 1),
            "customer_id": np.random.randint(1, 1000, num_rows),
            "product_id": np.random.randint(1, 100, num_rows),
            "amount": np.random.exponential(50, num_rows),
            "timestamp": pd.date_range("2023-01-01", periods=num_rows, freq="T"),
            "status": np.random.choice(["completed", "pending", "failed"], num_rows, p=[0.8, 0.15, 0.05])
        })
    else:
        # Generic table
        return pd.DataFrame({
            "id": range(1, num_rows + 1),
            "value": np.random.randn(num_rows),
            "category": np.random.choice(["A", "B", "C"], num_rows),
            "timestamp": pd.date_range("2023-01-01", periods=num_rows, freq="H")
        })

# API Endpoints
@router.post("/profile")
async def profile_data_source(request: ProfileRequest):
    """Profile a data source with ML-enhanced analysis"""
    try:
        # For demo, use mock data
        table_name = request.data_source.connection.get("tables", ["customers"])[0]
        df = generate_mock_data(table_name)
        
        # Initialize profiler
        profiler = EnhancedMLProfiler()
        
        # Run profiling
        metadata = {
            "source": request.data_source.name,
            "table": table_name,
            "timestamp": datetime.now().isoformat()
        }
        
        profile_result = await profiler.profile_with_ml(df, metadata)
        
        return profile_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/generate")
async def generate_quality_rules(request: RuleGenerationRequest):
    """Generate quality rules based on profile data"""
    try:
        profile_data = request.profile_data
        rules = []
        
        # Generate rules based on profile insights
        if "column_profiles" in profile_data:
            for col_profile in profile_data["column_profiles"]:
                col_name = col_profile["column_name"]
                
                # Completeness rule
                if col_profile.get("null_percentage", 0) < 5:
                    rules.append(QualityRule(
                        rule_id=f"rule_{col_name}_completeness",
                        rule_name=f"Check {col_name} completeness",
                        rule_type="completeness",
                        dimension="completeness",
                        column_name=col_name,
                        description=f"Ensure {col_name} has minimal null values",
                        sql_expression=f"SELECT COUNT(*) FROM table WHERE {col_name} IS NULL",
                        pyspark_code=f"df.filter(df['{col_name}'].isNull()).count()",
                        python_code=f"df['{col_name}'].isnull().sum()",
                        threshold=95.0,
                        severity="HIGH",
                        enabled=True,
                        business_context=f"Column {col_name} is critical for analysis"
                    ))
                
                # Add more rule generation logic based on ML insights
                if "ml_analysis" in profile_data and "anomalies" in profile_data["ml_analysis"]:
                    if col_name in profile_data["ml_analysis"]["anomalies"]:
                        rules.append(QualityRule(
                            rule_id=f"rule_{col_name}_anomaly",
                            rule_name=f"Detect anomalies in {col_name}",
                            rule_type="anomaly_detection",
                            dimension="validity",
                            column_name=col_name,
                            description=f"Monitor {col_name} for anomalous values",
                            sql_expression=f"-- ML-based anomaly detection",
                            pyspark_code=f"# Use ML model for anomaly detection",
                            python_code=f"# Isolation Forest on {col_name}",
                            threshold=5.0,
                            severity="MEDIUM",
                            enabled=True
                        ))
        
        return {"rules": rules}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/execute")
async def execute_quality_rules(request: RuleExecutionRequest):
    """Execute quality rules against a data source"""
    try:
        # Mock execution results
        results = {
            "execution_time": datetime.now().isoformat(),
            "total_rules": len(request.rules),
            "passed_count": 0,
            "failed_count": 0,
            "passed": True,
            "details": []
        }
        
        for rule in request.rules:
            if rule.enabled:
                # Simulate rule execution
                passed = np.random.random() > 0.2  # 80% pass rate for demo
                
                result = {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "passed": passed,
                    "actual_value": np.random.uniform(70, 100) if passed else np.random.uniform(0, 70),
                    "threshold": rule.threshold,
                    "message": f"Rule {rule.rule_name} {'passed' if passed else 'failed'}"
                }
                
                if passed:
                    results["passed_count"] += 1
                else:
                    results["failed_count"] += 1
                    results["passed"] = False
                    result["error_message"] = rule.error_message
                    result["suggested_action"] = rule.suggested_action
                
                results["details"].append(result)
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ml-insights")
async def get_ml_insights(request: ProfileRequest):
    """Get ML-powered insights for a data source"""
    try:
        # Generate mock ML insights
        table_name = request.data_source.connection.get("tables", ["customers"])[0]
        df = generate_mock_data(table_name)
        
        profiler = EnhancedMLProfiler()
        profile_result = await profiler.profile_with_ml(df)
        
        # Extract just ML insights
        return {"insights": profile_result.get("ml_analysis", {})}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitor/start")
async def start_monitoring(request: MonitoringRequest, background_tasks: BackgroundTasks):
    """Start real-time monitoring session"""
    try:
        session_id = str(uuid.uuid4())
        
        # Start background monitoring task
        background_tasks.add_task(
            monitor_data_quality,
            session_id,
            request.data_source,
            request.rules,
            request.interval_seconds
        )
        
        return {"session_id": session_id, "status": "monitoring_started"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitor/stop")
async def stop_monitoring(session_id: str):
    """Stop monitoring session"""
    # In a real implementation, you'd cancel the background task
    return {"session_id": session_id, "status": "monitoring_stopped"}

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id)

@router.get("/catalog")
async def get_catalog_data(
    tags: Optional[List[str]] = None,
    owner: Optional[str] = None,
    search: Optional[str] = None
):
    """Get data catalog entries"""
    # Mock catalog data
    catalog_entries = [
        {
            "id": "customers",
            "name": "customers",
            "type": "table",
            "database": "retail_analytics",
            "description": "Customer master data",
            "owner": "data-team",
            "tags": ["pii", "master-data"],
            "quality_score": 92,
            "last_profiled": datetime.now().isoformat()
        },
        {
            "id": "transactions", 
            "name": "transactions",
            "type": "table",
            "database": "retail_analytics",
            "description": "Transaction records",
            "owner": "data-team",
            "tags": ["transactional"],
            "quality_score": 88,
            "last_profiled": datetime.now().isoformat()
        }
    ]
    
    # Apply filters
    if tags:
        catalog_entries = [e for e in catalog_entries if any(t in e["tags"] for t in tags)]
    if owner:
        catalog_entries = [e for e in catalog_entries if e["owner"] == owner]
    if search:
        catalog_entries = [e for e in catalog_entries if search.lower() in e["name"].lower() or search.lower() in e["description"].lower()]
    
    return {"entries": catalog_entries}

@router.post("/spark/generate")
async def generate_spark_code(request: SparkGenerationRequest):
    """Generate optimized Spark code for profiling"""
    try:
        generator = SparkProfilerGenerator()
        
        # Generate code
        code = generator.generate_profiling_job(
            request.table_name,
            request.schema,
            request.profiling_config
        )
        
        return {"code": code}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task for monitoring
async def monitor_data_quality(
    session_id: str,
    data_source: DataSourceConfig,
    rules: List[QualityRule],
    interval: int
):
    """Background task for continuous monitoring"""
    while True:
        try:
            # Generate mock metrics
            metric = {
                "timestamp": datetime.now().isoformat(),
                "completeness": np.random.uniform(90, 100),
                "validity": np.random.uniform(85, 100),
                "uniqueness": np.random.uniform(95, 100),
                "consistency": np.random.uniform(90, 100),
                "row_count": np.random.randint(9000, 11000),
                "anomaly_count": np.random.randint(0, 50),
                "processing_time": np.random.randint(100, 500)
            }
            
            # Send via WebSocket
            await manager.send_message({
                "type": "metric",
                "data": {"metric": metric}
            }, session_id)
            
            # Check for alerts
            if metric["validity"] < 90:
                await manager.send_message({
                    "type": "alert",
                    "data": {
                        "alert": {
                            "type": "validity",
                            "severity": "warning",
                            "message": f"Validity dropped to {metric['validity']:.1f}%",
                            "timestamp": metric["timestamp"]
                        }
                    }
                }, session_id)
            
            await asyncio.sleep(interval)
            
        except Exception as e:
            print(f"Monitoring error: {e}")
            break