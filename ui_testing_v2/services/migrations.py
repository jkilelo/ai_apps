"""
Database migration management using Alembic
"""

import os
import logging
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import create_async_engine

from ..core.config import DatabaseConfig

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations using Alembic"""
    
    def __init__(self, config: DatabaseConfig, migrations_dir: Optional[str] = None):
        self.config = config
        self.migrations_dir = Path(migrations_dir or "migrations")
        self.alembic_cfg: Optional[Config] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize Alembic configuration"""
        if self._initialized:
            return
        
        # Create migrations directory if it doesn't exist
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Create alembic.ini file if it doesn't exist
        alembic_ini_path = self.migrations_dir / "alembic.ini"
        if not alembic_ini_path.exists():
            self._create_alembic_ini(alembic_ini_path)
        
        # Initialize Alembic config
        self.alembic_cfg = Config(str(alembic_ini_path))
        self.alembic_cfg.set_main_option("script_location", str(self.migrations_dir))
        self.alembic_cfg.set_main_option("sqlalchemy.url", self._get_sync_url())
        
        # Create migration environment if it doesn't exist
        env_py_path = self.migrations_dir / "env.py"
        if not env_py_path.exists():
            command.init(self.alembic_cfg, str(self.migrations_dir))
            self._customize_env_py(env_py_path)
        
        self._initialized = True
        logger.info("Migration manager initialized")
    
    def _get_sync_url(self) -> str:
        """Convert async database URL to sync URL for Alembic"""
        url = self.config.url
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://")
        elif url.startswith("sqlite+aiosqlite://"):
            return url.replace("sqlite+aiosqlite://", "sqlite:///")
        return url
    
    def _create_alembic_ini(self, path: Path) -> None:
        """Create alembic.ini configuration file"""
        content = """# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format.  This value is passed to the Formatter.format()
# method in string.format() style, using the format string and the
# variables revision and down_revision.
# revision_number_format = %04d

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = driver://user:pass@localhost/dbname

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        path.write_text(content)
    
    def _customize_env_py(self, path: Path) -> None:
        """Customize the generated env.py file for our models"""
        content = '''"""Alembic environment configuration for UI Testing Framework v2"""

import asyncio
import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Import your models here
from ui_testing_v2.models.database import *
from sqlmodel import SQLModel

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target metadata
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """Run migrations in async mode."""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        path.write_text(content)
    
    def create_migration(
        self,
        message: str,
        autogenerate: bool = True,
    ) -> str:
        """Create a new migration"""
        if not self._initialized:
            self.initialize()
        
        logger.info(f"Creating migration: {message}")
        
        if autogenerate:
            command.revision(self.alembic_cfg, message=message, autogenerate=True)
        else:
            command.revision(self.alembic_cfg, message=message)
        
        # Get the latest revision ID
        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        revision = script_dir.get_current_head()
        
        logger.info(f"Created migration {revision}: {message}")
        return revision
    
    def upgrade(self, revision: str = "head") -> None:
        """Upgrade database to a specific revision"""
        if not self._initialized:
            self.initialize()
        
        logger.info(f"Upgrading database to {revision}")
        command.upgrade(self.alembic_cfg, revision)
        logger.info("Database upgrade completed")
    
    def downgrade(self, revision: str) -> None:
        """Downgrade database to a specific revision"""
        if not self._initialized:
            self.initialize()
        
        logger.warning(f"Downgrading database to {revision}")
        command.downgrade(self.alembic_cfg, revision)
        logger.warning("Database downgrade completed")
    
    def get_current_revision(self) -> Optional[str]:
        """Get current database revision"""
        if not self._initialized:
            self.initialize()
        
        # Create sync engine for inspection
        sync_url = self._get_sync_url()
        engine = create_engine(sync_url)
        
        try:
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        finally:
            engine.dispose()
    
    def get_head_revision(self) -> Optional[str]:
        """Get the latest migration revision"""
        if not self._initialized:
            self.initialize()
        
        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        return script_dir.get_current_head()
    
    def show_history(self) -> list:
        """Show migration history"""
        if not self._initialized:
            self.initialize()
        
        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        revisions = []
        
        for revision in script_dir.walk_revisions():
            revisions.append({
                "revision": revision.revision,
                "down_revision": revision.down_revision,
                "branch_labels": revision.branch_labels,
                "depends_on": revision.depends_on,
                "doc": revision.doc,
                "create_date": getattr(revision, 'create_date', None),
            })
        
        return revisions
    
    def check_migration_status(self) -> dict:
        """Check if database is up to date with migrations"""
        current = self.get_current_revision()
        head = self.get_head_revision()
        
        return {
            "current_revision": current,
            "head_revision": head,
            "is_up_to_date": current == head,
            "needs_upgrade": current != head,
        }
    
    def ensure_current(self) -> bool:
        """Ensure database is at the current migration level"""
        status = self.check_migration_status()
        
        if not status["is_up_to_date"]:
            logger.info("Database migrations are not up to date, upgrading...")
            self.upgrade()
            return True
        
        return False
    
    async def async_ensure_current(self) -> bool:
        """Async version of ensure_current"""
        # Run in thread pool since Alembic is sync
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.ensure_current)


async def create_initial_migration(config: DatabaseConfig) -> str:
    """Create initial migration for the database schema"""
    migration_manager = MigrationManager(config)
    migration_manager.initialize()
    
    # Check if we have any migrations
    script_dir = ScriptDirectory.from_config(migration_manager.alembic_cfg)
    revisions = list(script_dir.walk_revisions())
    
    if not revisions:
        # Create initial migration
        logger.info("Creating initial database migration")
        revision = migration_manager.create_migration(
            "Initial migration",
            autogenerate=True
        )
        return revision
    else:
        logger.info("Database migrations already exist")
        return revisions[0].revision


async def setup_database(config: DatabaseConfig) -> None:
    """Complete database setup with migrations"""
    migration_manager = MigrationManager(config)
    
    # Initialize migration system
    migration_manager.initialize()
    
    # Check current status
    status = migration_manager.check_migration_status()
    logger.info(f"Migration status: {status}")
    
    # Create initial migration if needed
    if not status["head_revision"]:
        await create_initial_migration(config)
    
    # Upgrade to latest
    if not status["is_up_to_date"]:
        migration_manager.upgrade()
    
    logger.info("Database setup completed")
