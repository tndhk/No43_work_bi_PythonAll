"""CSV to Parquet ETL."""
from typing import Optional
import pandas as pd
from src.data.csv_parser import parse_full, CsvImportOptions
from src.data.type_inferrer import infer_schema, apply_types
from backend.etl.base_etl import BaseETL


class CsvETL(BaseETL):
    """ETL for converting CSV files to Parquet.

    Processing flow:
    1. extract: Read CSV file (using csv_parser)
    2. transform: Type inference + type application (using type_inferrer)
    3. load: Convert to Parquet and upload to S3 (using BaseETL.load)
    """

    def __init__(
        self,
        csv_path: str,
        partition_column: Optional[str] = None,
        csv_options: Optional[CsvImportOptions] = None,
    ):
        """
        Args:
            csv_path: Path to CSV file
            partition_column: Date column name for partitioning
            csv_options: CSV import options
        """
        self.csv_path = csv_path
        self.partition_column = partition_column
        self.csv_options = csv_options or CsvImportOptions()

    def extract(self) -> pd.DataFrame:
        """Extract data from CSV file."""
        with open(self.csv_path, "rb") as f:
            file_bytes = f.read()
        return parse_full(file_bytes, self.csv_options)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data: infer types and apply them."""
        schema = infer_schema(df)
        return apply_types(df, schema)

    def load(
        self,
        df: pd.DataFrame,
        dataset_id: str,
        partition_column: Optional[str] = None,
    ) -> None:
        """Load data to S3, using partition_column from constructor if not provided."""
        partition_col = partition_column or self.partition_column
        super().load(df, dataset_id, partition_col)
