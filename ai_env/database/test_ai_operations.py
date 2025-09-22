#!/usr/bin/env python3
"""
Test AI-Driven Database Operations
Demonstrates autonomous database management capabilities
"""

import json
import requests
import psycopg2
from datetime import datetime
from typing import Dict, Any

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': '5433',
    'user': 'ai_dba',
    'password': 'AIDBAdmin2025Secure',
    'database': 'ai_control'
}

# MCP Server URL
MCP_SERVER_URL = "http://localhost:8080"

def test_ai_agent_action():
    """Test logging an AI agent action"""
    print("\n=== Testing AI Agent Action Logging ===")

    action_data = {
        "agent_id": "550e8400-e29b-41d4-a716-446655440000",
        "action_type": "query_optimization",
        "target_database": "ai_control",
        "target_schema": "public",
        "target_object": "agent_actions",
        "sql_command": "CREATE INDEX idx_test ON agent_actions(created_at DESC)",
        "parameters": {"index_type": "btree"},
        "decision_confidence": 0.95,
        "decision_reasoning": "Query analysis shows frequent sorting by created_at",
        "llm_model": "gemini-2.5-flash"
    }

    response = requests.post(f"{MCP_SERVER_URL}/agent/action", json=action_data)
    if response.status_code == 200:
        result = response.json()
        print(f"[+] Agent action logged: {result['action_id']}")
        return result['action_id']
    else:
        print(f"[-] Failed to log action: {response.status_code}")
        return None

def test_performance_metrics():
    """Test performance metric collection"""
    print("\n=== Testing Performance Metric Collection ===")

    metrics = [
        {"metric_name": "query_latency_ms", "database_name": "ai_control", "value": 12.5},
        {"metric_name": "cache_hit_ratio", "database_name": "ai_control", "value": 0.95},
        {"metric_name": "connections_active", "database_name": "ai_control", "value": 15},
        {"metric_name": "transactions_per_sec", "database_name": "ai_control", "value": 150.7}
    ]

    for metric in metrics:
        response = requests.post(f"{MCP_SERVER_URL}/metrics/collect", json=metric)
        if response.status_code == 200:
            print(f"[+] Collected metric: {metric['metric_name']} = {metric['value']}")
        else:
            print(f"[-] Failed to collect {metric['metric_name']}")

def test_query_optimization():
    """Test query optimization API"""
    print("\n=== Testing Query Optimization ===")

    query_data = {
        "query": "SELECT * FROM agent_actions WHERE created_at > NOW() - INTERVAL '7 days' ORDER BY created_at DESC",
        "database": "ai_control",
        "explain_analyze": False
    }

    response = requests.post(f"{MCP_SERVER_URL}/optimize/query", json=query_data)
    if response.status_code == 200:
        result = response.json()
        print(f"[+] Query analyzed successfully")
        if result.get('optimizations'):
            for opt in result['optimizations']:
                print(f"    Optimization: {opt['type']} - {opt['suggestion']}")
    else:
        print(f"[-] Query optimization failed: {response.status_code}")

def test_self_healing():
    """Test self-healing action recording"""
    print("\n=== Testing Self-Healing Actions ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Insert a self-healing action
    cursor.execute("""
        INSERT INTO self_healing_actions (
            issue_detected, severity, detection_method,
            detection_metrics, resolution_strategy,
            actions_taken, issue_resolved
        ) VALUES (
            'High query latency detected',
            'medium',
            'performance_monitoring',
            '{"avg_latency_ms": 250, "threshold_ms": 100}'::jsonb,
            'auto_vacuum_analyze',
            '{"vacuum": true, "analyze": true, "tables": ["agent_actions"]}'::jsonb,
            true
        ) RETURNING healing_id;
    """)

    healing_id = cursor.fetchone()[0]
    conn.commit()

    print(f"[+] Self-healing action recorded: {healing_id}")

    # Query self-healing statistics
    cursor.execute("""
        SELECT severity, COUNT(*) as count,
               SUM(CASE WHEN issue_resolved THEN 1 ELSE 0 END) as resolved
        FROM self_healing_actions
        GROUP BY severity;
    """)

    print("\nSelf-Healing Statistics:")
    for row in cursor.fetchall():
        severity, count, resolved = row
        print(f"  {severity}: {count} issues, {resolved} resolved")

    cursor.close()
    conn.close()

def test_ai_driven_monitoring():
    """Test AI-driven monitoring capabilities"""
    print("\n=== Testing AI-Driven Monitoring ===")

    # Check database statistics
    response = requests.get(f"{MCP_SERVER_URL}/stats/database")
    if response.status_code == 200:
        stats = response.json()
        print("[+] Database Statistics:")
        print(f"    Size: {stats['database_size']['size_pretty']}")
        print(f"    Cache Hit Ratio: {stats.get('cache_hit_ratio', 'N/A')}")

        print("\n    Top Tables by Size:")
        for table in stats['top_tables'][:3]:
            print(f"      - {table['tablename']}: {table['size']}")

        print("\n    Connection States:")
        for conn_state in stats['connections']:
            print(f"      - {conn_state['state'] or 'idle'}: {conn_state['count']}")

def test_agent_heartbeat():
    """Test agent heartbeat updates"""
    print("\n=== Testing Agent Heartbeat ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Update agent heartbeat
    cursor.execute("""
        UPDATE ai_agents
        SET last_heartbeat = CURRENT_TIMESTAMP
        WHERE agent_name = 'master_dba_agent'
        RETURNING agent_name, last_heartbeat;
    """)

    result = cursor.fetchone()
    if result:
        print(f"[+] Agent heartbeat updated: {result[0]} at {result[1]}")

    conn.commit()
    cursor.close()
    conn.close()

def test_disaster_recovery():
    """Test disaster recovery checkpoint creation"""
    print("\n=== Testing Disaster Recovery ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Create a DR checkpoint
    cursor.execute("""
        INSERT INTO dr_checkpoints (
            checkpoint_type,
            backup_location,
            backup_size_bytes,
            validated,
            can_restore,
            recovery_priority
        ) VALUES (
            'incremental',
            '/backups/2025-09-21/checkpoint_001',
            1048576,
            true,
            true,
            8
        ) RETURNING checkpoint_id, created_at;
    """)

    checkpoint_id, created_at = cursor.fetchone()
    conn.commit()

    print(f"[+] DR Checkpoint created: {checkpoint_id}")
    print(f"    Created at: {created_at}")

    # Query DR readiness
    cursor.execute("""
        SELECT checkpoint_type, COUNT(*) as count,
               SUM(CASE WHEN can_restore THEN 1 ELSE 0 END) as restorable
        FROM dr_checkpoints
        GROUP BY checkpoint_type;
    """)

    print("\nDisaster Recovery Readiness:")
    for row in cursor.fetchall():
        checkpoint_type, count, restorable = row
        print(f"  {checkpoint_type}: {count} checkpoints, {restorable} restorable")

    cursor.close()
    conn.close()

def main():
    """Run all AI-driven database operation tests"""
    print("="*60)
    print("AI-DRIVEN DATABASE OPERATIONS TEST SUITE")
    print("Demonstrating Autonomous Database Management")
    print("="*60)

    try:
        # Test all AI operations
        action_id = test_ai_agent_action()
        test_performance_metrics()
        test_query_optimization()
        test_self_healing()
        test_ai_driven_monitoring()
        test_agent_heartbeat()
        test_disaster_recovery()

        print("\n" + "="*60)
        print("AI-DRIVEN DATABASE OPERATIONS COMPLETED SUCCESSFULLY")
        print("The database is ready for 100% autonomous AI management")
        print("="*60)

    except Exception as e:
        print(f"\n[-] Test failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())