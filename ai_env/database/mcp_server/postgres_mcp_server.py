#!/usr/bin/env python3
"""
MCP Server for PostgreSQL AI-Driven Database Management
Following AI_DRIVEN_POSTGRESQL_AUDIT.md specifications
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',  # Use IP instead of localhost
    'port': '5433',  # Using alternative port
    'user': 'ai_dba',
    'password': 'AIDBAdmin2025Secure',  # Password set when creating container
    'database': 'ai_control'
}

# Initialize FastAPI app
app = FastAPI(
    title="PostgreSQL MCP Server",
    description="Model Context Protocol server for AI-driven PostgreSQL management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection pool
connection_pool = None

# Pydantic models
class AgentAction(BaseModel):
    """Model for agent actions"""
    agent_id: str
    action_type: str
    target_database: Optional[str] = None
    target_schema: Optional[str] = None
    target_object: Optional[str] = None
    sql_command: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    decision_confidence: float = Field(ge=0, le=1)
    decision_reasoning: str
    llm_model: str

class QueryOptimization(BaseModel):
    """Model for query optimization requests"""
    query: str
    database: str = "ai_control"
    explain_analyze: bool = True

class PerformanceMetric(BaseModel):
    """Model for performance metrics"""
    metric_name: str
    database_name: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthCheck(BaseModel):
    """Model for health check results"""
    status: str
    database_connected: bool
    active_connections: int
    agent_status: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Database connection management
def get_connection():
    """Get database connection from pool"""
    global connection_pool
    if not connection_pool:
        connection_pool = SimpleConnectionPool(1, 20, **DB_CONFIG)
    return connection_pool.getconn()

def return_connection(conn):
    """Return connection to pool"""
    if connection_pool:
        connection_pool.putconn(conn)

# MCP Tools
@app.on_event("startup")
async def startup_event():
    """Initialize MCP server on startup"""
    logger.info("Starting PostgreSQL MCP Server...")
    try:
        # Test database connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"Connected to PostgreSQL: {version[0]}")
        cursor.close()
        return_connection(conn)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down PostgreSQL MCP Server...")
    if connection_pool:
        connection_pool.closeall()

# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Check MCP server and database health"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check database connection
        cursor.execute("SELECT 1;")

        # Get active connections
        cursor.execute("""
            SELECT count(*) as active_connections
            FROM pg_stat_activity
            WHERE state = 'active';
        """)
        active_connections = cursor.fetchone()['active_connections']

        # Get agent status
        cursor.execute("""
            SELECT agent_name, agent_type, status, last_heartbeat
            FROM ai_agents
            WHERE status = 'active';
        """)
        agents = cursor.fetchall()

        cursor.close()
        return_connection(conn)

        return HealthCheck(
            status="healthy",
            database_connected=True,
            active_connections=active_connections,
            agent_status={
                "active_agents": len(agents),
                "agents": agents
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent action logging
@app.post("/agent/action")
async def log_agent_action(action: AgentAction):
    """Log an agent action to the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO agent_actions (
                agent_id, action_type, target_database, target_schema,
                target_object, sql_command, parameters, status,
                decision_confidence, decision_reasoning, llm_model
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s, %s
            ) RETURNING action_id;
        """, (
            action.agent_id, action.action_type, action.target_database,
            action.target_schema, action.target_object, action.sql_command,
            json.dumps(action.parameters) if action.parameters else None,
            action.decision_confidence, action.decision_reasoning,
            action.llm_model
        ))

        action_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        return_connection(conn)

        return {"action_id": action_id, "status": "logged"}
    except Exception as e:
        logger.error(f"Failed to log agent action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Query optimization
@app.post("/optimize/query")
async def optimize_query(request: QueryOptimization):
    """Analyze and optimize a SQL query"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get query plan
        explain_cmd = "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)" if request.explain_analyze else "EXPLAIN (FORMAT JSON)"
        cursor.execute(f"{explain_cmd} {request.query}")
        query_plan = cursor.fetchone()

        # Analyze for optimization opportunities
        optimizations = []

        # Check for missing indexes
        cursor.execute("""
            SELECT schemaname, tablename, attname, n_distinct, correlation
            FROM pg_stats
            WHERE schemaname = 'public'
            ORDER BY n_distinct DESC;
        """)
        stats = cursor.fetchall()

        # Simple optimization suggestions
        if "Seq Scan" in json.dumps(query_plan):
            optimizations.append({
                "type": "index",
                "suggestion": "Consider adding indexes to avoid sequential scans"
            })

        cursor.close()
        return_connection(conn)

        return {
            "original_query": request.query,
            "query_plan": query_plan,
            "optimizations": optimizations,
            "statistics": stats[:5]  # Top 5 statistics
        }
    except Exception as e:
        logger.error(f"Query optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Performance metrics collection
@app.post("/metrics/collect")
async def collect_metrics(metric: PerformanceMetric):
    """Collect and store performance metrics"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Update or insert baseline
        cursor.execute("""
            INSERT INTO performance_baselines (
                metric_name, database_name, baseline_value,
                min_value, max_value, avg_value, samples_collected
            ) VALUES (%s, %s, %s, %s, %s, %s, 1)
            ON CONFLICT (metric_name, database_name) DO UPDATE SET
                baseline_value = %s,
                min_value = LEAST(performance_baselines.min_value, %s),
                max_value = GREATEST(performance_baselines.max_value, %s),
                avg_value = (performance_baselines.avg_value * performance_baselines.samples_collected + %s) / (performance_baselines.samples_collected + 1),
                samples_collected = performance_baselines.samples_collected + 1,
                last_updated = CURRENT_TIMESTAMP;
        """, (
            metric.metric_name, metric.database_name, metric.value,
            metric.value, metric.value, metric.value,
            metric.value, metric.value, metric.value, metric.value
        ))

        conn.commit()
        cursor.close()
        return_connection(conn)

        return {"status": "collected", "metric": metric.metric_name}
    except Exception as e:
        logger.error(f"Metric collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Database statistics
@app.get("/stats/database")
async def get_database_stats():
    """Get comprehensive database statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Database size
        cursor.execute("""
            SELECT pg_database_size(current_database()) as size_bytes,
                   pg_size_pretty(pg_database_size(current_database())) as size_pretty;
        """)
        db_size = cursor.fetchone()

        # Table sizes
        cursor.execute("""
            SELECT schemaname, tablename,
                   pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10;
        """)
        table_sizes = cursor.fetchall()

        # Connection stats
        cursor.execute("""
            SELECT state, count(*) as count
            FROM pg_stat_activity
            GROUP BY state;
        """)
        connection_stats = cursor.fetchall()

        # Cache hit ratio
        cursor.execute("""
            SELECT
                sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
            FROM pg_statio_user_tables;
        """)
        cache_hit = cursor.fetchone()

        cursor.close()
        return_connection(conn)

        return {
            "database_size": db_size,
            "top_tables": table_sizes,
            "connections": connection_stats,
            "cache_hit_ratio": cache_hit['cache_hit_ratio']
        }
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Self-healing endpoint
@app.post("/healing/detect")
async def detect_issues():
    """Detect and log database issues for self-healing"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        issues = []

        # Check for long-running queries
        cursor.execute("""
            SELECT pid, usename, query, state_change
            FROM pg_stat_activity
            WHERE state != 'idle'
            AND query NOT LIKE '%pg_stat_activity%'
            AND state_change < NOW() - INTERVAL '5 minutes';
        """)
        long_queries = cursor.fetchall()
        if long_queries:
            issues.append({
                "type": "long_running_queries",
                "severity": "medium",
                "count": len(long_queries),
                "details": long_queries
            })

        # Check for table bloat
        cursor.execute("""
            SELECT schemaname, tablename,
                   n_dead_tup, n_live_tup,
                   n_dead_tup::float / (n_live_tup + 1) as dead_ratio
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 1000
            AND n_dead_tup::float / (n_live_tup + 1) > 0.2
            ORDER BY dead_ratio DESC;
        """)
        bloated_tables = cursor.fetchall()
        if bloated_tables:
            issues.append({
                "type": "table_bloat",
                "severity": "low",
                "count": len(bloated_tables),
                "details": bloated_tables
            })

        # Log issues to self-healing table
        for issue in issues:
            cursor.execute("""
                INSERT INTO self_healing_actions (
                    issue_detected, severity, detection_method, detection_metrics
                ) VALUES (%s, %s, 'monitoring', %s);
            """, (
                issue['type'], issue['severity'],
                json.dumps(issue)
            ))

        conn.commit()
        cursor.close()
        return_connection(conn)

        return {
            "issues_detected": len(issues),
            "issues": issues
        }
    except Exception as e:
        logger.error(f"Issue detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)