#!/usr/bin/env python3
"""
Migrate SQLite Infrastructure Audit Database to PostgreSQL
Transfers all data from SQLite to the new AI-driven PostgreSQL database
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configurations
SQLITE_DB = Path(__file__).parent.parent / "infra_audit_system" / "infra_audit.db"
POSTGRES_CONFIG = {
    'host': '127.0.0.1',
    'port': '5433',
    'user': 'ai_dba',
    'password': 'AIDBAdmin2025Secure',
    'database': 'ai_control'
}

def create_postgres_schema(pg_conn):
    """Create infrastructure schema in PostgreSQL"""
    cursor = pg_conn.cursor()

    # Create schema for infrastructure audit
    cursor.execute("CREATE SCHEMA IF NOT EXISTS infra;")

    # Create tables in PostgreSQL matching SQLite schema
    create_tables_sql = """
    -- Layers table
    CREATE TABLE IF NOT EXISTS infra.layers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Categories table
    CREATE TABLE IF NOT EXISTS infra.categories (
        id SERIAL PRIMARY KEY,
        layer_id INTEGER REFERENCES infra.layers(id),
        name VARCHAR(100) NOT NULL,
        code VARCHAR(50) UNIQUE NOT NULL,
        description TEXT,
        icon VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Components table
    CREATE TABLE IF NOT EXISTS infra.components (
        id SERIAL PRIMARY KEY,
        category_id INTEGER REFERENCES infra.categories(id),
        code VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        version VARCHAR(50),
        license VARCHAR(100),
        url TEXT,
        documentation_url TEXT,
        repository_url TEXT,
        is_open_source BOOLEAN DEFAULT FALSE,
        is_cloud_native BOOLEAN DEFAULT FALSE,
        is_ai_component BOOLEAN DEFAULT FALSE,
        requires_gpu BOOLEAN DEFAULT FALSE,
        maturity_level VARCHAR(20),
        vendor VARCHAR(100),
        cost_type VARCHAR(20),
        estimated_monthly_cost_min DECIMAL(10,2),
        estimated_monthly_cost_max DECIMAL(10,2),
        minimum_ram_gb INTEGER,
        minimum_cpu_cores INTEGER,
        minimum_storage_gb INTEGER,
        supported_platforms JSONB,
        tags JSONB,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Profiles table
    CREATE TABLE IF NOT EXISTS infra.profiles (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        type VARCHAR(50) NOT NULL,
        description TEXT,
        parent_profile_id INTEGER REFERENCES infra.profiles(id),
        is_ai_first BOOLEAN DEFAULT TRUE,
        default_llm_provider VARCHAR(50),
        estimated_setup_hours INTEGER,
        min_monthly_cost DECIMAL(10,2),
        max_monthly_cost DECIMAL(10,2),
        complexity_score INTEGER,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Profile Components junction table
    CREATE TABLE IF NOT EXISTS infra.profile_components (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER REFERENCES infra.profiles(id) ON DELETE CASCADE,
        component_id INTEGER REFERENCES infra.components(id),
        inclusion_type VARCHAR(20) DEFAULT 'required',
        configuration JSONB,
        priority INTEGER DEFAULT 50,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Audit Sessions table
    CREATE TABLE IF NOT EXISTS infra.audit_sessions (
        id SERIAL PRIMARY KEY,
        session_id UUID UNIQUE DEFAULT gen_random_uuid(),
        profile_id INTEGER REFERENCES infra.profiles(id),
        status VARCHAR(20) DEFAULT 'pending',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        total_components INTEGER DEFAULT 0,
        passed_components INTEGER DEFAULT 0,
        failed_components INTEGER DEFAULT 0,
        warnings_count INTEGER DEFAULT 0,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Audit Results table
    CREATE TABLE IF NOT EXISTS infra.audit_results (
        id SERIAL PRIMARY KEY,
        session_id INTEGER REFERENCES infra.audit_sessions(id) ON DELETE CASCADE,
        component_id INTEGER REFERENCES infra.components(id),
        status VARCHAR(20),
        message TEXT,
        details JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_components_category ON infra.components(category_id);
    CREATE INDEX IF NOT EXISTS idx_components_ai ON infra.components(is_ai_component);
    CREATE INDEX IF NOT EXISTS idx_profile_components_profile ON infra.profile_components(profile_id);
    CREATE INDEX IF NOT EXISTS idx_audit_sessions_profile ON infra.audit_sessions(profile_id);
    CREATE INDEX IF NOT EXISTS idx_audit_results_session ON infra.audit_results(session_id);
    """

    cursor.execute(create_tables_sql)
    pg_conn.commit()
    logger.info("PostgreSQL schema created successfully")

def migrate_layers(sqlite_conn, pg_conn):
    """Migrate layers table"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    sqlite_cursor.execute("SELECT * FROM layers")
    layers = sqlite_cursor.fetchall()

    if layers:
        insert_sql = """
            INSERT INTO infra.layers (id, name, description, order_index, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """
        data = [(row[0], row[1], row[2], row[3], row[4] or datetime.now()) for row in layers]
        execute_batch(pg_cursor, insert_sql, data)
        pg_conn.commit()
        logger.info(f"Migrated {len(layers)} layers")

def migrate_categories(sqlite_conn, pg_conn):
    """Migrate categories table"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    # SQLite columns: ['id', 'code', 'name', 'layer_id', 'icon', 'color', 'created_at']
    sqlite_cursor.execute("SELECT id, code, name, layer_id, icon, created_at FROM categories")
    categories = sqlite_cursor.fetchall()

    if categories:
        insert_sql = """
            INSERT INTO infra.categories (id, code, name, layer_id, icon, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (code) DO NOTHING
        """
        data = [(row[0], row[1], row[2], row[3], row[4], row[5] or datetime.now())
                for row in categories]
        execute_batch(pg_cursor, insert_sql, data)
        pg_conn.commit()
        logger.info(f"Migrated {len(categories)} categories")

def migrate_components(sqlite_conn, pg_conn):
    """Migrate components table"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    # Get all columns from SQLite
    sqlite_cursor.execute("SELECT * FROM components")
    components = sqlite_cursor.fetchall()

    if components:
        insert_sql = """
            INSERT INTO infra.components (
                id, category_id, code, name, description, version, license, url,
                documentation_url, repository_url, is_open_source, is_cloud_native,
                is_ai_component, requires_gpu, maturity_level, vendor, cost_type,
                estimated_monthly_cost_min, estimated_monthly_cost_max,
                minimum_ram_gb, minimum_cpu_cores, minimum_storage_gb,
                supported_platforms, tags, metadata, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (code) DO NOTHING
        """

        data = []
        for row in components:
            # Map SQLite columns to PostgreSQL columns
            # SQLite: id(0), code(1), name(2), category_id(3), layer_id(4), description(5),
            # version_min(6), version_recommended(7), version_latest(8), is_required(9),
            # is_ai_component(10), is_opensource(11), license_type(12), documentation_url(13),
            # repository_url(14), cost_type(15), estimated_monthly_cost_min(16),
            # estimated_monthly_cost_max(17), setup_complexity(18), setup_time_minutes(19),
            # resource_requirements(20), tags(21), metadata(22), created_at(23), updated_at(24)

            # Parse resource requirements JSON to extract values
            resource_req = {}
            try:
                if row[20]:
                    resource_req = json.loads(row[20])
            except (json.JSONDecodeError, TypeError):
                resource_req = {}

            # Convert JSON strings to proper format with error handling
            try:
                tags = json.dumps(json.loads(row[21]) if row[21] else [])
            except (json.JSONDecodeError, TypeError):
                tags = json.dumps([])

            try:
                metadata = json.dumps(json.loads(row[22]) if row[22] else {})
            except (json.JSONDecodeError, TypeError):
                metadata = json.dumps({})

            data.append((
                row[0],  # id
                row[3],  # category_id
                row[1],  # code
                row[2],  # name
                row[5],  # description
                row[7],  # version (use recommended version)
                row[12],  # license
                None,  # url
                row[13],  # documentation_url
                row[14],  # repository_url
                bool(row[11]),  # is_open_source
                False,  # is_cloud_native (not in SQLite)
                bool(row[10]),  # is_ai_component
                False,  # requires_gpu (not directly in SQLite)
                None,  # maturity_level
                None,  # vendor
                row[15],  # cost_type
                row[16],  # estimated_monthly_cost_min
                row[17],  # estimated_monthly_cost_max
                resource_req.get('min_ram_gb'),  # minimum_ram_gb
                resource_req.get('min_cpu_cores'),  # minimum_cpu_cores
                resource_req.get('min_storage_gb'),  # minimum_storage_gb
                json.dumps([]),  # supported_platforms (not in SQLite)
                tags,  # tags
                metadata,  # metadata
                row[23] or datetime.now()  # created_at
            ))

        execute_batch(pg_cursor, insert_sql, data)
        pg_conn.commit()
        logger.info(f"Migrated {len(components)} components")

def migrate_profiles(sqlite_conn, pg_conn):
    """Migrate profiles table"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    sqlite_cursor.execute("SELECT * FROM profiles")
    profiles = sqlite_cursor.fetchall()

    if profiles:
        insert_sql = """
            INSERT INTO infra.profiles (
                id, name, type, description, parent_profile_id, is_ai_first,
                default_llm_provider, estimated_setup_hours, min_monthly_cost,
                max_monthly_cost, complexity_score, metadata, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """

        data = []
        for row in profiles:
            try:
                metadata = json.dumps(json.loads(row[11]) if row[11] else {})
            except (json.JSONDecodeError, TypeError):
                metadata = json.dumps({})
            data.append((
                row[0], row[1], row[2], row[3], row[4], bool(row[5]),
                row[6], row[7], row[8], row[9], row[10], metadata,
                row[12] or datetime.now()
            ))

        execute_batch(pg_cursor, insert_sql, data)
        pg_conn.commit()
        logger.info(f"Migrated {len(profiles)} profiles")

def migrate_profile_components(sqlite_conn, pg_conn):
    """Migrate profile_components table"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    sqlite_cursor.execute("SELECT * FROM profile_components")
    profile_components = sqlite_cursor.fetchall()

    if profile_components:
        insert_sql = """
            INSERT INTO infra.profile_components (
                id, profile_id, component_id, inclusion_type, configuration, priority
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """

        data = []
        for row in profile_components:
            configuration = json.dumps(json.loads(row[4]) if row[4] else {})
            data.append((row[0], row[1], row[2], row[3], configuration, row[5]))

        execute_batch(pg_cursor, insert_sql, data)
        pg_conn.commit()
        logger.info(f"Migrated {len(profile_components)} profile components")

def reset_sequences(pg_conn):
    """Reset PostgreSQL sequences after migration"""
    cursor = pg_conn.cursor()

    sequences = [
        ('layers', 'id'),
        ('categories', 'id'),
        ('components', 'id'),
        ('profiles', 'id'),
        ('profile_components', 'id'),
        ('audit_sessions', 'id'),
        ('audit_results', 'id')
    ]

    for table, column in sequences:
        cursor.execute(f"""
            SELECT setval(
                pg_get_serial_sequence('infra.{table}', '{column}'),
                COALESCE((SELECT MAX({column}) FROM infra.{table}), 1)
            );
        """)

    pg_conn.commit()
    logger.info("Reset PostgreSQL sequences")

def main():
    """Main migration function"""
    logger.info("Starting SQLite to PostgreSQL migration...")

    # Check if SQLite database exists
    if not SQLITE_DB.exists():
        logger.error(f"SQLite database not found at {SQLITE_DB}")
        return

    # Connect to databases
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        pg_conn = psycopg2.connect(**POSTGRES_CONFIG)

        # Create PostgreSQL schema
        create_postgres_schema(pg_conn)

        # Migrate tables in order
        migrate_layers(sqlite_conn, pg_conn)
        migrate_categories(sqlite_conn, pg_conn)
        migrate_components(sqlite_conn, pg_conn)
        migrate_profiles(sqlite_conn, pg_conn)
        migrate_profile_components(sqlite_conn, pg_conn)

        # Reset sequences
        reset_sequences(pg_conn)

        # Close connections
        sqlite_conn.close()
        pg_conn.close()

        logger.info("Migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    main()