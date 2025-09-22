#!/usr/bin/env python3
"""Test PostgreSQL connection"""

import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Try different connection approaches
connections = [
    {
        'name': 'Environment vars',
        'config': {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'user': os.getenv('POSTGRES_USER', 'ai_dba'),
            'password': os.getenv('POSTGRES_PASSWORD', 'AIDBAdmin2025Secure'),
            'database': os.getenv('POSTGRES_DB', 'ai_control')
        }
    },
    {
        'name': 'Direct localhost',
        'config': {
            'host': '127.0.0.1',
            'port': '5432',
            'user': 'ai_dba',
            'password': 'AIDBAdmin2025Secure',
            'database': 'ai_control'
        }
    },
    {
        'name': 'No password (trust)',
        'config': {
            'host': '127.0.0.1',
            'port': '5432',
            'user': 'ai_dba',
            'database': 'ai_control'
        }
    }
]

for conn_info in connections:
    print(f"\nTrying: {conn_info['name']}")
    print(f"Config: {conn_info['config']}")
    try:
        conn = psycopg2.connect(**conn_info['config'])
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"SUCCESS! Connected to: {version[0]}")
        cursor.close()
        conn.close()
        break
    except Exception as e:
        print(f"FAILED: {e}")