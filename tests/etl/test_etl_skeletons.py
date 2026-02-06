"""Tests for ETL skeleton classes (etl_api, etl_rds, etl_s3)."""
import pytest
import pandas as pd
from backend.etl.etl_api import ApiETL
from backend.etl.etl_rds import RdsETL
from backend.etl.etl_s3 import S3RawETL


def test_api_etl_extract_raises_not_implemented():
    """Test: ApiETL.extract() raises NotImplementedError."""
    # Given: ApiETL instance
    etl = ApiETL()
    
    # When/Then: extract() raises NotImplementedError
    with pytest.raises(NotImplementedError, match="API ETL not implemented in Phase 1"):
        etl.extract()


def test_api_etl_transform_passes_through():
    """Test: ApiETL.transform() passes DataFrame through."""
    # Given: ApiETL instance and DataFrame
    etl = ApiETL()
    df = pd.DataFrame({"col1": [1, 2, 3]})
    
    # When: Transforming
    result = etl.transform(df)
    
    # Then: DataFrame is returned unchanged
    pd.testing.assert_frame_equal(result, df)


def test_rds_etl_extract_raises_not_implemented():
    """Test: RdsETL.extract() raises NotImplementedError."""
    # Given: RdsETL instance
    etl = RdsETL()
    
    # When/Then: extract() raises NotImplementedError
    with pytest.raises(NotImplementedError, match="RDS ETL not implemented in Phase 1"):
        etl.extract()


def test_rds_etl_transform_passes_through():
    """Test: RdsETL.transform() passes DataFrame through."""
    # Given: RdsETL instance and DataFrame
    etl = RdsETL()
    df = pd.DataFrame({"col1": [1, 2, 3]})
    
    # When: Transforming
    result = etl.transform(df)
    
    # Then: DataFrame is returned unchanged
    pd.testing.assert_frame_equal(result, df)


def test_s3_raw_etl_extract_raises_not_implemented():
    """Test: S3RawETL.extract() raises NotImplementedError."""
    # Given: S3RawETL instance
    etl = S3RawETL()
    
    # When/Then: extract() raises NotImplementedError
    with pytest.raises(NotImplementedError, match="S3 Raw ETL not implemented in Phase 1"):
        etl.extract()


def test_s3_raw_etl_transform_passes_through():
    """Test: S3RawETL.transform() passes DataFrame through."""
    # Given: S3RawETL instance and DataFrame
    etl = S3RawETL()
    df = pd.DataFrame({"col1": [1, 2, 3]})
    
    # When: Transforming
    result = etl.transform(df)
    
    # Then: DataFrame is returned unchanged
    pd.testing.assert_frame_equal(result, df)
