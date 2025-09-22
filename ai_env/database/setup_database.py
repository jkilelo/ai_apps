#!/usr/bin/env python3
"""
Setup AI Control Database Schema for PostgreSQL 18
Following AI_DRIVEN_POSTGRESQL_AUDIT.md specifications
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'user': os.getenv('POSTGRES_USER', 'ai_dba'),
    'password': os.getenv('POSTGRES_PASSWORD', 'AIDBAdmin2025Secure'),
    'database': os.getenv('POSTGRES_DB', 'ai_control')
}

def create_tables():
    """Create all AI control database tables"""

    create_tables_sql = """
    -- Agent Actions Log Table
    CREATE TABLE IF NOT EXISTS agent_actions (
        action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        agent_id UUID REFERENCES ai_agents(agent_id),
        action_type TEXT NOT NULL,
        target_database TEXT,
        target_schema TEXT,
        target_object TEXT,
        sql_command TEXT,
        parameters JSONB,
        status TEXT CHECK(status IN ('pending', 'running', 'success', 'failed', 'rolled_back')),
        result JSONB,
        error_message TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        duration_ms INTEGER GENERATED ALWAYS AS (
            CASE
                WHEN completed_at IS NOT NULL
                THEN EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000
                ELSE NULL
            END
        ) STORED,
        decision_confidence FLOAT CHECK(decision_confidence >= 0 AND decision_confidence <= 1),
        decision_reasoning TEXT,
        llm_model TEXT,
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Performance Baselines Table
    CREATE TABLE IF NOT EXISTS performance_baselines (
        baseline_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        metric_name TEXT NOT NULL,
        database_name TEXT,
        baseline_value NUMERIC,
        min_value NUMERIC,
        max_value NUMERIC,
        avg_value NUMERIC,
        stddev_value NUMERIC,
        percentile_95 NUMERIC,
        percentile_99 NUMERIC,
        alert_threshold NUMERIC,
        critical_threshold NUMERIC,
        samples_collected INTEGER DEFAULT 0,
        learning_iterations INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(metric_name, database_name)
    );

    -- Query Optimization History Table
    CREATE TABLE IF NOT EXISTS query_optimizations (
        optimization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        query_hash TEXT NOT NULL,
        original_query TEXT,
        optimized_query TEXT,
        original_execution_time_ms NUMERIC,
        optimized_execution_time_ms NUMERIC,
        improvement_percentage NUMERIC GENERATED ALWAYS AS (
            CASE
                WHEN original_execution_time_ms > 0
                THEN ((original_execution_time_ms - optimized_execution_time_ms) / original_execution_time_ms) * 100
                ELSE 0
            END
        ) STORED,
        optimization_type TEXT[],
        indexes_created TEXT[],
        statistics_updated BOOLEAN DEFAULT FALSE,
        agent_id UUID REFERENCES ai_agents(agent_id),
        confidence_score FLOAT CHECK(confidence_score >= 0 AND confidence_score <= 1),
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Self-Healing Actions Table
    CREATE TABLE IF NOT EXISTS self_healing_actions (
        healing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        issue_detected TEXT NOT NULL,
        severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
        detection_method TEXT,
        detection_metrics JSONB,
        resolution_strategy TEXT,
        actions_taken JSONB,
        rollback_plan JSONB,
        issue_resolved BOOLEAN DEFAULT FALSE,
        resolution_time_ms INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP
    );

    -- Disaster Recovery Checkpoints Table
    CREATE TABLE IF NOT EXISTS dr_checkpoints (
        checkpoint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        checkpoint_type TEXT CHECK(checkpoint_type IN ('full', 'incremental', 'wal')),
        checkpoint_lsn pg_lsn,
        backup_location TEXT,
        backup_size_bytes BIGINT,
        encryption_key_id TEXT,
        validated BOOLEAN DEFAULT FALSE,
        validation_checksum TEXT,
        can_restore BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        created_by_agent UUID REFERENCES ai_agents(agent_id),
        recovery_priority INTEGER DEFAULT 5 CHECK(recovery_priority BETWEEN 1 AND 10)
    );
    """

    create_indexes_sql = """
    -- Create indexes for agent actions
    CREATE INDEX IF NOT EXISTS idx_agent_actions_agent_time ON agent_actions(agent_id, started_at DESC);
    CREATE INDEX IF NOT EXISTS idx_agent_actions_status ON agent_actions(status) WHERE status IN ('pending', 'running');
    CREATE INDEX IF NOT EXISTS idx_agent_actions_created ON agent_actions(created_at DESC);

    -- Create indexes for performance baselines
    CREATE INDEX IF NOT EXISTS idx_performance_baselines_metric ON performance_baselines(metric_name, database_name);

    -- Create indexes for query optimizations
    CREATE INDEX IF NOT EXISTS idx_query_optimizations_hash ON query_optimizations(query_hash);
    CREATE INDEX IF NOT EXISTS idx_query_optimizations_applied ON query_optimizations(applied_at DESC);

    -- Create indexes for self-healing
    CREATE INDEX IF NOT EXISTS idx_self_healing_severity ON self_healing_actions(severity, issue_resolved);
    CREATE INDEX IF NOT EXISTS idx_self_healing_created ON self_healing_actions(created_at DESC);

    -- Create indexes for disaster recovery
    CREATE INDEX IF NOT EXISTS idx_dr_checkpoints_type ON dr_checkpoints(checkpoint_type);
    CREATE INDEX IF NOT EXISTS idx_dr_checkpoints_created ON dr_checkpoints(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_dr_checkpoints_expires ON dr_checkpoints(expires_at) WHERE expires_at IS NOT NULL;

    -- Create index for active agents
    CREATE INDEX IF NOT EXISTS idx_ai_agents_status ON ai_agents(status) WHERE status = 'active';
    CREATE INDEX IF NOT EXISTS idx_ai_agents_heartbeat ON ai_agents(last_heartbeat DESC);
    """

    insert_master_agent_sql = """
    -- Insert Master DBA Agent
    INSERT INTO ai_agents (agent_name, agent_type, mcp_server_url, capabilities, status)
    VALUES (
        'master_dba_agent',
        'dba',
        'mcp://localhost:8080',
        '{
            "database_management": true,
            "query_optimization": true,
            "backup_restore": true,
            "monitoring": true,
            "security": true,
            "self_healing": true,
            "autonomous_operation": true
        }'::jsonb,
        'active'
    ) ON CONFLICT (agent_name) DO NOTHING;
    """

    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("Creating AI control database tables...")
        cursor.execute(create_tables_sql)
        print("Tables created successfully!")

        print("Creating indexes...")
        cursor.execute(create_indexes_sql)
        print("Indexes created successfully!")

        print("Inserting master DBA agent...")
        cursor.execute(insert_master_agent_sql)
        print("Master DBA agent registered!")

        # Verify tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table[0]}")

        # Verify master agent
        cursor.execute("SELECT agent_name, agent_type, status FROM ai_agents;")
        agents = cursor.fetchall()
        print("\nRegistered agents:")
        for agent in agents:
            print(f"  - {agent[0]} ({agent[1]}): {agent[2]}")

        cursor.close()
        conn.close()

        print("\nDatabase setup completed successfully!")
        return True

    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

if __name__ == "__main__":
    create_tables()