"""Tests for APAC DOT Due Date _chart_builders module.

TDD Step 1 (RED): These tests define the expected behavior of
build_pivot_data() -- the aggregation-only function extracted from
the old charts/_pivot_table_builder.py.

build_pivot_data() takes a filtered DataFrame, breakdown tab, num/percent
mode, column map, and breakdown map.  It returns a pivoted DataFrame
suitable for passing to the shared build_table() renderer.
"""
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

def _make_sample_df() -> pd.DataFrame:
    """Create a sample DataFrame mimicking the reference dataset."""
    return pd.DataFrame({
        "Delivery Completed Month": [
            "2024-01", "2024-01", "2024-02", "2024-02",
        ],
        "business area": ["APAC", "EMEA", "APAC", "APAC"],
        "Metric Workstream": ["WS-A", "WS-B", "WS-A", "WS-A"],
        "Vendor: Account Name": ["Vendor1", "Vendor2", "Vendor1", "Vendor1"],
        "AMP VS AV Scope": ["AMP", "AV", "AMP", "AMP"],
        "order tags": ["TypeA", "TypeB", "TypeA", "TypeA"],
        "job name": ["PRC-Job-1", "Normal-Job-2", "PRC-Job-3", "PRC-Job-4"],
        "work order id": ["WO-001", "WO-002", "WO-003", "WO-004"],
    })


_REF_COLUMN_MAP = {
    "month": "Delivery Completed Month",
    "area": "business area",
    "category": "Metric Workstream",
    "vendor": "Vendor: Account Name",
    "amp_av": "AMP VS AV Scope",
    "order_type": "order tags",
    "job_name": "job name",
    "work_order_id": "work order id",
}

_REF_BREAKDOWN_MAP = {
    "area": "business area",
    "category": "Metric Workstream",
    "vendor": "Vendor: Account Name",
}


# ===========================================================================
# Module existence
# ===========================================================================

class TestModuleExists:
    """_chart_builders module must exist and expose build_pivot_data."""

    def test_module_imports(self):
        """_chart_builders module should be importable."""
        from src.pages.apac_dot_due_date import _chart_builders  # noqa: F401

    def test_build_pivot_data_is_callable(self):
        """build_pivot_data must be a callable function."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data
        assert callable(build_pivot_data)


# ===========================================================================
# Return type
# ===========================================================================

class TestBuildPivotDataReturnType:
    """build_pivot_data must return a pandas DataFrame."""

    def test_returns_dataframe(self):
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        assert isinstance(result, pd.DataFrame)

    def test_returns_empty_dataframe_for_empty_input(self):
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        empty_df = pd.DataFrame({
            "Delivery Completed Month": pd.Series(dtype="str"),
            "business area": pd.Series(dtype="str"),
            "Metric Workstream": pd.Series(dtype="str"),
            "Vendor: Account Name": pd.Series(dtype="str"),
            "work order id": pd.Series(dtype="str"),
        })
        result = build_pivot_data(
            filtered_df=empty_df,
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# ===========================================================================
# Pivot structure
# ===========================================================================

class TestPivotStructure:
    """build_pivot_data must produce correct pivot table structure."""

    def test_has_breakdown_column_as_first_col(self):
        """The first column should be the breakdown column."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        assert result.columns[0] == "business area"

    def test_has_month_columns(self):
        """Result should contain month columns derived from data."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        # Data has months 2024-01 and 2024-02
        assert "2024-01" in result.columns.tolist()
        assert "2024-02" in result.columns.tolist()

    def test_has_avg_column(self):
        """Result should contain an AVG column."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        assert "AVG" in result.columns.tolist()

    def test_has_grand_total_row(self):
        """Result should contain a GRAND TOTAL row."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        breakdown_col = "business area"
        assert "GRAND TOTAL" in result[breakdown_col].values

    def test_month_columns_are_sorted(self):
        """Month columns should appear in chronological order."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        cols = result.columns.tolist()
        # Remove first col (breakdown) and last col (AVG)
        month_cols = cols[1:-1]
        assert month_cols == sorted(month_cols)


# ===========================================================================
# Aggregation correctness (num mode)
# ===========================================================================

class TestAggregationNum:
    """build_pivot_data with num mode must count unique work order IDs."""

    def test_counts_unique_work_orders(self):
        """Each cell should contain the count of unique work order IDs."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        # APAC has WO-001 in 2024-01, WO-003 + WO-004 in 2024-02
        apac_row = result[result["business area"] == "APAC"]
        assert len(apac_row) == 1
        assert apac_row["2024-01"].values[0] == 1
        assert apac_row["2024-02"].values[0] == 2

    def test_grand_total_sums_correctly(self):
        """GRAND TOTAL row should sum all breakdown rows."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        grand_total = result[result["business area"] == "GRAND TOTAL"]
        # 2024-01: APAC=1 + EMEA=1 = 2; 2024-02: APAC=2 + EMEA=0 = 2
        assert grand_total["2024-01"].values[0] == 2
        assert grand_total["2024-02"].values[0] == 2

    def test_avg_column_is_mean_of_months(self):
        """AVG column should be the mean of all month columns, rounded to 0 decimal."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        # APAC: mean(1, 2) = 1.5 -> rounded to 2.0
        apac_row = result[result["business area"] == "APAC"]
        assert apac_row["AVG"].values[0] == 2.0

    def test_missing_breakdown_value_filled_with_zero(self):
        """If a breakdown value has no data in a month, cell should be 0."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        # EMEA has no data in 2024-02
        emea_row = result[result["business area"] == "EMEA"]
        assert emea_row["2024-02"].values[0] == 0


# ===========================================================================
# Percent mode
# ===========================================================================

class TestAggregationPercent:
    """build_pivot_data with percent mode must convert counts to percentages."""

    def test_percent_mode_values_are_percentages(self):
        """In percent mode, each cell should be (count / column_total * 100)."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="percent",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        # 2024-01: APAC=1/2*100=50.0, EMEA=1/2*100=50.0
        apac_row = result[result["business area"] == "APAC"]
        assert apac_row["2024-01"].values[0] == 50.0

    def test_percent_grand_total_is_100(self):
        """In percent mode, GRAND TOTAL for each month should be 100.0."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="percent",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        grand_total = result[result["business area"] == "GRAND TOTAL"]
        assert grand_total["2024-01"].values[0] == 100.0
        assert grand_total["2024-02"].values[0] == 100.0

    def test_percent_avg_is_mean_of_percent_months(self):
        """In percent mode, AVG should be mean of percent month values."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="area",
            num_percent_mode="percent",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        # APAC: 50.0% in 2024-01, 100.0% in 2024-02 -> mean = 75.0
        apac_row = result[result["business area"] == "APAC"]
        assert apac_row["AVG"].values[0] == 75.0


# ===========================================================================
# Different breakdown tabs
# ===========================================================================

class TestDifferentBreakdowns:
    """build_pivot_data must respect the breakdown_tab argument."""

    def test_category_breakdown(self):
        """Using breakdown_tab='category' should group by Metric Workstream."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="category",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        assert result.columns[0] == "Metric Workstream"
        assert "WS-A" in result["Metric Workstream"].values
        assert "WS-B" in result["Metric Workstream"].values

    def test_vendor_breakdown(self):
        """Using breakdown_tab='vendor' should group by Vendor: Account Name."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        result = build_pivot_data(
            filtered_df=_make_sample_df(),
            breakdown_tab="vendor",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        assert result.columns[0] == "Vendor: Account Name"
        assert "Vendor1" in result["Vendor: Account Name"].values
        assert "Vendor2" in result["Vendor: Account Name"].values


# ===========================================================================
# Column name formatting
# ===========================================================================

class TestColumnFormatting:
    """Month columns must be formatted as strings (YYYY-MM-DD for datetime, or as-is for strings)."""

    def test_datetime_month_columns_formatted(self):
        """If month column contains datetime values, they should be formatted as strings."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data

        df = _make_sample_df()
        # Convert month strings to actual datetime objects
        df["Delivery Completed Month"] = pd.to_datetime(
            df["Delivery Completed Month"], format="%Y-%m"
        )
        result = build_pivot_data(
            filtered_df=df,
            breakdown_tab="area",
            num_percent_mode="num",
            column_map=_REF_COLUMN_MAP,
            breakdown_map=_REF_BREAKDOWN_MAP,
        )
        # All columns except first (breakdown) and last (AVG) should be string
        month_cols = result.columns.tolist()[1:-1]
        for col in month_cols:
            assert isinstance(col, str)
