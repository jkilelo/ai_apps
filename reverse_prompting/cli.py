"""
Main CLI Interface for Reverse Prompting Engine

This module provides a command-line interface for the reverse prompting system,
allowing users to easily run reverse prompting operations from the terminal.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List
import logging

from .core.models import CodeArtifact, CodeLanguage, EngineConfig, PromptStrategy
from .engines.reverse_engine import ReversePromptingEngine
from .utils.monitoring import start_global_monitoring, stop_global_monitoring


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_code_from_file(file_path: Path) -> CodeArtifact:
    """Load code from a file and create a CodeArtifact."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Determine language from file extension
    language_map = {
        ".py": CodeLanguage.PYTHON,
        ".js": CodeLanguage.JAVASCRIPT,
        ".ts": CodeLanguage.TYPESCRIPT,
        ".java": CodeLanguage.JAVA,
        ".cs": CodeLanguage.CSHARP,
        ".cpp": CodeLanguage.CPP,
        ".cc": CodeLanguage.CPP,
        ".cxx": CodeLanguage.CPP,
        ".rs": CodeLanguage.RUST,
        ".go": CodeLanguage.GO,
    }

    language = language_map.get(file_path.suffix.lower(), CodeLanguage.PYTHON)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return CodeArtifact(
        name=file_path.stem,
        language=language,
        content=content,
        description=f"Code loaded from {file_path}",
        metadata={
            "file_path": str(file_path),
            "file_size": len(content),
            "language_detected": language.value,
        },
    )


def parse_strategies(strategy_names: List[str]) -> List[PromptStrategy]:
    """Parse strategy names into PromptStrategy enums."""
    strategies = []
    strategy_map = {strategy.value: strategy for strategy in PromptStrategy}

    for name in strategy_names:
        if name in strategy_map:
            strategies.append(strategy_map[name])
        else:
            available = ", ".join(strategy_map.keys())
            raise ValueError(f"Unknown strategy '{name}'. Available: {available}")

    return strategies


async def run_reverse_prompting(args):
    """Run the reverse prompting process."""
    # Setup logging
    setup_logging(args.log_level)

    # Start monitoring if enabled
    if args.enable_monitoring:
        start_global_monitoring(args.monitoring_interval)

    try:
        # Load the target code
        print(f"Loading code from: {args.input_file}")
        target_code = load_code_from_file(Path(args.input_file))
        print(
            f"Loaded {target_code.language.value} code: {len(target_code.content)} characters"
        )

        # Parse strategies
        strategies = None
        if args.strategies:
            strategies = parse_strategies(args.strategies)
            print(f"Using strategies: {[s.value for s in strategies]}")

        # Create engine configuration
        config = EngineConfig(
            max_iterations=args.max_iterations,
            parallel_strategies=args.parallel_strategies,
            success_threshold=args.success_threshold,
            enable_evolution=args.enable_evolution,
            enable_monitoring=args.enable_monitoring,
            enable_caching=args.enable_caching,
            storage_backend=args.storage_backend,
            storage_path=args.storage_path,
            log_level=args.log_level.upper(),
        )

        # Configure LLM providers
        if args.openai_api_key:
            config.openai_config = {
                "api_key": args.openai_api_key,
                "model": args.openai_model,
            }

        if args.anthropic_api_key:
            config.anthropic_config = {
                "api_key": args.anthropic_api_key,
                "model": args.anthropic_model,
            }

        if args.google_api_key:
            config.google_config = {
                "api_key": args.google_api_key,
                "model": args.google_model,
            }

        # Create and run the engine
        engine = ReversePromptingEngine(config=config)

        print(f"\nStarting reverse prompting session: {args.session_name}")
        print("=" * 60)

        session = await engine.run_reverse_prompting(
            target_code=target_code,
            session_name=args.session_name,
            target_description=args.description,
            strategies=strategies,
            max_iterations=args.max_iterations,
        )

        # Display results
        print("\n" + "=" * 60)
        print("REVERSE PROMPTING COMPLETED")
        print("=" * 60)

        print(f"Session ID: {session.id}")
        print(f"Total prompts generated: {len(session.generated_prompts)}")
        print(f"Total artifacts generated: {len(session.generated_artifacts)}")
        print(f"Total evaluations: {len(session.evaluations)}")
        print(f"Success rate: {session.get_success_rate():.2%}")

        if session.best_result:
            print(f"Best score: {session.best_result.overall_score:.3f}")
            print(
                f"Best prompt strategy: {session.best_result.metadata.get('strategy', 'Unknown')}"
            )

        # Save results if requested
        if args.output_file:
            output_path = Path(args.output_file)
            output_data = {
                "session": session.dict(),
                "summary": {
                    "session_id": str(session.id),
                    "session_name": session.name,
                    "target_code": target_code.dict(),
                    "total_prompts": len(session.generated_prompts),
                    "total_evaluations": len(session.evaluations),
                    "success_rate": session.get_success_rate(),
                    "best_score": (
                        session.best_result.overall_score
                        if session.best_result
                        else 0.0
                    ),
                },
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, default=str)

            print(f"\nResults saved to: {output_path}")

        # Cleanup
        await engine.cleanup()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    finally:
        if args.enable_monitoring:
            stop_global_monitoring()

    return 0


async def list_sessions(args):
    """List existing sessions."""
    config = EngineConfig(
        storage_backend=args.storage_backend, storage_path=args.storage_path
    )

    engine = ReversePromptingEngine(config=config)

    try:
        sessions = await engine.list_sessions(args.limit)

        if not sessions:
            print("No sessions found.")
            return 0

        print(f"Found {len(sessions)} sessions:")
        print("=" * 80)
        print(
            f"{'ID':<8} {'Name':<20} {'Created':<20} {'Best Score':<12} {'Success Rate':<12}"
        )
        print("-" * 80)

        for session_info in sessions:
            print(
                f"{session_info['id'][:8]:<8} {session_info['name'][:20]:<20} "
                f"{session_info['created_at'][:19]:<20} {session_info['best_score']:<12.3f} "
                f"{session_info['success_rate']:<12.2%}"
            )

        await engine.cleanup()
        return 0

    except Exception as e:
        print(f"Error listing sessions: {e}", file=sys.stderr)
        return 1


async def show_session(args):
    """Show details of a specific session."""
    config = EngineConfig(
        storage_backend=args.storage_backend, storage_path=args.storage_path
    )

    engine = ReversePromptingEngine(config=config)

    try:
        status = await engine.get_session_status(args.session_id)

        if not status:
            print(f"Session not found: {args.session_id}")
            return 1

        print("Session Details:")
        print("=" * 50)
        for key, value in status.items():
            print(f"{key}: {value}")

        await engine.cleanup()
        return 0

    except Exception as e:
        print(f"Error showing session: {e}", file=sys.stderr)
        return 1


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Reverse Prompting Engine - Generate high-quality prompts from existing code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with Python file
  python -m reverse_prompting run my_script.py

  # Use specific strategies
  python -m reverse_prompting run my_script.py --strategies chain_of_thought few_shot

  # Enable evolution and monitoring
  python -m reverse_prompting run my_script.py --enable-evolution --enable-monitoring

  # Use specific LLM with API key
  python -m reverse_prompting run my_script.py --openai-api-key YOUR_KEY

  # List existing sessions
  python -m reverse_prompting list

  # Show session details
  python -m reverse_prompting show SESSION_ID
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser(
        "run", help="Run reverse prompting on a code file"
    )
    run_parser.add_argument("input_file", help="Path to the code file to analyze")
    run_parser.add_argument(
        "--session-name",
        default="reverse_prompting_session",
        help="Name for this reverse prompting session",
    )
    run_parser.add_argument(
        "--description", help="Description of what the code should do"
    )
    run_parser.add_argument(
        "--strategies",
        nargs="+",
        choices=[
            "zero_shot",
            "few_shot",
            "chain_of_thought",
            "self_consistency",
            "tree_of_thoughts",
            "mixture_of_experts",
            "meta_prompting",
        ],
        help="Prompting strategies to use",
    )
    run_parser.add_argument(
        "--max-iterations", type=int, default=10, help="Maximum iterations per strategy"
    )
    run_parser.add_argument(
        "--parallel-strategies",
        type=int,
        default=1,
        help="Number of strategies to run in parallel",
    )
    run_parser.add_argument(
        "--success-threshold",
        type=float,
        default=0.8,
        help="Success threshold for early termination",
    )
    run_parser.add_argument(
        "--enable-evolution",
        action="store_true",
        help="Enable evolutionary prompt improvement",
    )
    run_parser.add_argument(
        "--enable-monitoring", action="store_true", help="Enable performance monitoring"
    )
    run_parser.add_argument(
        "--monitoring-interval",
        type=float,
        default=5.0,
        help="Monitoring interval in seconds",
    )
    run_parser.add_argument(
        "--enable-caching",
        action="store_true",
        default=True,
        help="Enable result caching",
    )
    run_parser.add_argument(
        "--storage-backend",
        choices=["sqlite", "redis", "mongodb"],
        default="sqlite",
        help="Storage backend to use",
    )
    run_parser.add_argument(
        "--storage-path", default="./data", help="Path for storage backend"
    )
    run_parser.add_argument("--output-file", help="Save results to file")
    run_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    # LLM configuration
    run_parser.add_argument("--openai-api-key", help="OpenAI API key")
    run_parser.add_argument(
        "--openai-model", default="gpt-4", help="OpenAI model to use"
    )
    run_parser.add_argument("--anthropic-api-key", help="Anthropic API key")
    run_parser.add_argument(
        "--anthropic-model",
        default="claude-3-sonnet-20240229",
        help="Anthropic model to use",
    )
    run_parser.add_argument("--google-api-key", help="Google API key")
    run_parser.add_argument(
        "--google-model", default="gemini-pro", help="Google model to use"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List existing sessions")
    list_parser.add_argument(
        "--limit", type=int, default=20, help="Maximum number of sessions to show"
    )
    list_parser.add_argument(
        "--storage-backend",
        choices=["sqlite", "redis", "mongodb"],
        default="sqlite",
        help="Storage backend to use",
    )
    list_parser.add_argument(
        "--storage-path", default="./data", help="Path for storage backend"
    )

    # Show command
    show_parser = subparsers.add_parser("show", help="Show session details")
    show_parser.add_argument("session_id", help="Session ID to show")
    show_parser.add_argument(
        "--storage-backend",
        choices=["sqlite", "redis", "mongodb"],
        default="sqlite",
        help="Storage backend to use",
    )
    show_parser.add_argument(
        "--storage-path", default="./data", help="Path for storage backend"
    )

    return parser


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "run":
        return await run_reverse_prompting(args)
    elif args.command == "list":
        return await list_sessions(args)
    elif args.command == "show":
        return await show_session(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


def cli_main():
    """Synchronous entry point for setuptools."""
    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(cli_main())
