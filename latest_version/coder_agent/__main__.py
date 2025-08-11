#!/usr/bin/env python3
"""
CODER Agent CLI - Main entry point
"""

import asyncio
import sys
import os
from pathlib import Path
import click
import structlog
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from coder_agent.core.engine import CoderEngine
from coder_agent.contracts.base import AgentRequest
from coder_agent.config.settings import load_config


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@click.command()
@click.argument('task', required=True)
@click.option('--project-path', '-p', default='.', help='Project directory path')
@click.option('--config', '-c', default=None, help='Configuration file path')
@click.option('--timeout', '-t', default=3600, help='Task timeout in seconds')
@click.option('--no-tests', is_flag=True, help='Skip test requirements')
@click.option('--platform', default='any', type=click.Choice(['windows', 'linux', 'mac', 'any']), 
              help='Target platform')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--dry-run', is_flag=True, help='Show plan without executing')
def main(
    task: str,
    project_path: str,
    config: Optional[str],
    timeout: int,
    no_tests: bool,
    platform: str,
    verbose: bool,
    dry_run: bool
):
    """
    CODER Agent - Autonomous coding intelligence that surpasses current assistants.
    
    Examples:
        coder_agent "Fix the login bug in auth.py"
        coder_agent "Add comprehensive tests for the User model" -p ./src
        coder_agent "Refactor the database module to use async" --no-tests
    """
    
    # Set up logging level
    if verbose:
        structlog.configure(
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    click.echo(f"""
╔══════════════════════════════════════════════════════════════╗
║                      CODER Agent v1.0                        ║
║         Autonomous Coding Intelligence Framework             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    click.echo(f"📋 Task: {task}")
    click.echo(f"📁 Project: {os.path.abspath(project_path)}")
    click.echo(f"🎯 Platform: {platform}")
    click.echo(f"🧪 Tests: {'Disabled' if no_tests else 'Required'}")
    click.echo(f"⏱️  Timeout: {timeout}s")
    
    if dry_run:
        click.echo("\n🔍 DRY RUN MODE - Will show plan only\n")
    
    # Run the agent
    try:
        asyncio.run(execute_task(
            task=task,
            project_path=project_path,
            config_path=config,
            timeout=timeout,
            require_tests=not no_tests,
            platform=platform,
            dry_run=dry_run
        ))
    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n\n❌ Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


async def execute_task(
    task: str,
    project_path: str,
    config_path: Optional[str],
    timeout: int,
    require_tests: bool,
    platform: str,
    dry_run: bool
):
    """Execute the coding task"""
    
    # Load configuration
    if config_path:
        config = load_config(config_path)
    else:
        config = load_config()
    
    # Create agent request
    request = AgentRequest(
        task=task,
        project_path=os.path.abspath(project_path),
        timeout_seconds=timeout,
        require_tests=require_tests,
        platform=platform
    )
    
    # Initialize engine
    engine = CoderEngine(config)
    
    if dry_run:
        # Just create and show the plan
        click.echo("\n📝 Creating task plan...\n")
        
        context = await engine._understand_context(request)
        plan = await engine.task_planner.create_plan(request, context)
        
        click.echo("=" * 60)
        click.echo(f"TASK PLAN: {plan.objective}")
        click.echo("=" * 60)
        
        for i, task in enumerate(plan.tasks, 1):
            deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
            click.echo(f"{i}. [{task.priority.value}] {task.content}{deps}")
            click.echo(f"   Estimated tokens: {task.estimated_tokens}")
        
        click.echo("\n" + "=" * 60)
        click.echo(f"Total tasks: {len(plan.tasks)}")
        click.echo(f"Estimated tokens: {plan.total_estimated_tokens}")
        click.echo(f"Max parallel execution: {plan.max_parallel_tasks}")
        click.echo("=" * 60)
        
        return
    
    # Execute the task
    click.echo("\n🚀 Starting execution...\n")
    
    with click.progressbar(length=100, label='Executing') as bar:
        # Create a progress callback
        def progress_callback(percentage: int):
            bar.update(percentage - bar.pos)
        
        # Execute with progress tracking
        response = await engine.execute(request)
        bar.update(100 - bar.pos)
    
    # Display results
    click.echo("\n\n" + "=" * 60)
    click.echo("EXECUTION RESULTS")
    click.echo("=" * 60)
    
    if response.success:
        click.echo("✅ Task completed successfully!")
    else:
        click.echo("❌ Task failed")
    
    if response.changes:
        click.echo(f"\n📝 Files changed: {len(response.changes)}")
        for change in response.changes[:10]:  # Show first 10
            status = "✓" if change.get("success") else "✗"
            click.echo(f"   {status} {change.get('operation')}: {change.get('file')}")
    
    if response.tests_run:
        passed = sum(1 for t in response.tests_run if t.get("passed"))
        click.echo(f"\n🧪 Tests: {passed}/{len(response.tests_run)} passed")
    
    if response.errors:
        click.echo(f"\n⚠️  Errors:")
        for error in response.errors[:5]:  # Show first 5
            click.echo(f"   • {error}")
    
    if response.warnings:
        click.echo(f"\n⚡ Warnings:")
        for warning in response.warnings[:5]:  # Show first 5
            click.echo(f"   • {warning}")
    
    click.echo(f"\n⏱️  Duration: {response.duration_seconds:.2f}s")
    click.echo(f"🔤 Tokens used: {response.tokens_used:,}")
    
    click.echo("=" * 60)


if __name__ == "__main__":
    main()