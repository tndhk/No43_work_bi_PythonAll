"""Generic CSV file ETL loader.

This script loads CSV files to MinIO/S3 based on configuration in csv_datasets.yaml.

Usage:
    # List all configured datasets
    python backend/scripts/load_csv.py --list

    # Load specific dataset
    python backend/scripts/load_csv.py --dataset "Dataset Name"

    # Load all enabled datasets
    python backend/scripts/load_csv.py --all

    # Dry run (show what would be executed)
    python backend/scripts/load_csv.py --all --dry-run
"""
import sys
import argparse
from pathlib import Path
from typing import List, Dict

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml

from backend.etl.etl_csv import CsvETL
from backend.etl.resolve_csv_path import resolve_csv_path


def load_config(config_path: Path) -> dict:
    """Load CSV datasets configuration from YAML.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        The full configuration dict containing a 'datasets' list.

    Raises:
        FileNotFoundError: If config_path does not exist.
        ValueError: If the datasets list is empty.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    datasets = config.get("datasets", [])
    if not datasets:
        raise ValueError("No datasets configured in configuration file")

    return config


def load_dataset(dataset_config: dict, dry_run: bool = False) -> bool:
    """Load a single CSV dataset through the ETL pipeline.

    Args:
        dataset_config: Dataset configuration dict.
        dry_run: If True, only show what would be done.

    Returns:
        True if successful, False otherwise.
    """
    name = dataset_config["name"]
    minio_dataset_id = dataset_config["minio_dataset_id"]
    source_dir = dataset_config["source_dir"]
    file_pattern = dataset_config["file_pattern"]
    partition_column = dataset_config.get("partition_column")
    csv_options = dataset_config.get("csv_options")

    print(f"\n{'=' * 60}")
    print(f"DataSet: {name}")
    print(f"{'=' * 60}")
    print(f"Source: {source_dir}/{file_pattern}")
    print(f"MinIO ID: {minio_dataset_id}")
    print(f"Partition Column: {partition_column or 'None'}")
    print()

    if dry_run:
        print("[DRY RUN] Would execute ETL pipeline")
        return True

    try:
        csv_path = resolve_csv_path(source_dir, file_pattern)

        etl_kwargs = {
            "partition_column": partition_column,
        }
        if csv_options is not None:
            etl_kwargs["csv_options"] = csv_options

        etl = CsvETL(str(csv_path), **etl_kwargs)
        etl.run(minio_dataset_id)

        print(f"Successfully loaded '{name}' to MinIO")
        return True

    except Exception as e:
        print(f"Error loading '{name}': {e}")
        return False


def list_datasets(datasets: List[Dict]) -> None:
    """Display all configured datasets.

    Args:
        datasets: List of dataset configurations.
    """
    print("=== Configured CSV DataSets ===")
    print()

    enabled_count = sum(1 for ds in datasets if ds.get("enabled", False))
    disabled_count = len(datasets) - enabled_count

    print(f"Total: {len(datasets)} datasets")
    print(f"Enabled: {enabled_count}")
    print(f"Disabled: {disabled_count}")
    print()

    for idx, ds in enumerate(datasets, 1):
        status = "+" if ds.get("enabled", False) else "-"
        partition = ds.get("partition_column") or "None"

        print(f"{idx}. [{status}] {ds['name']}")
        print(f"   Source: {ds.get('source_dir', '')}/{ds.get('file_pattern', '')}")
        print(f"   MinIO ID: {ds['minio_dataset_id']}")
        print(f"   Partition: {partition}")
        if ds.get("description"):
            print(f"   Description: {ds['description']}")
        print()


def main(argv: list = None):
    """Main entry point.

    Args:
        argv: Command-line arguments (for testability). If None, uses sys.argv.
    """
    parser = argparse.ArgumentParser(
        description="Load CSV files to MinIO based on configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config file",
    )

    args = parser.parse_args(argv)

    # Determine config path
    if args.config:
        config_path = Path(args.config)
    else:
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "backend" / "config" / "csv_datasets.yaml"

    # Load configuration
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    datasets = config["datasets"]

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
        target_datasets = [ds for ds in datasets if ds["name"] == args.dataset]
        if not target_datasets:
            print(f"Error: Dataset '{args.dataset}' not found in configuration")
            print("\nAvailable datasets:")
            for ds in datasets:
                print(f"  - {ds['name']}")
            sys.exit(1)
    elif args.all:
        target_datasets = [ds for ds in datasets if ds.get("enabled", False)]
        if not target_datasets:
            print("Error: No enabled datasets found in configuration")
            sys.exit(1)

    # Execute ETL
    print("=== CSV to MinIO ETL ===")
    print(f"Target: {len(target_datasets)} dataset(s)")
    if args.dry_run:
        print("Mode: DRY RUN")
    print()

    success_count = 0
    failure_count = 0

    for ds_config in target_datasets:
        success = load_dataset(ds_config, args.dry_run)
        if success:
            success_count += 1
        else:
            failure_count += 1

    # Summary
    print(f"\n{'=' * 60}")
    print("=== ETL Summary ===")
    print(f"{'=' * 60}")
    print(f"Total: {len(target_datasets)} datasets")
    print(f"Success: {success_count}")
    print(f"Failure: {failure_count}")

    if failure_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
