#!/usr/bin/env python3
"""
Infrastructure Audit System CLI
Command-line interface for managing and auditing infrastructure profiles
"""

import asyncio
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich import print as rprint
import json

from core import InfrastructureAuditSystem, AuditSystemConfig
from models import ProfileType, Component, Layer, Category, CostType, LLMProvider
from profiles import ProfileFactory

# Initialize CLI app
app = typer.Typer(
    name="infra-audit",
    help="Infrastructure Audit System - AI-First Infrastructure Management",
    add_completion=False,
    rich_markup_mode="rich"
)

# Rich console for better output
console = Console()


# ============================================
# Global State
# ============================================

def get_audit_system(db_path: Optional[str] = None) -> InfrastructureAuditSystem:
    """Get initialized audit system"""
    config = AuditSystemConfig()
    if db_path:
        config.db_path = Path(db_path)
    return InfrastructureAuditSystem(config)


# ============================================
# Profile Commands
# ============================================

@app.command("create-profile")
def create_profile(
    profile_type: ProfileType = typer.Argument(..., help="Profile type"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Custom profile name"),
    budget: Optional[float] = typer.Option(None, "--budget", "-b", help="Monthly budget limit"),
    users: Optional[int] = typer.Option(None, "--users", "-u", help="Target number of users"),
    llm_provider: Optional[LLMProvider] = typer.Option(None, "--llm", help="Default LLM provider"),
    db_path: Optional[str] = typer.Option(None, "--db", help="Database path"),
):
    """Create a new infrastructure profile"""
    try:
        system = get_audit_system(db_path)

        # Prepare overrides
        overrides = {}
        if name:
            overrides["name"] = name
        if budget:
            overrides["max_monthly_budget"] = budget
        if users:
            overrides["target_users"] = users
        if llm_provider:
            overrides["default_llm_provider"] = llm_provider

        with console.status(f"[bold green]Creating {profile_type.value} profile..."):
            profile = system.create_profile(profile_type, **overrides)

        # Display created profile
        rprint(f"\n[OK] [bold green]Profile created successfully![/]")
        rprint(f"[INFO] **Code**: {profile.code}")
        rprint(f"[NAME] **Name**: {profile.name}")
        rprint(f"[TYPE] **Type**: {profile.profile_type.value}")
        rprint(f"[AI] **AI Provider**: {profile.default_llm_provider.value}")
        rprint(f"[USERS] **Target Users**: {profile.target_users}")
        rprint(f"[BUDGET] **Budget**: ${profile.max_monthly_budget or 'No limit'}")

    except Exception as e:
        rprint(f"[ERROR] [bold red]Error creating profile: {e}[/]")
        raise typer.Exit(1)


@app.command("list-profiles")
def list_profiles(
    db_path: Optional[str] = typer.Option(None, "--db", help="Database path")
):
    """List available profile types and their characteristics"""
    try:
        comparison = ProfileFactory.get_profile_comparison()

        table = Table(title="Available Infrastructure Profiles", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Name", style="white")
        table.add_column("Users", justify="right")
        table.add_column("Scale", style="yellow")
        table.add_column("Budget/Month", justify="right", style="green")
        table.add_column("RAM (GB)", justify="right")
        table.add_column("GPU", justify="center")
        table.add_column("Setup Time", style="blue")
        table.add_column("AI Provider", style="purple")

        for profile_type, data in comparison.items():
            gpu_icon = "Yes" if data["gpu_required"] else "No"
            budget_str = f"${data['budget']:.0f}" if data['budget'] > 0 else "Free"

            table.add_row(
                profile_type.upper(),
                data["name"],
                str(data["users"]),
                data["scale"],
                budget_str,
                str(data["ram_gb"]),
                gpu_icon,
                data["setup_hours"],
                data["ai_provider"]
            )

        console.print(table)

        # Add recommendations
        rprint("\n[TIP] [bold yellow]Recommendations:[/]")
        rprint("- **POC**: Quick demos and prototypes (< 2 hours)")
        rprint("- **Local**: Individual development (< 8 hours)")
        rprint("- **OpenSource**: Privacy-focused, no proprietary APIs")
        rprint("- **Enterprise**: Production-ready with full compliance")
        rprint("- **Hybrid**: Balanced mix of open source and commercial")

    except Exception as e:
        rprint(f"❌ [bold red]Error listing profiles: {e}[/]")
        raise typer.Exit(1)


@app.command("profile-summary")
def profile_summary(
    profile_code: str = typer.Argument(..., help="Profile code"),
    db_path: Optional[str] = typer.Option(None, "--db", help="Database path")
):
    """Show detailed profile summary with statistics"""
    try:
        system = get_audit_system(db_path)

        with console.status(f"[bold blue]Analyzing profile {profile_code}..."):
            summary = system.get_profile_summary(profile_code)

        if not summary:
            rprint(f"[ERROR] [bold red]Profile not found: {profile_code}[/]")
            raise typer.Exit(1)

        profile = summary.profile

        # Profile header
        panel_content = f"""
[bold]{profile.name}[/]
[ID] Code: {profile.code}
[TYPE] Type: {profile.profile_type.value}
[AI] AI-First: {"Yes" if profile.is_ai_first else "No"} ({profile.default_llm_provider.value})
[SCALE] Scale: {profile.target_scale.value}
[USERS] Users: {profile.target_users}
"""
        console.print(Panel(panel_content, title="Profile Information", border_style="blue"))

        # Statistics table
        stats_table = Table(title="Component Statistics", show_header=True)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", justify="right", style="white")

        stats_table.add_row("Total Components", str(summary.total_components))
        stats_table.add_row("Required", str(summary.required_components))
        stats_table.add_row("Optional", str(summary.optional_components))
        stats_table.add_row("Free", str(summary.free_components))
        stats_table.add_row("Paid", str(summary.paid_components))

        console.print(stats_table)

        # Cost and resources
        cost_table = Table(title="Cost & Resource Estimates", show_header=True)
        cost_table.add_column("Resource", style="cyan")
        cost_table.add_column("Requirement", justify="right", style="white")

        cost_table.add_row("Monthly Cost (Min)", f"${summary.min_monthly_cost}")
        cost_table.add_row("Monthly Cost (Max)", f"${summary.max_monthly_cost}")
        cost_table.add_row("Setup Time", f"{summary.total_setup_hours:.1f} hours")
        cost_table.add_row("Complexity (1-5)", f"{summary.average_complexity:.1f}")
        cost_table.add_row("RAM Required", f"{summary.total_min_ram_gb} GB")
        cost_table.add_row("Storage Required", f"{summary.total_min_storage_gb} GB")
        cost_table.add_row("GPU Required", "Yes" if summary.requires_gpu else "No")

        console.print(cost_table)

        # Readiness score
        score_color = "green" if summary.readiness_score >= 80 else "yellow" if summary.readiness_score >= 60 else "red"
        rprint(f"\n[SCORE] **Readiness Score**: [{score_color}]{summary.readiness_score:.0f}/100[/]")

        if summary.is_budget_friendly:
            rprint("[OK] [bold green]Within budget constraints[/]")
        else:
            rprint("[WARN] [bold red]Exceeds budget limits[/]")

    except Exception as e:
        rprint(f"❌ [bold red]Error getting profile summary: {e}[/]")
        raise typer.Exit(1)


# ============================================
# Audit Commands
# ============================================

@app.command("audit")
def run_audit(
    profile_code: str = typer.Argument(..., help="Profile code to audit"),
    environment: str = typer.Option("development", "--env", "-e", help="Target environment"),
    user_email: Optional[str] = typer.Option(None, "--user", help="User email for audit trail"),
    db_path: Optional[str] = typer.Option(None, "--db", help="Database path")
):
    """Run infrastructure audit for a profile"""
    try:
        system = get_audit_system(db_path)

        rprint(f"\n[AUDIT] [bold blue]Starting infrastructure audit for profile: {profile_code}[/]")

        # Run audit with progress indicator
        async def run_audit_async():
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Running audit checks...", total=None)

                session = await system.audit_profile(
                    profile_code=profile_code,
                    environment=environment,
                    user_email=user_email
                )

                progress.update(task, description="Audit completed!")
                return session

        # Run async audit
        session = asyncio.run(run_audit_async())

        # Display results
        rprint(f"\n[OK] [bold green]Audit completed![/]")
        rprint(f"[ID] Session ID: {session.session_id}")
        rprint(f"[TIME] Duration: {session.duration_seconds}s")
        rprint(f"[STATS] Success Rate: {session.success_rate:.1f}%")

        # Results table
        results_table = Table(title="Audit Results", show_header=True)
        results_table.add_column("Status", style="cyan")
        results_table.add_column("Count", justify="right", style="white")
        results_table.add_column("Percentage", justify="right", style="yellow")

        total = session.total_components
        results_table.add_row("[PASS] Passed", str(session.passed_components), f"{(session.passed_components/total)*100:.1f}%")
        results_table.add_row("[FAIL] Failed", str(session.failed_components), f"{(session.failed_components/total)*100:.1f}%")
        results_table.add_row("[SKIP] Skipped", str(session.skipped_components), f"{(session.skipped_components/total)*100:.1f}%")

        console.print(results_table)

        # Recommendations
        if session.report and session.report.get("recommendations"):
            rprint("\n[TIP] [bold yellow]Recommendations:[/]")
            for rec in session.report["recommendations"]:
                rprint(f"- {rec}")

        # Next steps
        if session.report and session.report.get("next_steps"):
            rprint("\n[NEXT] [bold cyan]Next Steps:[/]")
            for step in session.report["next_steps"]:
                rprint(f"- {step}")

    except Exception as e:
        rprint(f"[ERROR] [bold red]Audit failed: {e}[/]")
        raise typer.Exit(1)


# ============================================
# System Commands
# ============================================

@app.command("init")
def initialize_system(
    db_path: Optional[str] = typer.Option(None, "--db", help="Database path"),
    force: bool = typer.Option(False, "--force", help="Force reinitialize")
):
    """Initialize the audit system database"""
    try:
        config = AuditSystemConfig()
        if db_path:
            config.db_path = Path(db_path)

        if config.db_path.exists() and not force:
            rprint(f"[WARN] [yellow]Database already exists: {config.db_path}[/]")
            rprint("Use --force to reinitialize")
            return

        if force and config.db_path.exists():
            config.db_path.unlink()

        with console.status("[bold green]Initializing audit system..."):
            system = InfrastructureAuditSystem(config)

        rprint(f"[OK] [bold green]Audit system initialized successfully![/]")
        rprint(f"[DB] Database: {config.db_path}")
        rprint(f"[VERSION] Schema version: 1.0.0")

        # Show stats
        stats = system.get_system_stats()
        if stats:
            rprint(f"[STATS] Components: {sum(stats.get('components', {}).values())}")
            rprint(f"[PROFILES] Profiles: {sum(stats.get('profiles', {}).values())}")

    except Exception as e:
        rprint(f"[ERROR] [bold red]Initialization failed: {e}[/]")
        raise typer.Exit(1)


@app.command("stats")
def system_stats(
    db_path: Optional[str] = typer.Option(None, "--db", help="Database path")
):
    """Show system statistics"""
    try:
        system = get_audit_system(db_path)
        stats = system.get_system_stats()

        rprint("\n[STATS] [bold blue]System Statistics[/]")

        if stats.get('components'):
            rprint("\n[COMPONENTS] **Components by Cost Type:**")
            for cost_type, count in stats['components'].items():
                rprint(f"  - {cost_type}: {count}")

        if stats.get('profiles'):
            rprint("\n[PROFILES] **Profiles by Type:**")
            for profile_type, count in stats['profiles'].items():
                rprint(f"  - {profile_type}: {count}")

        if stats.get('audits'):
            rprint("\n[AUDITS] **Audit Statistics:**")
            rprint(f"  - Total audits: {stats['audits']['total']}")
            rprint(f"  - Average success rate: {stats['audits']['avg_success_rate']}%")

    except Exception as e:
        rprint(f"[ERROR] [bold red]Error getting stats: {e}[/]")
        raise typer.Exit(1)


@app.command("backup")
def backup_system(
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Backup file path"),
    db_path: Optional[str] = typer.Option(None, "--db", help="Database path")
):
    """Create system backup"""
    try:
        system = get_audit_system(db_path)

        with console.status("[bold blue]Creating backup..."):
            backup_path = system.backup_system()

        rprint(f"[OK] [bold green]Backup created successfully![/]")
        rprint(f"[FILE] Backup file: {backup_path}")

    except Exception as e:
        rprint(f"[ERROR] [bold red]Backup failed: {e}[/]")
        raise typer.Exit(1)


# ============================================
# Utility Commands
# ============================================

@app.command("export-profile")
def export_profile(
    profile_code: str = typer.Argument(..., help="Profile code to export"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json/yaml)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    db_path: Optional[str] = typer.Option(None, "--db", help="Database path")
):
    """Export profile configuration"""
    try:
        system = get_audit_system(db_path)
        profile = system.get_profile(profile_code)

        if not profile:
            rprint(f"[ERROR] [bold red]Profile not found: {profile_code}[/]")
            raise typer.Exit(1)

        # Export profile
        if format.lower() == "json":
            content = profile.model_dump_json(indent=2)
            extension = ".json"
        elif format.lower() == "yaml":
            import yaml
            content = yaml.dump(profile.model_dump(), default_flow_style=False)
            extension = ".yaml"
        else:
            rprint(f"[ERROR] [bold red]Unsupported format: {format}[/]")
            raise typer.Exit(1)

        # Determine output path
        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"{profile_code}_profile{extension}")

        # Write file
        output_path.write_text(content)

        rprint(f"[OK] [bold green]Profile exported successfully![/]")
        rprint(f"[FILE] File: {output_path}")

        # Show preview
        if format.lower() == "json":
            syntax = Syntax(content[:500] + "..." if len(content) > 500 else content, "json")
            console.print(Panel(syntax, title="Preview"))

    except Exception as e:
        rprint(f"[ERROR] [bold red]Export failed: {e}[/]")
        raise typer.Exit(1)


@app.command("version")
def show_version():
    """Show version information"""
    rprint("\n[bold blue]Infrastructure Audit System[/]")
    rprint("Version: 1.0.0")
    rprint("Python: 3.13+")
    rprint("AI-First: Yes")
    rprint("Database: SQLite3")
    rprint("Models: Pydantic v2")
    rprint("\nUse --help with any command for more information")


# ============================================
# Main Entry Point
# ============================================

def main():
    """Main CLI entry point"""
    app()


if __name__ == "__main__":
    main()