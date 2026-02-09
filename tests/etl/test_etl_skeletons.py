"""Tests for ETL skeleton classes (etl_api, etl_rds, etl_s3)."""
import pytest
import pandas as pd
from backend.etl.etl_api import ApiETL
from backend.etl.etl_rds import RdsETL
from backend.etl.etl_s3 import S3RawETL


@pytest.mark.parametrize("etl_cls, expected_msg", [
    (ApiETL, "API ETL not implemented - skeleton only"),
    (RdsETL, "RDS ETL not implemented - skeleton only"),
    (S3RawETL, "S3 Raw ETL not implemented - skeleton only"),
])
def test_etl_extract_raises_not_implemented(etl_cls, expected_msg):
    """Test: ETL.extract() raises NotImplementedError."""
    # Given: ETL instance
    etl = etl_cls()

    # When/Then: extract() raises NotImplementedError
    with pytest.raises(NotImplementedError, match=expected_msg):
        etl.extract()


@pytest.mark.parametrize("etl_cls", [ApiETL, RdsETL, S3RawETL])
def test_etl_transform_passes_through(etl_cls):
    """Test: ETL.transform() passes DataFrame through."""
    # Given: ETL instance and DataFrame
    etl = etl_cls()
    df = pd.DataFrame({"col1": [1, 2, 3]})

    # When: Transforming
    result = etl.transform(df)

    # Then: DataFrame is returned unchanged
    pd.testing.assert_frame_equal(result, df)
