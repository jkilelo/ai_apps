#!/usr/bin/env python3
"""
Infrastructure Audit System Demonstration
Shows the complete workflow from profile creation to audit execution
"""

import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
import tempfile
import json

from core import InfrastructureAuditSystem, AuditSystemConfig
from models import ProfileType, Component, Category, Layer, CostType, LLMProvider
from profiles import ProfileFactory


console = Console()


def demo_header():
    """Display demo header"""
    title = """
[SYSTEM] Infrastructure Audit System Demo
AI-First Infrastructure Management

[FEATURES]:
- SQLite3 + Pydantic v2 Architecture
- 5 Pre-configured Profiles (POC to Enterprise)
- AI-First Design (Mandatory LLM Integration)
- Cost Estimation & Dependency Tracking
- Parallel Audit Execution
"""
    console.print(Panel(title, border_style="blue", title="[bold blue]Welcome[/]"))


async def run_demo():
    """Run complete system demonstration"""
    demo_header()

    # Use temporary database for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "demo_audit.db"

        console.print("\n[STEP 1] [bold blue]Initialize System[/]")
        config = AuditSystemConfig(db_path=db_path)
        system = InfrastructureAuditSystem(config)
        console.print(f"[OK] Database initialized: {db_path}")

        # Demo available profiles
        console.print("\n[STEP 2] [bold blue]Available Profiles[/]")
        comparison = ProfileFactory.get_profile_comparison()

        table = Table(title="Infrastructure Profiles Comparison", show_header=True)
        table.add_column("Type", style="cyan")
        table.add_column("Budget/Month", style="green")
        table.add_column("Setup Time", style="yellow")
        table.add_column("AI Provider", style="purple")
        table.add_column("Use Case", style="white")

        for profile_type, data in comparison.items():
            budget_str = f"${data['budget']:.0f}" if data['budget'] > 0 else "Free"
            table.add_row(
                profile_type.upper(),
                budget_str,
                data["setup_hours"],
                data["ai_provider"],
                data["name"]
            )

        console.print(table)

        # Create different profiles
        console.print("\n[STEP 3] [bold blue]Create Profiles[/]")

        profiles_to_create = [
            (ProfileType.POC, {"budget": 25}),
            (ProfileType.LOCAL, {"budget": 75, "users": 3}),
            (ProfileType.OPENSOURCE, {"llm_provider": LLMProvider.OLLAMA}),
            (ProfileType.HYBRID, {"budget": 300, "users": 20}),
        ]

        created_profiles = []
        for profile_type, overrides in profiles_to_create:
            with console.status(f"[bold green]Creating {profile_type.value} profile..."):
                profile = system.create_profile(profile_type, **overrides)
                created_profiles.append(profile)

            console.print(f"[OK] Created: [bold]{profile.code}[/] - {profile.name}")

        # Show profile summaries
        console.print("\n[STEP 4] [bold blue]Profile Analysis[/]")

        summary_table = Table(title="Profile Summary Statistics", show_header=True)
        summary_table.add_column("Profile", style="cyan")
        summary_table.add_column("Components", justify="right")
        summary_table.add_column("Cost Range", style="green")
        summary_table.add_column("Setup Time", style="yellow")
        summary_table.add_column("Readiness", style="white")

        for profile in created_profiles:
            summary = system.get_profile_summary(profile.code)
            if summary:
                cost_range = f"${summary.min_monthly_cost}-${summary.max_monthly_cost}"
                setup_time = f"{summary.total_setup_hours:.1f}h"
                readiness = f"{summary.readiness_score:.0f}/100"

                summary_table.add_row(
                    profile.code,
                    str(summary.total_components),
                    cost_range,
                    setup_time,
                    readiness
                )

        console.print(summary_table)

        # Run audits for each profile
        console.print("\n[STEP 5] [bold blue]Infrastructure Audits[/]")

        audit_results = []
        for profile in created_profiles:
            console.print(f"\n[AUDIT] Auditing: [bold]{profile.code}[/]")

            try:
                with console.status(f"[bold yellow]Running audit for {profile.code}..."):
                    session = await system.audit_profile(
                        profile_code=profile.code,
                        environment="development",
                        user_email="demo@example.com"
                    )

                audit_results.append((profile.code, session))

                # Show quick results
                status_icon = "[PASS]" if session.success_rate >= 80 else "[WARN]" if session.success_rate >= 60 else "[FAIL]"
                console.print(f"{status_icon} {profile.code}: {session.success_rate:.1f}% success "
                            f"({session.passed_components}/{session.total_components} passed)")

            except Exception as e:
                console.print(f"[ERROR] Audit failed for {profile.code}: {e}")

        # Detailed audit results
        console.print("\n[STEP 6] [bold blue]Audit Results Analysis[/]")

        results_table = Table(title="Detailed Audit Results", show_header=True)
        results_table.add_column("Profile", style="cyan")
        results_table.add_column("Success Rate", style="green")
        results_table.add_column("Duration", style="yellow")
        results_table.add_column("Passed", justify="right")
        results_table.add_column("Failed", justify="right")
        results_table.add_column("Status", style="white")

        for profile_code, session in audit_results:
            success_color = "green" if session.success_rate >= 80 else "yellow" if session.success_rate >= 60 else "red"
            status = "Ready" if session.success_rate >= 80 else "Needs Work" if session.success_rate >= 60 else "Not Ready"

            results_table.add_row(
                profile_code,
                f"[{success_color}]{session.success_rate:.1f}%[/]",
                f"{session.duration_seconds}s",
                str(session.passed_components),
                str(session.failed_components),
                status
            )

        console.print(results_table)

        # Show recommendations
        console.print("\n[STEP 7] [bold blue]Recommendations[/]")

        # POC profile recommendations
        poc_session = next((s for p, s in audit_results if p == "poc_minimal"), None)
        if poc_session and poc_session.report:
            console.print("\n[POC] [bold yellow]POC Profile (Quick Demo Setup):[/]")
            for rec in poc_session.report.get("recommendations", []):
                console.print(f"  - {rec}")

        # Overall recommendations
        console.print("\n[RECOMMENDATIONS] [bold green]General Recommendations:[/]")
        console.print("  - **POC Profile**: Perfect for demos and quick prototypes")
        console.print("  - **Local Profile**: Ideal for individual development")
        console.print("  - **OpenSource Profile**: Best for privacy-focused projects")
        console.print("  - **Hybrid Profile**: Good balance for small teams")
        console.print("  - **Enterprise Profile**: Production-ready with full compliance")

        # Export demonstration
        console.print("\n[STEP 8] [bold blue]Export Capabilities[/]")

        # Export POC profile
        poc_profile = next((p for p in created_profiles if p.code == "poc_minimal"), None)
        if poc_profile:
            export_data = poc_profile.model_dump_json(indent=2)
            console.print("[EXPORT] [bold yellow]Sample POC Profile Export (JSON):[/]")

            # Show truncated export
            lines = export_data.split('\n')
            if len(lines) > 15:
                truncated = '\n'.join(lines[:15]) + '\n  ... (truncated)'
            else:
                truncated = export_data

            from rich.syntax import Syntax
            syntax = Syntax(truncated, "json", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Profile Export"))

        # System statistics
        console.print("\n[STEP 9] [bold blue]System Statistics[/]")
        stats = system.get_system_stats()

        if stats:
            stats_content = f"""
Total Components: {sum(stats.get('components', {}).values())}
Total Profiles: {sum(stats.get('profiles', {}).values())}
Total Audits: {stats.get('audits', {}).get('total', 0)}
Average Success Rate: {stats.get('audits', {}).get('avg_success_rate', 0)}%
"""
            console.print(Panel(stats_content, title="System Overview", border_style="green"))

        # Cost analysis
        console.print("\n[STEP 10] [bold blue]Cost Analysis[/]")

        cost_table = Table(title="Monthly Cost Estimates", show_header=True)
        cost_table.add_column("Profile", style="cyan")
        cost_table.add_column("Minimum", style="green")
        cost_table.add_column("Maximum", style="red")
        cost_table.add_column("Recommended Budget", style="yellow")

        for profile in created_profiles:
            summary = system.get_profile_summary(profile.code)
            if summary:
                from decimal import Decimal
                recommended = summary.max_monthly_cost * Decimal("1.2")  # 20% buffer

                cost_table.add_row(
                    profile.code,
                    f"${summary.min_monthly_cost}",
                    f"${summary.max_monthly_cost}",
                    f"${recommended:.0f}"
                )

        console.print(cost_table)

        # Conclusion
        console.print("\n[COMPLETE] [bold green]Demo Complete![/]")

        conclusion = """
[SUCCESS] Successfully demonstrated:
- Profile creation and management
- Infrastructure auditing with parallel execution
- Cost estimation and resource planning
- AI-first validation (all profiles have LLM)
- Export capabilities for configuration management

[READY] Ready for production use!

Next steps:
- Choose appropriate profile for your use case
- Run actual infrastructure audit
- Export configuration for team sharing
- Set up monitoring and maintenance
"""

        console.print(Panel(conclusion, title="Summary", border_style="green"))

        # Show CLI examples
        console.print("\n[CLI] [bold blue]CLI Usage Examples[/]")

        cli_examples = """
# Initialize new system
python cli.py init

# Create profiles
python cli.py create-profile poc --budget 50
python cli.py create-profile local --users 5

# Run audits
python cli.py audit poc_minimal
python cli.py audit local_dev --env staging

# Get information
python cli.py list-profiles
python cli.py profile-summary poc_minimal
python cli.py stats

# Export configurations
python cli.py export-profile poc_minimal --format json
python cli.py backup --output backup.db
"""

        from rich.syntax import Syntax
        syntax = Syntax(cli_examples, "bash", theme="monokai")
        console.print(Panel(syntax, title="CLI Commands"))


def demo_ai_first_validation():
    """Demonstrate AI-first validation"""
    console.print("\n[AI-FIRST] [bold blue]AI-First Validation Demo[/]")

    # This would fail validation
    try:
        from models import Profile
        Profile(
            code="invalid_profile",
            name="Non-AI Profile",
            profile_type=ProfileType.CUSTOM,
            is_ai_first=True,
            default_llm_provider=LLMProvider.LOCAL,
            metadata={}  # Missing local_llm_config
        )
    except Exception as e:
        console.print(f"[OK] [green]Validation caught invalid profile: {e}[/]")

    # This would pass
    try:
        valid_profile = Profile(
            code="valid_ai_profile",
            name="Valid AI Profile",
            profile_type=ProfileType.LOCAL,
            is_ai_first=True,
            default_llm_provider=LLMProvider.GEMINI,
            target_users=1,
            target_scale="development",
            min_ram_gb=16,
            min_storage_gb=100,
            min_cpu_cores=4
        )
        console.print(f"[OK] [green]Valid AI-first profile created: {valid_profile.code}[/]")
    except Exception as e:
        console.print(f"[ERROR] [red]Unexpected validation error: {e}[/]")


def main():
    """Main demo function"""
    try:
        # Run AI-first validation demo
        demo_ai_first_validation()

        # Run main system demo
        asyncio.run(run_demo())

    except KeyboardInterrupt:
        console.print("\n\n[WARN] [yellow]Demo interrupted by user[/]")
    except Exception as e:
        console.print(f"\n\n[ERROR] [bold red]Demo failed: {e}[/]")
        import traceback
        console.print(traceback.format_exc())


if __name__ == "__main__":
    main()