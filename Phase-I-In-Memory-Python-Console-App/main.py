#!/usr/bin/env python3
"""Entry point for TodoFlow CLI application."""

import sys
import argparse

from todo_app.cli import main as cli_main
from todo_app.interactive_cli import main as interactive_main
from todo_app.clean_cli import main as clean_main

def main_entry() -> int:
    """Main entry point with options for different modes."""
    parser = argparse.ArgumentParser(description="TodoFlow application")
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode with arrow key navigation')
    parser.add_argument('--clean', '-c', action='store_true',
                       help='Run in clean CLI mode with numbered menu')
    parser.add_argument('--cli', '-x', action='store_true',
                       help='Run in original CLI mode with commands')

    # Parse arguments
    args, remaining = parser.parse_known_args()

    if args.interactive:
        return interactive_main()
    elif args.clean:
        return clean_main()
    elif args.cli:
        # Pass remaining args to the original CLI
        import sys
        # Temporarily modify sys.argv to exclude the --interactive flag
        original_argv = sys.argv[:]
        sys.argv = [sys.argv[0]] + remaining
        result = cli_main()
        # Restore original argv
        sys.argv = original_argv
        return result
    else:
        # Default to clean CLI mode
        return clean_main()

if __name__ == "__main__":
    sys.exit(main_entry())
