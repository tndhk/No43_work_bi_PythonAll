"""Tests for data transformation operations."""
import pytest
import pandas as pd
from types import ModuleType
from tools.page_generator.operations import (
    apply_filter_operation,
    apply_groupby_operation,
    apply_pivot_operation,
    apply_compute_operation,
    apply_rename_operation,
    apply_sort_operation,
    apply_ensure_columns_operation,
    apply_custom_operation,
    execute_transform_pipeline,
)


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "region": ["AMER", "EMEA", "APAC", "AMER", "EMEA"],
        "status": ["Completed", "Cancelled", "Completed", "Invalid", "Completed"],
        "year": [2024, 2024, 2023, 2024, 2023],
        "id": ["1", "2", "3", "4", "5"],
        "duration": [100, 150, 200, 120, 180],
        "count": [1, 1, 1, 1, 1],
    })


@pytest.fixture
def pivot_df():
    """Create a DataFrame suitable for pivot testing."""
    return pd.DataFrame({
        "fiscal_year": ["2024", "2024", "2024", "2023", "2023"],
        "quarter": ["Q1", "Q1", "Q2", "Q1", "Q2"],
        "status": ["Completed", "Invalid", "Completed", "Completed", "Invalid"],
        "count": [10, 5, 15, 8, 3],
    })


@pytest.fixture
def date_df():
    """Create a DataFrame with date strings for sorting."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "start_date": ["15-Jan-24", "01-Feb-24", "20-Dec-23", "05-Jan-24"],
        "value": [100, 200, 300, 400],
    })


class TestFilterOperation:
    def test_filter_with_column_and_values(self, sample_df):
        """Test filter with explicit column and values."""
        op = {"column": "status", "values": ["Completed", "Invalid"]}
        result = apply_filter_operation(sample_df, op)
        assert len(result) == 4
        assert set(result["status"].unique()) == {"Completed", "Invalid"}

    def test_filter_with_exclude_pattern(self, sample_df):
        """Test filter with exclude pattern."""
        op = {"exclude_status": ["Cancelled"]}
        result = apply_filter_operation(sample_df, op)
        assert len(result) == 4
        assert "Cancelled" not in result["status"].values

    def test_filter_multiple_exclude(self, sample_df):
        """Test filter with multiple exclude patterns."""
        op = {"exclude_status": ["Cancelled", "Invalid"]}
        result = apply_filter_operation(sample_df, op)
        assert len(result) == 3
        assert set(result["status"].unique()) == {"Completed"}

    def test_filter_invalid_column(self, sample_df):
        """Test filter with non-existent column."""
        op = {"column": "nonexistent", "values": ["test"]}
        with pytest.raises(ValueError, match="Column 'nonexistent' not found"):
            apply_filter_operation(sample_df, op)

    def test_filter_missing_parameters(self, sample_df):
        """Test filter with missing required parameters."""
        op = {}
        with pytest.raises(ValueError, match="requires either"):
            apply_filter_operation(sample_df, op)


class TestGroupbyOperation:
    def test_groupby_basic(self, sample_df):
        """Test basic groupby operation."""
        op = {
            "columns": ["region"],
            "agg": {"duration": "sum", "id": "count"}
        }
        result = apply_groupby_operation(sample_df, op)
        assert len(result) == 3
        assert "region" in result.columns
        assert "duration" in result.columns
        assert "id" in result.columns

    def test_groupby_multiple_columns(self, sample_df):
        """Test groupby with multiple grouping columns."""
        op = {
            "columns": ["region", "year"],
            "agg": {"id": "nunique", "duration": "sum"}
        }
        result = apply_groupby_operation(sample_df, op)
        assert len(result) == 4  # AMER-2024, EMEA-2024, APAC-2023, EMEA-2023
        assert all(col in result.columns for col in ["region", "year", "id", "duration"])

    def test_groupby_invalid_column(self, sample_df):
        """Test groupby with non-existent column."""
        op = {
            "columns": ["nonexistent"],
            "agg": {"id": "count"}
        }
        with pytest.raises(ValueError, match="Groupby column 'nonexistent' not found"):
            apply_groupby_operation(sample_df, op)

    def test_groupby_invalid_agg_column(self, sample_df):
        """Test groupby with non-existent aggregation column."""
        op = {
            "columns": ["region"],
            "agg": {"nonexistent": "sum"}
        }
        with pytest.raises(ValueError, match="Aggregation column 'nonexistent' not found"):
            apply_groupby_operation(sample_df, op)

    def test_groupby_missing_keys(self, sample_df):
        """Test groupby with missing required keys."""
        op = {"columns": ["region"]}
        with pytest.raises(ValueError, match="requires 'columns' and 'agg' keys"):
            apply_groupby_operation(sample_df, op)


class TestPivotOperation:
    def test_pivot_basic(self, pivot_df):
        """Test basic pivot operation."""
        op = {
            "index": ["fiscal_year", "quarter"],
            "columns": "status",
            "values": "count",
            "fill_value": 0
        }
        result = apply_pivot_operation(pivot_df, op)
        assert "fiscal_year" in result.columns
        assert "quarter" in result.columns
        assert "Completed" in result.columns
        assert "Invalid" in result.columns

    def test_pivot_single_index(self, pivot_df):
        """Test pivot with single index column."""
        op = {
            "index": "fiscal_year",
            "columns": "status",
            "values": "count",
            "fill_value": 0
        }
        result = apply_pivot_operation(pivot_df, op)
        assert "fiscal_year" in result.columns
        assert len(result) == 2  # 2023, 2024

    def test_pivot_no_fill_value(self, pivot_df):
        """Test pivot without fill_value."""
        op = {
            "index": ["fiscal_year"],
            "columns": "status",
            "values": "count"
        }
        result = apply_pivot_operation(pivot_df, op)
        assert "Completed" in result.columns

    def test_pivot_invalid_column(self, pivot_df):
        """Test pivot with non-existent column."""
        op = {
            "index": ["nonexistent"],
            "columns": "status",
            "values": "count"
        }
        with pytest.raises(ValueError, match="Pivot index column 'nonexistent' not found"):
            apply_pivot_operation(pivot_df, op)


class TestComputeOperation:
    def test_compute_basic(self, sample_df):
        """Test basic compute operation."""
        op = {"name": "total", "expression": "duration + count"}
        result = apply_compute_operation(sample_df, op)
        assert "total" in result.columns
        assert result["total"].iloc[0] == 101

    def test_compute_complex_expression(self, sample_df):
        """Test compute with complex expression."""
        op = {"name": "score", "expression": "duration * 2 + count * 10"}
        result = apply_compute_operation(sample_df, op)
        assert "score" in result.columns
        assert result["score"].iloc[0] == 210  # 100*2 + 1*10

    def test_compute_invalid_expression(self, sample_df):
        """Test compute with invalid expression."""
        op = {"name": "bad", "expression": "nonexistent_col + 1"}
        with pytest.raises(ValueError, match="Failed to evaluate expression"):
            apply_compute_operation(sample_df, op)

    def test_compute_missing_keys(self, sample_df):
        """Test compute with missing required keys."""
        op = {"name": "total"}
        with pytest.raises(ValueError, match="requires 'name' and 'expression' keys"):
            apply_compute_operation(sample_df, op)


class TestRenameOperation:
    def test_rename_basic(self, sample_df):
        """Test basic rename operation."""
        op = {"mapping": {"region": "Region", "status": "Status"}}
        result = apply_rename_operation(sample_df, op)
        assert "Region" in result.columns
        assert "Status" in result.columns
        assert "region" not in result.columns
        assert "status" not in result.columns

    def test_rename_partial(self, sample_df):
        """Test rename with only some columns."""
        op = {"mapping": {"id": "Task ID"}}
        result = apply_rename_operation(sample_df, op)
        assert "Task ID" in result.columns
        assert "region" in result.columns  # unchanged

    def test_rename_missing_key(self, sample_df):
        """Test rename with missing mapping key."""
        op = {}
        with pytest.raises(ValueError, match="requires 'mapping' key"):
            apply_rename_operation(sample_df, op)


class TestSortOperation:
    def test_sort_basic(self, sample_df):
        """Test basic sort operation."""
        op = {"by": "duration", "ascending": True}
        result = apply_sort_operation(sample_df, op)
        assert result["duration"].iloc[0] == 100
        assert result["duration"].iloc[-1] == 200

    def test_sort_descending(self, sample_df):
        """Test sort in descending order."""
        op = {"by": "duration", "ascending": False}
        result = apply_sort_operation(sample_df, op)
        assert result["duration"].iloc[0] == 200
        assert result["duration"].iloc[-1] == 100

    def test_sort_numeric(self, sample_df):
        """Test sort with numeric conversion."""
        df = sample_df.copy()
        df["id"] = df["id"].astype(str)  # Make sure it's string
        op = {"by": "id", "numeric": True, "ascending": True}
        result = apply_sort_operation(df, op)
        assert result["id"].iloc[0] == "1"
        assert result["id"].iloc[-1] == "5"

    def test_sort_parse_date(self, date_df):
        """Test sort with date parsing."""
        op = {
            "parse_date": {
                "column": "start_date",
                "format": "%d-%b-%y",
                "output": "_sort_temp"
            },
            "ascending": True
        }
        result = apply_sort_operation(date_df, op)
        assert result["start_date"].iloc[0] == "20-Dec-23"
        assert result["start_date"].iloc[-1] == "01-Feb-24"
        assert "_sort_temp" in result.columns

    def test_sort_invalid_column(self, sample_df):
        """Test sort with non-existent column."""
        op = {"by": "nonexistent"}
        with pytest.raises(ValueError, match="Sort column 'nonexistent' not found"):
            apply_sort_operation(sample_df, op)

    def test_sort_missing_by(self, sample_df):
        """Test sort without 'by' or 'parse_date'."""
        op = {"ascending": True}
        with pytest.raises(ValueError, match="requires 'by' key or 'parse_date' configuration"):
            apply_sort_operation(sample_df, op)


class TestEnsureColumnsOperation:
    def test_ensure_columns_basic(self, sample_df):
        """Test ensure columns with default value."""
        op = {"columns": ["Completed", "Invalid"], "default_value": 0}
        result = apply_ensure_columns_operation(sample_df, op)
        assert "Completed" in result.columns
        assert "Invalid" in result.columns
        assert (result["Completed"] == 0).all()
        assert (result["Invalid"] == 0).all()

    def test_ensure_columns_existing(self, sample_df):
        """Test ensure columns doesn't overwrite existing."""
        op = {"columns": ["region", "new_col"], "default_value": 99}
        result = apply_ensure_columns_operation(sample_df, op)
        assert "new_col" in result.columns
        assert (result["new_col"] == 99).all()
        assert "AMER" in result["region"].values  # unchanged

    def test_ensure_columns_no_default(self, sample_df):
        """Test ensure columns with default 0."""
        op = {"columns": ["col1"]}
        result = apply_ensure_columns_operation(sample_df, op)
        assert "col1" in result.columns
        assert (result["col1"] == 0).all()

    def test_ensure_columns_missing_key(self, sample_df):
        """Test ensure columns with missing columns key."""
        op = {}
        with pytest.raises(ValueError, match="requires 'columns' key"):
            apply_ensure_columns_operation(sample_df, op)


class TestCustomOperation:
    def test_custom_basic(self, sample_df):
        """Test custom operation with mock module."""
        # Create a mock module with a custom function
        mock_module = ModuleType("mock_module")

        def add_prefix(df, prefix="test"):
            df = df.copy()
            df["prefixed_id"] = prefix + "_" + df["id"]
            return df

        mock_module.add_prefix = add_prefix

        op = {
            "function": "add_prefix",
            "args": {"prefix": "custom"}
        }
        result = apply_custom_operation(sample_df, op, mock_module)
        assert "prefixed_id" in result.columns
        assert result["prefixed_id"].iloc[0] == "custom_1"

    def test_custom_no_args(self, sample_df):
        """Test custom operation without args."""
        mock_module = ModuleType("mock_module")

        def simple_transform(df):
            df = df.copy()
            df["transformed"] = True
            return df

        mock_module.simple_transform = simple_transform

        op = {"function": "simple_transform"}
        result = apply_custom_operation(sample_df, op, mock_module)
        assert "transformed" in result.columns
        assert result["transformed"].all()

    def test_custom_function_not_found(self, sample_df):
        """Test custom operation with non-existent function."""
        mock_module = ModuleType("mock_module")
        op = {"function": "nonexistent"}
        with pytest.raises(ValueError, match="Function 'nonexistent' not found"):
            apply_custom_operation(sample_df, op, mock_module)

    def test_custom_missing_function_key(self, sample_df):
        """Test custom operation without function key."""
        mock_module = ModuleType("mock_module")
        op = {"args": {}}
        with pytest.raises(ValueError, match="requires 'function' key"):
            apply_custom_operation(sample_df, op, mock_module)


class TestExecuteTransformPipeline:
    def test_pipeline_single_operation(self, sample_df):
        """Test pipeline with single operation."""
        operations = [
            {"type": "filter", "column": "status", "values": ["Completed"]}
        ]
        result = execute_transform_pipeline(sample_df, operations)
        assert len(result) == 3
        assert (result["status"] == "Completed").all()

    def test_pipeline_multiple_operations(self, sample_df):
        """Test pipeline with multiple chained operations."""
        operations = [
            {"type": "filter", "column": "status", "values": ["Completed", "Invalid"]},
            {"type": "groupby", "columns": ["region"], "agg": {"duration": "sum"}},
            {"type": "rename", "mapping": {"region": "Region", "duration": "Total Duration"}},
        ]
        result = execute_transform_pipeline(sample_df, operations)
        assert "Region" in result.columns
        assert "Total Duration" in result.columns
        assert len(result) == 3  # AMER, EMEA, APAC

    def test_pipeline_with_custom(self, sample_df):
        """Test pipeline with custom operation."""
        mock_module = ModuleType("mock_module")

        def multiply_duration(df, factor=2):
            df = df.copy()
            df["duration"] = df["duration"] * factor
            return df

        mock_module.multiply_duration = multiply_duration

        operations = [
            {"type": "custom", "function": "multiply_duration", "args": {"factor": 3}},
            {"type": "filter", "column": "region", "values": ["AMER"]},
        ]
        result = execute_transform_pipeline(sample_df, operations, custom_module=mock_module)
        assert len(result) == 2
        assert result["duration"].iloc[0] == 300  # 100 * 3

    def test_pipeline_unknown_operation(self, sample_df):
        """Test pipeline with unknown operation type."""
        operations = [
            {"type": "unknown_op", "param": "value"}
        ]
        with pytest.raises(ValueError, match="Unknown operation type: unknown_op"):
            execute_transform_pipeline(sample_df, operations)

    def test_pipeline_missing_type(self, sample_df):
        """Test pipeline with operation missing type key."""
        operations = [
            {"column": "status"}
        ]
        with pytest.raises(ValueError, match="Operation missing 'type' key"):
            execute_transform_pipeline(sample_df, operations)

    def test_pipeline_custom_without_module(self, sample_df):
        """Test custom operation without providing module."""
        operations = [
            {"type": "custom", "function": "some_func"}
        ]
        with pytest.raises(ValueError, match="requires custom_module"):
            execute_transform_pipeline(sample_df, operations)

    def test_pipeline_complex_scenario(self, pivot_df):
        """Test complex realistic pipeline."""
        operations = [
            # Filter to only completed or invalid
            {"type": "filter", "column": "status", "values": ["Completed", "Invalid"]},
            # Group by year and quarter
            {"type": "groupby", "columns": ["fiscal_year", "quarter"], "agg": {"count": "sum"}},
            # Rename for display
            {"type": "rename", "mapping": {"fiscal_year": "Fiscal Year", "quarter": "Quarter", "count": "Total Count"}},
            # Sort by year
            {"type": "sort", "by": "Fiscal Year", "ascending": True},
        ]
        result = execute_transform_pipeline(pivot_df, operations)
        assert "Fiscal Year" in result.columns
        assert "Quarter" in result.columns
        assert "Total Count" in result.columns
        assert result["Fiscal Year"].iloc[0] == "2023"

    def test_pipeline_empty_operations(self, sample_df):
        """Test pipeline with no operations."""
        operations = []
        result = execute_transform_pipeline(sample_df, operations)
        assert result.equals(sample_df)
