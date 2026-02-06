"""DOMO API to Parquet ETL."""
import os
import requests
import pandas as pd
from typing import Optional
from backend.etl.base_etl import BaseETL
from src.data.type_inferrer import infer_schema, apply_types


class DomoApiETL(BaseETL):
    """ETL for converting DOMO DataSet to Parquet.
    
    DOMO API Documentation: https://developer.domo.com/portal/3b1e3a7d5f420-data-set-api
    
    Args:
        dataset_id: DOMO DataSet ID (UUID format)
        client_id: DOMO API Client ID (from .env)
        client_secret: DOMO API Client Secret (from .env)
        partition_column: Optional date column name for partitioning
    """

    def __init__(
        self,
        dataset_id: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        partition_column: Optional[str] = None,
        exclude_filter: Optional[dict] = None,
    ):
        self.dataset_id = dataset_id
        # Strip quotes if present (for .env files with quoted values)
        self.client_id = (client_id or os.getenv("DOMO_CLIENT_ID") or "").strip('"')
        self.client_secret = (
            client_secret or os.getenv("DOMO_CLIENT_SECRET") or ""
        ).strip('"')
        self.partition_column = partition_column
        self.exclude_filter = exclude_filter
        self.access_token: Optional[str] = None

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "DOMO_CLIENT_ID and DOMO_CLIENT_SECRET must be set in .env"
            )

    def _get_access_token(self) -> str:
        """Get OAuth2 access token from DOMO API.
        
        Returns:
            Access token (valid for 3600 seconds)
        """
        if self.access_token:
            return self.access_token

        url = "https://api.domo.com/oauth/token"
        params = {
            "grant_type": "client_credentials",
            "scope": "data",
        }

        response = requests.post(
            url,
            params=params,
            auth=(self.client_id, self.client_secret),
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = data["access_token"]
        print(f"✓ Access token acquired (expires in {data['expires_in']}s)")
        return self.access_token

    def get_dataset_info(self) -> dict:
        """Get DataSet metadata from DOMO API.
        
        Returns:
            DataSet metadata (name, rows, columns, schema)
        """
        token = self._get_access_token()
        url = f"https://api.domo.com/v1/datasets/{self.dataset_id}"
        params = {"fields": "all"}

        response = requests.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def extract(self) -> pd.DataFrame:
        """Extract data from DOMO DataSet API.
        
        Returns:
            Raw DataFrame from DOMO DataSet
        """
        # Get DataSet info
        info = self.get_dataset_info()
        print(f"DataSet: {info['name']}")
        print(f"Rows: {info.get('rows', 'unknown')}")
        print(f"Columns: {info.get('columns', 'unknown')}")

        # Export data as CSV
        token = self._get_access_token()
        url = f"https://api.domo.com/v1/datasets/{self.dataset_id}/data"
        params = {"includeHeader": "true"}

        print("Downloading data from DOMO...")
        response = requests.get(
            url,
            params=params,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "text/csv",
            },
            timeout=300,  # 5 minutes for large datasets
        )
        response.raise_for_status()

        # Parse CSV
        from io import StringIO

        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)

        print(f"✓ Downloaded {len(df)} rows, {len(df.columns)} columns")
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data with type inference and optional filtering.
        
        Args:
            df: Raw DataFrame from DOMO
            
        Returns:
            Transformed DataFrame with proper types
        """
        print("Inferring data types...")
        schema = infer_schema(df)
        df = apply_types(df, schema)

        # 除外フィルター処理
        if self.exclude_filter:
            column = self.exclude_filter.get("column")
            keep_value = self.exclude_filter.get("keep_value")
            
            if column and keep_value and column in df.columns:
                original_count = len(df)
                df = df[df[column] == keep_value].copy()
                filtered_count = len(df)
                excluded_count = original_count - filtered_count
                
                print(f"✓ Applied exclude filter:")
                print(f"  Column: {column}")
                print(f"  Keep value: {keep_value}")
                print(f"  Original rows: {original_count:,}")
                print(f"  Filtered rows: {filtered_count:,}")
                print(f"  Excluded rows: {excluded_count:,}")
            else:
                print(f"⚠ Exclude filter skipped (column '{column}' not found or invalid config)")

        print("✓ Data transformation complete")
        print(f"  Final shape: {df.shape}")

        return df

    def run(self, dataset_id: str) -> None:
        """Execute ETL pipeline: extract -> transform -> load.
        
        Args:
            dataset_id: Target dataset ID in MinIO (not DOMO dataset_id)
        """
        df = self.extract()
        df = self.transform(df)
        self.load(df, dataset_id, partition_column=self.partition_column)
        print(f"✓ Successfully loaded dataset '{dataset_id}' to S3")
