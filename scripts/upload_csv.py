#!/usr/bin/env python3
"""CSV upload CLI tool.

Usage:
    python scripts/upload_csv.py <csv_file> --dataset-id <id> [--partition-col <col>]

Arguments:
    csv_file          CSV file path
    --dataset-id      Dataset ID (S3 key)
    --partition-col   Date column name for partitioning (optional, single file if omitted)
"""
import argparse
import sys
from pathlib import Path
from backend.etl.etl_csv import CsvETL


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Upload CSV file to S3 as Parquet dataset"
    )
    parser.add_argument(
        "csv_file",
        type=str,
        help="Path to CSV file",
    )
    parser.add_argument(
        "--dataset-id",
        type=str,
        required=True,
        help="Dataset ID (S3 key)",
    )
    parser.add_argument(
        "--partition-col",
        type=str,
        default=None,
        help="Date column name for partitioning",
    )

    args = parser.parse_args()

    # Validate CSV file exists
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {args.csv_file}", file=sys.stderr)
        sys.exit(1)

    # Run ETL
    try:
        etl = CsvETL(str(csv_path), partition_column=args.partition_col)
        etl.run(args.dataset_id)
        print(f"Successfully uploaded {args.csv_file} as dataset: {args.dataset_id}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
