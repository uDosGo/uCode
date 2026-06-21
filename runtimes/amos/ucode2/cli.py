"""
uCode2 CLI — ProseUI Markdown Learning Environment

uCode2 is a thin shim that provides the ProseUI surface.
Canonical source: https://github.com/uDosGo/uConnect

Usage:
  ucode2 [OPTIONS]
  ucode2 render <file>     # Render a markdown file
  ucode2 --help            # Show help
  ucode2 --version         # Show version
"""

import sys
import argparse


def _render_markdown(filepath: str) -> None:
    """Render a markdown file using the prose renderer."""
    try:
        from ucode2.prose.renderer import render_markdown
        with open(filepath, 'r') as f:
            source = f.read()
        result = render_markdown(source)
        print(result)
    except ImportError:
        print("Error: prose renderer not available")
        print("Install uCode2 with: pip install ucode2")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='uCode2 - ProseUI: Beautiful GFM markdown learning environment',
    )
    parser.add_argument('command', nargs='?', choices=['render'],
                       help='Command to execute')
    parser.add_argument('file', nargs='?',
                       help='File to process')
    parser.add_argument('--version', action='version',
                       version='uCode2 1.0.0',
                       help='Show version')
    
    args = parser.parse_args()
    
    if args.command == 'render' and args.file:
        _render_markdown(args.file)
    else:
        print("uCode2 v1.0.0 — ProseUI Markdown Learning Environment")
        print()
        print("Canonical source: https://github.com/uDosGo/uConnect")
        print()
        print("Usage:")
        print("  ucode2 render <file>    Render a markdown file")
        print("  ucode2 --help           Show help")
        print("  ucode2 --version        Show version")
        print()
        print("To launch the full ProseUI surface, run the UI Hub from uConnect:")
        print("  cd /path/to/uConnect && npm run dev")


if __name__ == '__main__':
    main()
