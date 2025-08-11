"""
Main entry point for the reverse prompting package when run as a module.

This allows users to run the CLI with: python -m reverse_prompting
"""

from .cli import cli_main

if __name__ == "__main__":
    exit(cli_main())
