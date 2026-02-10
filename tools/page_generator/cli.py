"""Command-line interface for page generator."""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .parser import load_page_spec
from .generators import (
    generate_constants,
    generate_layout,
    generate_filters,
    generate_data_loader,
    generate_custom_logic,
    generate_callbacks,
    generate_chart_builders,
)

FILE_GENERATORS = {
    'constants': ('_constants.py', generate_constants),
    'layout': ('_layout.py', generate_layout),
    'filters': ('_filters.py', generate_filters),
    'data_loader': ('_data_loader.py', generate_data_loader),
    'custom_logic': ('_custom_logic.py', generate_custom_logic),
    'callbacks': ('_callbacks.py', generate_callbacks),
    'chart_builders': ('_chart_builders.py', generate_chart_builders),
}

ALL_FILE_TYPES = list(FILE_GENERATORS.keys())


def generate_file(page_dir: Path, file_type: str, dry_run: bool = False) -> bool:
    """Generate a single file.

    Args:
        page_dir: Path to page directory
        file_type: Type of file to generate
        dry_run: If True, print to console instead of writing to file

    Returns:
        True if successful, False otherwise
    """
    spec_path = page_dir / "page_spec.yaml"

    try:
        spec = load_page_spec(spec_path)
    except Exception as e:
        print(f"Error loading {spec_path}: {e}", file=sys.stderr)
        return False

    try:
        filename, generator_func = FILE_GENERATORS[file_type]
        code = generator_func(spec)
        output_path = page_dir / filename

        if dry_run:
            print(f"\n{'='*60}\n{output_path}\n{'='*60}")
            print(code)
        else:
            output_path.write_text(code, encoding='utf-8')
            print(f"Generated: {output_path}")

        return True

    except Exception as e:
        print(f"Error generating {file_type}: {e}", file=sys.stderr)
        return False


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Optional command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description='Generate dashboard page from page_spec.yaml',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all files
  python3 -m tools.page_generator src/pages/hamm_overview

  # Generate specific files
  python3 -m tools.page_generator src/pages/hamm_overview --files constants layout

  # Dry run (print to console)
  python3 -m tools.page_generator src/pages/hamm_overview --dry-run

  # Generate only custom_logic skeleton
  python3 -m tools.page_generator src/pages/my_new_page --files custom_logic
        """,
    )

    parser.add_argument(
        'page_dir',
        help='Path to page directory (e.g., src/pages/hamm_overview)',
    )

    parser.add_argument(
        '--files',
        nargs='+',
        choices=ALL_FILE_TYPES + ['all'],
        default=['all'],
        help='Files to generate (default: all)',
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print generated code without writing files',
    )

    args = parser.parse_args(argv)

    page_dir = Path(args.page_dir)
    spec_path = page_dir / "page_spec.yaml"

    if not page_dir.exists():
        print(f"Error: Directory not found: {page_dir}", file=sys.stderr)
        return 1

    if not spec_path.exists():
        print(f"Error: {spec_path} not found", file=sys.stderr)
        return 1

    # Determine which files to generate
    files_to_generate = ALL_FILE_TYPES if 'all' in args.files else args.files

    # Generate files
    success_count = 0
    for file_type in files_to_generate:
        if generate_file(page_dir, file_type, dry_run=args.dry_run):
            success_count += 1

    # Print summary
    if args.dry_run:
        print(f"\nDry run completed. Would generate {success_count}/{len(files_to_generate)} file(s).")
    else:
        print(f"\nSuccess! Generated {success_count}/{len(files_to_generate)} file(s) from {spec_path}")

    return 0 if success_count == len(files_to_generate) else 1


if __name__ == "__main__":
    sys.exit(main())
