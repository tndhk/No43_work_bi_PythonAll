"""Generic DOMO DataSet ETL loader.

This script loads DOMO DataSets based on configuration in domo_datasets.yaml.

Usage:
    # List all configured datasets
    python backend/scripts/load_domo.py --list

    # Load specific dataset
    python backend/scripts/load_domo.py --dataset "APAC DOT Due Date"

    # Load all enabled datasets
    python backend/scripts/load_domo.py --all

    # Dry run (show what would be executed)
    python backend/scripts/load_domo.py --all --dry-run
"""
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env file
from dotenv import load_dotenv

load_dotenv(project_root / ".env")

import yaml
from backend.etl.etl_domo import DomoApiETL


def load_config() -> List[Dict]:
    """Load DOMO datasets configuration from YAML.

    Returns:
        List of dataset configurations
    """
    config_path = project_root / "backend" / "config" / "domo_datasets.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please create backend/config/domo_datasets.yaml"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    datasets = config.get("datasets", [])

    if not datasets:
        raise ValueError("No datasets configured in domo_datasets.yaml")

    return datasets


def list_datasets(datasets: List[Dict]) -> None:
    """Display all configured datasets.

    Args:
        datasets: List of dataset configurations
    """
    print("=== Configured DOMO DataSets ===")
    print()

    enabled_count = sum(1 for ds in datasets if ds.get("enabled", False))
    disabled_count = len(datasets) - enabled_count

    print(f"Total: {len(datasets)} datasets")
    print(f"Enabled: {enabled_count}")
    print(f"Disabled: {disabled_count}")
    print()

    for idx, ds in enumerate(datasets, 1):
        status = "✓" if ds.get("enabled", False) else "✗"
        partition = ds.get("partition_column") or "None"

        print(f"{idx}. [{status}] {ds['name']}")
        print(f"   DOMO ID: {ds['domo_dataset_id']}")
        print(f"   MinIO ID: {ds['minio_dataset_id']}")
        print(f"   Partition: {partition}")
        if ds.get("description"):
            print(f"   Description: {ds['description']}")
        print()


def load_dataset(config: Dict, dry_run: bool = False) -> bool:
    """Load a single DOMO dataset.

    Args:
        config: Dataset configuration
        dry_run: If True, only show what would be done

    Returns:
        True if successful, False otherwise
    """
    name = config["name"]
    domo_dataset_id = config["domo_dataset_id"]
    minio_dataset_id = config["minio_dataset_id"]
    partition_column = config.get("partition_column")
    exclude_filter = config.get("exclude_filter")

    print(f"\n{'='*60}")
    print(f"DataSet: {name}")
    print(f"{'='*60}")
    print(f"DOMO Dataset ID: {domo_dataset_id}")
    print(f"MinIO Dataset ID: {minio_dataset_id}")
    print(f"Partition Column: {partition_column or 'None'}")
    
    # 除外フィルター情報を表示
    if exclude_filter:
        print(f"Exclude Filter: {exclude_filter['column']} == '{exclude_filter['keep_value']}'")
    
    print()

    if dry_run:
        print("[DRY RUN] Would execute ETL pipeline")
        return True

    try:
        # Create ETL instance
        etl = DomoApiETL(
            dataset_id=domo_dataset_id,
            partition_column=partition_column,
            exclude_filter=exclude_filter,
        )

        # Run ETL pipeline
        print("Starting ETL pipeline...")
        etl.run(minio_dataset_id)

        print(f"\n✓ Successfully loaded '{name}' to MinIO")
        return True

    except Exception as e:
        print(f"\n✗ Error loading '{name}': {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Load DOMO DataSets to MinIO based on configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all configured datasets
  python backend/scripts/load_domo.py --list

  # Load specific dataset
  python backend/scripts/load_domo.py --dataset "APAC DOT Due Date"

  # Load all enabled datasets
  python backend/scripts/load_domo.py --all

  # Dry run
  python backend/scripts/load_domo.py --all --dry-run
        """,
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all configured datasets and exit",
    )

    parser.add_argument(
        "--dataset",
        type=str,
        help="Load specific dataset by name",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Load all enabled datasets",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        datasets = load_config()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # List datasets
    if args.list:
        list_datasets(datasets)
        sys.exit(0)

    # Validate arguments
    if not args.dataset and not args.all:
        parser.print_help()
        print("\nError: Must specify --dataset or --all")
        sys.exit(1)

    # Filter datasets
    if args.dataset:
        # Load specific dataset
        target_datasets = [ds for ds in datasets if ds["name"] == args.dataset]

        if not target_datasets:
            print(f"Error: Dataset '{args.dataset}' not found in configuration")
            print("\nAvailable datasets:")
            for ds in datasets:
                print(f"  - {ds['name']}")
            sys.exit(1)

    elif args.all:
        # Load all enabled datasets
        target_datasets = [ds for ds in datasets if ds.get("enabled", False)]

        if not target_datasets:
            print("Error: No enabled datasets found in configuration")
            sys.exit(1)

    # Execute ETL
    print("=== DOMO to MinIO ETL ===")
    print(f"Target: {len(target_datasets)} dataset(s)")
    if args.dry_run:
        print("Mode: DRY RUN")
    print()

    success_count = 0
    failure_count = 0

    for config in target_datasets:
        success = load_dataset(config, dry_run=args.dry_run)
        if success:
            success_count += 1
        else:
            failure_count += 1

    # Summary
    print(f"\n{'='*60}")
    print("=== ETL Summary ===")
    print(f"{'='*60}")
    print(f"Total: {len(target_datasets)} datasets")
    print(f"Success: {success_count}")
    print(f"Failure: {failure_count}")
    print()

    if failure_count > 0:
        print("Some datasets failed to load. Check logs above for details.")
        sys.exit(1)
    else:
        print("All datasets loaded successfully!")
        print()
        print("Next steps:")
        print("  1. Verify data in MinIO console: http://localhost:9001")
        print("  2. Test with ParquetReader:")
        print()
        print("     from src.data.parquet_reader import ParquetReader")
        print("     from src.core.cache import get_cached_dataset")
        print("     reader = ParquetReader()")
        for ds in target_datasets:
            print(f"     df = get_cached_dataset(reader, '{ds['minio_dataset_id']}')")


if __name__ == "__main__":
    main()
