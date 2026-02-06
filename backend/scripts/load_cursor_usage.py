"""ETL script to load Cursor usage CSV data to MinIO S3 as Parquet."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.etl.etl_csv import CsvETL


def main():
    """Load Cursor usage CSV to S3."""
    csv_path = project_root / "backend" / "data_sources" / "team-usage-events-15944373-2026-01-28.csv"
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    print(f"Loading CSV from: {csv_path}")
    
    # Create ETL instance
    etl = CsvETL(
        csv_path=str(csv_path),
        partition_column="Date",  # Partition by date
    )
    
    # Run ETL
    dataset_id = "cursor-usage"
    print(f"Running ETL for dataset: {dataset_id}")
    etl.run(dataset_id)
    
    print(f"Successfully loaded dataset '{dataset_id}' to S3")


if __name__ == "__main__":
    main()
