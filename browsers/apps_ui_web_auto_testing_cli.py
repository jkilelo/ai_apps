#!/usr/bin/env python3
"""
UI Web Auto Testing CLI - Command Line Interface for the 4-step automation framework
"""

import click
import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.syntax import Syntax
from datetime import datetime

from .sdk import WebAutomationSDK, WorkflowConfig, ExecutionConfig

console = Console()

class CLIContext:
    """CLI Context Manager"""
    def __init__(self):
        self.sdk = WebAutomationSDK()
        self.config_file = Path.home() / ".web_automation" / "config.json"
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.sdk.api_base_url = config.get('api_base_url', self.sdk.api_base_url)
    
    def save_config(self):
        """Save configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        config = {
            'api_base_url': self.sdk.api_base_url,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

# Create CLI group
@click.group()
@click.pass_context
def cli(ctx):
    """
    Web Automation Testing CLI - A powerful framework for automated web testing
    
    This CLI provides a 4-step workflow for comprehensive web automation:
    
    \b
    1. TARGET SETUP - Analyze URLs and extract elements
    2. WORKFLOW BUILD - Generate test cases
    3. TEST EXECUTION - Run automated tests
    4. RESULTS REPORT - Get comprehensive results
    
    Use 'web-automation run' for a complete workflow or individual commands for each step.
    """
    ctx.obj = CLIContext()

# ===== WORKFLOW COMMANDS =====

@cli.command()
@click.option('--url', '-u', required=True, help='Target URL to test')
@click.option('--name', '-n', default='Test Suite', help='Name for the test suite')
@click.option('--profile', '-p', default='qa_tester', 
              type=click.Choice(['qa_tester', 'developer', 'accessibility_tester']),
              help='Testing profile to use')
@click.option('--browser', '-b', default='chrome', 
              type=click.Choice(['chrome', 'firefox', 'safari', 'edge']),
              help='Browser for testing')
@click.option('--parallel', is_flag=True, help='Run tests in parallel')
@click.option('--cross-browser', is_flag=True, help='Enable cross-browser testing')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--format', '-f', default='json', 
              type=click.Choice(['json', 'html', 'pdf']),
              help='Output format')
@click.pass_obj
async def run(ctx_obj, url, name, profile, browser, parallel, cross_browser, output, format):
    """Run complete 4-step automated testing workflow"""
    console.print(Panel.fit(
        f"[bold cyan]Web Automation Testing Workflow[/bold cyan]\n"
        f"Target: {url}\n"
        f"Profile: {profile}\n"
        f"Browser: {browser}",
        title="Starting Workflow"
    ))
    
    workflow_config = WorkflowConfig(
        target_url=url,
        test_name=name,
        profile=profile,
        browser_type=browser,
        include_accessibility=True
    )
    
    execution_config = ExecutionConfig(
        execution_mode='parallel' if parallel else 'sequential',
        cross_browser=cross_browser,
        capture_screenshots=True
    )
    
    try:
        # Run complete workflow with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            # Track overall progress
            overall_task = progress.add_task("[cyan]Running workflow...", total=4)
            
            # Step 1: Target Setup
            progress.update(overall_task, description="[yellow]Step 1: Analyzing target URL...")
            session = await ctx_obj.sdk.start_workflow(workflow_config)
            progress.update(overall_task, advance=1)
            console.print(f"✓ Session created: {session.session_id}")
            
            # Step 2: Workflow Builder  
            progress.update(overall_task, description="[yellow]Step 2: Building test workflow...")
            await ctx_obj.sdk.wait_for_step_completion(session.session_id, 1)
            await ctx_obj.sdk.build_workflow(session.session_id)
            await ctx_obj.sdk.wait_for_step_completion(session.session_id, 2)
            progress.update(overall_task, advance=1)
            console.print("✓ Test workflow built")
            
            # Step 3: Test Execution
            progress.update(overall_task, description="[yellow]Step 3: Executing tests...")
            await ctx_obj.sdk.execute_tests(session.session_id, execution_config)
            await ctx_obj.sdk.wait_for_step_completion(session.session_id, 3)
            progress.update(overall_task, advance=1)
            console.print("✓ Tests executed")
            
            # Step 4: Results & Report
            progress.update(overall_task, description="[yellow]Step 4: Generating report...")
            results = await ctx_obj.sdk.get_results(session.session_id, format)
            progress.update(overall_task, advance=1)
            
        # Display results
        display_results(results)
        
        # Save to file if requested
        if output:
            save_results(results, output, format)
            console.print(f"\n✓ Results saved to: {output}")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

# ===== INDIVIDUAL STEP COMMANDS =====

@cli.group()
def step():
    """Execute individual workflow steps"""
    pass

@step.command('target')
@click.option('--url', '-u', required=True, help='Target URL to analyze')
@click.option('--profile', '-p', default='qa_tester', help='Testing profile')
@click.option('--output', '-o', help='Save session ID to file')
@click.pass_obj
async def target_setup(ctx_obj, url, profile, output):
    """Step 1: Analyze target URL and extract elements"""
    console.print(f"[cyan]Analyzing target URL: {url}[/cyan]")
    
    config = WorkflowConfig(
        target_url=url,
        test_name=f"Analysis of {url}",
        profile=profile
    )
    
    session = await ctx_obj.sdk.start_workflow(config)
    console.print(f"✓ Session created: {session.session_id}")
    
    # Wait for completion
    with console.status("Extracting elements..."):
        await ctx_obj.sdk.wait_for_step_completion(session.session_id, 1)
    
    status = await ctx_obj.sdk.get_workflow_status(session.session_id)
    elements_count = len(status.elements_data.get('elements', []))
    
    console.print(f"✓ Extracted {elements_count} elements")
    
    if output:
        with open(output, 'w') as f:
            json.dump({'session_id': session.session_id}, f)

@step.command('build')
@click.option('--session-id', '-s', required=True, help='Session ID from target step')
@click.option('--test-types', '-t', multiple=True, default=['functional'], 
              help='Types of tests to generate')
@click.pass_obj
async def build_workflow(ctx_obj, session_id, test_types):
    """Step 2: Build test workflow from extracted elements"""
    console.print(f"[cyan]Building test workflow for session: {session_id}[/cyan]")
    
    await ctx_obj.sdk.build_workflow(session_id, list(test_types))
    
    with console.status("Generating test cases..."):
        await ctx_obj.sdk.wait_for_step_completion(session_id, 2)
    
    status = await ctx_obj.sdk.get_workflow_status(session_id)
    test_count = len(status.workflow_data.get('test_cases', []))
    
    console.print(f"✓ Generated {test_count} test cases")

@step.command('execute')
@click.option('--session-id', '-s', required=True, help='Session ID')
@click.option('--parallel', is_flag=True, help='Run tests in parallel')
@click.option('--browser', '-b', default='chrome', help='Browser to use')
@click.pass_obj
async def execute_tests(ctx_obj, session_id, parallel, browser):
    """Step 3: Execute generated test cases"""
    console.print(f"[cyan]Executing tests for session: {session_id}[/cyan]")
    
    config = ExecutionConfig(
        execution_mode='parallel' if parallel else 'sequential',
        browser=browser
    )
    
    await ctx_obj.sdk.execute_tests(session_id, config)
    
    with console.status("Running tests..."):
        await ctx_obj.sdk.wait_for_step_completion(session_id, 3)
    
    status = await ctx_obj.sdk.get_workflow_status(session_id)
    execution_data = status.execution_data
    
    console.print(f"✓ Executed {execution_data['total_tests']} tests")
    console.print(f"  Passed: {execution_data['passed_tests']}")
    console.print(f"  Failed: {execution_data['failed_tests']}")

@step.command('report')
@click.option('--session-id', '-s', required=True, help='Session ID')
@click.option('--format', '-f', default='json', 
              type=click.Choice(['json', 'html', 'pdf']),
              help='Report format')
@click.option('--output', '-o', help='Output file')
@click.pass_obj
async def get_report(ctx_obj, session_id, format, output):
    """Step 4: Generate test results report"""
    console.print(f"[cyan]Generating report for session: {session_id}[/cyan]")
    
    results = await ctx_obj.sdk.get_results(session_id, format)
    
    display_results(results)
    
    if output:
        save_results(results, output, format)
        console.print(f"\n✓ Report saved to: {output}")

# ===== SESSION MANAGEMENT COMMANDS =====

@cli.group()
def session():
    """Manage workflow sessions"""
    pass

@session.command('list')
@click.pass_obj
async def list_sessions(ctx_obj):
    """List all workflow sessions"""
    sessions = await ctx_obj.sdk.list_sessions()
    
    if not sessions:
        console.print("[yellow]No active sessions found[/yellow]")
        return
    
    table = Table(title="Active Workflow Sessions")
    table.add_column("Session ID", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Current Step")
    table.add_column("Created At")
    table.add_column("Target URL")
    
    for session in sessions:
        table.add_row(
            session.session_id,
            session.status,
            str(session.current_step),
            session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            session.target_data.get('target_url', 'N/A') if session.target_data else 'N/A'
        )
    
    console.print(table)

@session.command('status')
@click.argument('session_id')
@click.option('--watch', '-w', is_flag=True, help='Watch session progress')
@click.pass_obj
async def session_status(ctx_obj, session_id, watch):
    """Get detailed session status"""
    if watch:
        with console.status(f"Watching session {session_id}...") as status:
            while True:
                session = await ctx_obj.sdk.get_workflow_status(session_id)
                status.update(f"Session {session_id} - Step {session.current_step}/4 - {session.status}")
                
                if session.status == 'completed':
                    break
                
                await asyncio.sleep(2)
    
    session = await ctx_obj.sdk.get_workflow_status(session_id)
    
    console.print(Panel.fit(
        f"[bold]Session Details[/bold]\n\n"
        f"ID: {session.session_id}\n"
        f"Status: {session.status}\n"
        f"Current Step: {session.current_step}/4\n"
        f"Created: {session.created_at}\n"
        f"Steps Completed: {', '.join(session.steps_completed)}",
        title=f"Session {session_id}"
    ))

@session.command('delete')
@click.argument('session_id')
@click.confirmation_option(prompt='Are you sure you want to delete this session?')
@click.pass_obj
async def delete_session(ctx_obj, session_id):
    """Delete a workflow session"""
    await ctx_obj.sdk.delete_session(session_id)
    console.print(f"✓ Session {session_id} deleted")

# ===== CONFIGURATION COMMANDS =====

@cli.group()
def config():
    """Manage CLI configuration"""
    pass

@config.command('set')
@click.option('--api-url', help='API base URL')
@click.pass_obj
def config_set(ctx_obj, api_url):
    """Set configuration values"""
    if api_url:
        ctx_obj.sdk.api_base_url = api_url
        ctx_obj.save_config()
        console.print(f"✓ API URL set to: {api_url}")

@config.command('show')
@click.pass_obj
def config_show(ctx_obj):
    """Show current configuration"""
    console.print(Panel.fit(
        f"[bold]Current Configuration[/bold]\n\n"
        f"API URL: {ctx_obj.sdk.api_base_url}\n"
        f"Config File: {ctx_obj.config_file}",
        title="Web Automation CLI Config"
    ))

# ===== UTILITY FUNCTIONS =====

def display_results(results: Dict[str, Any]):
    """Display test results in a formatted way"""
    console.print("\n[bold cyan]Test Results Summary[/bold cyan]")
    
    # Session info
    session_info = results.get('session_info', {})
    console.print(f"\nTest Name: {session_info.get('test_name', 'N/A')}")
    console.print(f"Target URL: {session_info.get('target_url', 'N/A')}")
    
    # Metrics
    metrics = results.get('metrics', {})
    console.print(f"\n[bold]Performance Metrics:[/bold]")
    console.print(f"  Success Rate: {metrics.get('success_rate', 0):.1f}%")
    console.print(f"  Coverage Score: {metrics.get('coverage_score', 0):.1f}%")
    console.print(f"  Accessibility: {metrics.get('accessibility_compliance', 0):.1f}%")
    
    # Test execution summary
    test_exec = results.get('test_execution', {})
    console.print(f"\n[bold]Test Execution:[/bold]")
    console.print(f"  Total Tests: {test_exec.get('total_tests', 0)}")
    console.print(f"  Passed: [green]{test_exec.get('passed_tests', 0)}[/green]")
    console.print(f"  Failed: [red]{test_exec.get('failed_tests', 0)}[/red]")
    console.print(f"  Duration: {test_exec.get('execution_time', 0):.2f}s")
    
    # Failed tests details
    failed_tests = [t for t in test_exec.get('test_results', []) if t.get('status') == 'failed']
    if failed_tests:
        console.print(f"\n[bold red]Failed Tests:[/bold red]")
        for test in failed_tests:
            console.print(f"  - {test.get('name', 'Unknown')}: {test.get('error', 'No error message')}")

def save_results(results: Dict[str, Any], output_path: str, format: str):
    """Save results to file"""
    output_path = Path(output_path)
    
    if format == 'json':
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    elif format == 'html':
        # Generate HTML report
        html_content = generate_html_report(results)
        with open(output_path, 'w') as f:
            f.write(html_content)
    elif format == 'pdf':
        # Would need PDF generation library
        console.print("[yellow]PDF export not yet implemented[/yellow]")

def generate_html_report(results: Dict[str, Any]) -> str:
    """Generate HTML report from results"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Web Automation Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; }}
        .metrics {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background: #e8f5e9; padding: 15px; border-radius: 5px; }}
        .failed {{ background: #ffebee; }}
        .passed {{ background: #e8f5e9; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Web Automation Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <h2>Test Summary</h2>
    <div class="metrics">
        <div class="metric">
            <h3>Success Rate</h3>
            <p>{results.get('metrics', {}).get('success_rate', 0):.1f}%</p>
        </div>
        <div class="metric">
            <h3>Total Tests</h3>
            <p>{results.get('test_execution', {}).get('total_tests', 0)}</p>
        </div>
        <div class="metric passed">
            <h3>Passed</h3>
            <p>{results.get('test_execution', {}).get('passed_tests', 0)}</p>
        </div>
        <div class="metric failed">
            <h3>Failed</h3>
            <p>{results.get('test_execution', {}).get('failed_tests', 0)}</p>
        </div>
    </div>
    
    <h2>Test Results</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Error</th>
        </tr>
        {"".join(f'''
        <tr class="{test.get('status', 'unknown')}">
            <td>{test.get('name', 'Unknown')}</td>
            <td>{test.get('status', 'Unknown')}</td>
            <td>{test.get('duration', 0):.2f}s</td>
            <td>{test.get('error', '')}</td>
        </tr>
        ''' for test in results.get('test_execution', {}).get('test_results', []))}
    </table>
</body>
</html>
"""

# Main entry point
def main():
    """Main CLI entry point with async support"""
    def run_async(coro):
        """Run async function in sync context"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    
    # Patch click commands to support async
    for name, cmd in cli.commands.items():
        if asyncio.iscoroutinefunction(cmd.callback):
            orig_callback = cmd.callback
            cmd.callback = lambda *args, **kwargs: run_async(orig_callback(*args, **kwargs))
    
    # Handle subcommands
    for group_name, group in cli.commands.items():
        if hasattr(group, 'commands'):
            for name, cmd in group.commands.items():
                if asyncio.iscoroutinefunction(cmd.callback):
                    orig_callback = cmd.callback
                    cmd.callback = lambda *args, **kwargs: run_async(orig_callback(*args, **kwargs))
    
    cli()

if __name__ == '__main__':
    main()