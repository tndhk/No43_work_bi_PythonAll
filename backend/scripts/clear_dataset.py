"""Clear dataset from MinIO/S3.

This script deletes all objects for a given dataset from MinIO/S3.
Useful when you need to re-upload data with different filters or schema.

Usage:
    python backend/scripts/clear_dataset.py apac-dot-due-date
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env file
from dotenv import load_dotenv

load_dotenv(project_root / ".env")

from src.data.s3_client import get_s3_client
from src.data.config import settings


def clear_dataset(dataset_id: str) -> None:
    """Delete all objects for a dataset.
    
    Args:
        dataset_id: Dataset ID in MinIO (e.g., "apac-dot-due-date")
    """
    client = get_s3_client()
    bucket = settings.s3_bucket
    prefix = f"datasets/{dataset_id}/"
    
    print(f"Clearing dataset: {dataset_id}")
    print(f"Bucket: {bucket}")
    print(f"Prefix: {prefix}")
    print()
    
    # List all objects
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
    deleted_count = 0
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                client.delete_object(Bucket=bucket, Key=obj['Key'])
                deleted_count += 1
                print(f"Deleted: {obj['Key']}")
    
    if deleted_count == 0:
        print(f"⚠ No objects found for dataset '{dataset_id}'")
    else:
        print(f"\n✓ Deleted {deleted_count} objects for dataset '{dataset_id}'")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python backend/scripts/clear_dataset.py <dataset_id>")
        print("\nExample:")
        print("  python backend/scripts/clear_dataset.py apac-dot-due-date")
        sys.exit(1)
    
    dataset_id = sys.argv[1]
    
    try:
        clear_dataset(dataset_id)
    except Exception as e:
        print(f"\n✗ Error clearing dataset: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
