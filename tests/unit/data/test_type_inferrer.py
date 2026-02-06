"""Tests for type inferrer."""
import pytest
import pandas as pd
from src.data.type_inferrer import infer_column_type, infer_schema, apply_types
from src.data.models import ColumnSchema


def test_infer_column_type_integer():
    """Test: Integer type inference."""
    # Given: Series with integers
    series = pd.Series([1, 2, 3, 4, 5])

    # When: Inferring type
    dtype = infer_column_type(series)

    # Then: int64 is inferred
    assert dtype == "int64"


def test_infer_column_type_float():
    """Test: Float type inference."""
    # Given: Series with floats
    series = pd.Series([1.0, 2.5, 3.7])

    # When: Inferring type
    dtype = infer_column_type(series)

    # Then: float64 is inferred
    assert dtype == "float64"


def test_infer_column_type_bool():
    """Test: Boolean type inference."""
    # Given: Series with boolean-like values
    series = pd.Series(["true", "false", "1", "0"])

    # When: Inferring type
    dtype = infer_column_type(series)

    # Then: bool is inferred
    assert dtype == "bool"


def test_infer_column_type_date():
    """Test: Date type inference."""
    # Given: Series with dates
    series = pd.Series(["2024-01-01", "2024-01-02", "2024-01-03"])

    # When: Inferring type
    dtype = infer_column_type(series)

    # Then: date is inferred
    assert dtype == "date"


def test_infer_column_type_string():
    """Test: String type inference."""
    # Given: Series with strings
    series = pd.Series(["Alice", "Bob", "Charlie"])

    # When: Inferring type
    dtype = infer_column_type(series)

    # Then: string is inferred
    assert dtype == "string"


def test_infer_schema():
    """Test: Schema inference for DataFrame."""
    # Given: DataFrame with mixed types
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "amount": [100.0, 200.0, 300.0],
    })

    # When: Inferring schema
    schema = infer_schema(df)

    # Then: Schema is inferred for all columns
    assert len(schema) == 3
    assert schema[0].name == "id"
    assert schema[1].name == "name"
    assert schema[2].name == "amount"


def test_apply_types():
    """Test: Type application to DataFrame."""
    # Given: DataFrame and schema
    df = pd.DataFrame({
        "id": ["1", "2", "3"],
        "amount": ["100.0", "200.0", "300.0"],
    })
    schema = [
        ColumnSchema(name="id", data_type="int64"),
        ColumnSchema(name="amount", data_type="float64"),
    ]

    # When: Applying types
    result = apply_types(df, schema)

    # Then: Types are applied
    assert pd.api.types.is_integer_dtype(result["id"])
    assert pd.api.types.is_float_dtype(result["amount"])
