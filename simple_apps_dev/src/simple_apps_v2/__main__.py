"""
Main entry point for Simple Apps v2 when run as a module.

Usage:
    python -m simple_apps_v2 [command] [options]
"""

import sys

from simple_apps_v2.cli import main

if __name__ == "__main__":
    sys.exit(main())