"""Tests for _ch00_reference_table.build() -- Reference Table chart module.

TDD Step 1 (RED): These tests define the expected behaviour of the
build(filtered_df, breakdown_tab, num_percent_mode) function BEFORE
the implementation exists.

The function should:
- Accept a filtered DataFrame, breakdown_tab key, and num/percent mode
- Return a tuple of (title: str, component: Any)
- Handle empty DataFrames gracefully
- Handle errors gracefully
- Create a proper pivot table grouped by the breakdown column
- Support both "number" and "percent" modes
"""
import pandas as pd
import pytest

from src.pages.apac_dot_due_date._constants import COLUMN_MAP, BREAKDOWN_MAP


# ---------------------------------------------------------------------------
# Helpers -- build sample DataFrames
# ---------------------------------------------------------------------------

def _make_sample_df(n_areas=2, n_months=3, n_rows_per_group=5):
    """Create a realistic sample DataFrame matching the expected schema.

    Generates data with:
    - COLUMN_MAP['work_order_id']: unique identifiers
    - COLUMN_MAP['month']: date values
    - 'business area': area dimension
    - 'Metric Workstream': category dimension
    - 'Vendor: Account Name': vendor dimension
    """
    rows = []
    wo_id = 1
    areas = [f"Area_{i}" for i in range(n_areas)]
    categories = ["Cat_A", "Cat_B"]
    vendors = ["Vendor_X", "Vendor_Y"]
    months = pd.date_range("2024-01-01", periods=n_months, freq="MS")

    for area in areas:
        for month in months:
            for _ in range(n_rows_per_group):
                rows.append({
                    COLUMN_MAP["work_order_id"]: f"WO-{wo_id:04d}",
                    COLUMN_MAP["month"]: month,
                    "business area": area,
                    "Metric Workstream": categories[wo_id % 2],
                    "Vendor: Account Name": vendors[wo_id % 2],
                })
                wo_id += 1
        # Add one duplicate work order id to test nunique
        rows.append({
            COLUMN_MAP["work_order_id"]: f"WO-{wo_id - 1:04d}",  # duplicate last id
            COLUMN_MAP["month"]: months[0],
            "business area": area,
            "Metric Workstream": categories[0],
            "Vendor: Account Name": vendors[0],
        })

    return pd.DataFrame(rows)


def _make_empty_df():
    """Create an empty DataFrame with the expected columns."""
    return pd.DataFrame(columns=[
        COLUMN_MAP["work_order_id"],
        COLUMN_MAP["month"],
        "business area",
        "Metric Workstream",
        "Vendor: Account Name",
    ])


def _make_single_row_df():
    """Create a DataFrame with exactly one row."""
    return pd.DataFrame([{
        COLUMN_MAP["work_order_id"]: "WO-0001",
        COLUMN_MAP["month"]: pd.Timestamp("2024-01-01"),
        "business area": "Area_0",
        "Metric Workstream": "Cat_A",
        "Vendor: Account Name": "Vendor_X",
    }])


# ===========================================================================
# Test: Module importability
# ===========================================================================

class TestModuleImport:
    """The charts sub-package and _ch00_reference_table module must be importable."""

    def test_charts_package_importable(self):
        import src.pages.apac_dot_due_date.charts  # noqa: F401

    def test_ch00_module_importable(self):
        from src.pages.apac_dot_due_date.charts import _ch00_reference_table  # noqa: F401

    def test_build_function_exists(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        assert callable(build)


# ===========================================================================
# Test: Return type and structure
# ===========================================================================

class TestBuildReturnType:
    """build() must return a (str, component) tuple."""

    def test_returns_tuple(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        result = build(df, "area", "number")
        assert isinstance(result, tuple)

    def test_returns_length_two_tuple(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        result = build(df, "area", "number")
        assert len(result) == 2

    def test_first_element_is_string(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        title, _ = build(df, "area", "number")
        assert isinstance(title, str)

    def test_title_contains_reference(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        title, _ = build(df, "area", "number")
        assert "Reference" in title

    def test_title_contains_work_order(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        title, _ = build(df, "area", "number")
        assert "Work Order" in title


# ===========================================================================
# Test: Empty DataFrame handling
# ===========================================================================

class TestBuildEmptyDataFrame:
    """build() must handle empty DataFrames gracefully."""

    def test_empty_df_returns_tuple(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_empty_df()
        result = build(df, "area", "number")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_df_returns_title(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_empty_df()
        title, _ = build(df, "area", "number")
        assert isinstance(title, str)
        assert "Reference" in title

    def test_empty_df_returns_no_data_message(self):
        """When no data, the component should be an html element with a message."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build
        from dash import html

        df = _make_empty_df()
        _, component = build(df, "area", "number")
        # Should be an html.P with a "no data" type message
        assert isinstance(component, html.P)

    def test_zero_length_df_returns_no_data_message(self):
        """DataFrame with columns but zero rows should also return no-data."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build
        from dash import html

        df = _make_empty_df()
        assert len(df) == 0
        _, component = build(df, "area", "number")
        assert isinstance(component, html.P)


# ===========================================================================
# Test: Number mode (default)
# ===========================================================================

class TestBuildNumberMode:
    """build() with num_percent_mode='number' should produce count-based pivot."""

    def test_component_is_datatable(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build
        from dash import dash_table

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        assert isinstance(component, dash_table.DataTable)

    def test_datatable_has_data(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        assert len(component.data) > 0

    def test_datatable_has_columns(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        assert len(component.columns) > 0

    def test_datatable_includes_avg_column(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        col_names = [c["name"] for c in component.columns]
        assert "AVG" in col_names

    def test_datatable_includes_grand_total_row(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP["area"]
        values = [row[breakdown_col] for row in component.data]
        assert "GRAND TOTAL" in values

    def test_grand_total_row_is_last(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP["area"]
        last_row = component.data[-1]
        assert last_row[breakdown_col] == "GRAND TOTAL"

    def test_grand_total_equals_sum_of_other_rows(self):
        """GRAND TOTAL row values should equal the sum of non-total rows."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP["area"]

        non_total_rows = [r for r in component.data if r[breakdown_col] != "GRAND TOTAL"]
        grand_total_row = [r for r in component.data if r[breakdown_col] == "GRAND TOTAL"][0]

        # Check a month column (first non-breakdown, non-AVG column)
        data_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]
        for col in data_cols:
            expected_sum = sum(r[col] for r in non_total_rows)
            assert grand_total_row[col] == expected_sum, (
                f"GRAND TOTAL for '{col}': expected {expected_sum}, got {grand_total_row[col]}"
            )

    def test_number_mode_values_are_counts(self):
        """In number mode, values should be non-negative integers (counts)."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP["area"]
        data_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]

        for row in component.data:
            for col in data_cols:
                val = row[col]
                assert val >= 0, f"Count should be >= 0, got {val}"

    def test_nunique_counts_work_order_ids(self):
        """Values should be nunique(work order id), not raw row counts."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        # Our sample has one duplicate per area in the first month
        df = _make_sample_df(n_areas=1, n_months=1, n_rows_per_group=3)
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP["area"]

        # There should be exactly 1 area row + 1 GRAND TOTAL row
        area_rows = [r for r in component.data if r[breakdown_col] != "GRAND TOTAL"]
        assert len(area_rows) == 1

        # The area has 3 unique WO ids (n_rows_per_group=3), NOT 4 (3+1 dup)
        month_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]
        assert len(month_cols) == 1
        assert area_rows[0][month_cols[0]] == 3


# ===========================================================================
# Test: Percent mode
# ===========================================================================

class TestBuildPercentMode:
    """build() with num_percent_mode='percent' should produce percentage-based pivot."""

    def test_percent_mode_returns_datatable(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build
        from dash import dash_table

        df = _make_sample_df()
        _, component = build(df, "area", "percent")
        assert isinstance(component, dash_table.DataTable)

    def test_percent_mode_grand_total_is_100(self):
        """In percent mode, GRAND TOTAL for each month column should be 100.0."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "percent")
        breakdown_col = BREAKDOWN_MAP["area"]

        grand_total_row = [r for r in component.data if r[breakdown_col] == "GRAND TOTAL"][0]
        data_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]

        for col in data_cols:
            assert grand_total_row[col] == 100.0, (
                f"GRAND TOTAL percent for '{col}' should be 100.0, got {grand_total_row[col]}"
            )

    def test_percent_mode_values_between_0_and_100(self):
        """All percentage values should be between 0 and 100."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "percent")
        breakdown_col = BREAKDOWN_MAP["area"]
        data_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]

        for row in component.data:
            for col in data_cols:
                val = row[col]
                assert 0 <= val <= 100, f"Percent value should be 0-100, got {val}"


# ===========================================================================
# Test: Breakdown tab variations
# ===========================================================================

class TestBuildBreakdownTabs:
    """build() should work for all BREAKDOWN_MAP keys."""

    @pytest.mark.parametrize("breakdown_tab", list(BREAKDOWN_MAP.keys()))
    def test_each_breakdown_tab_returns_tuple(self, breakdown_tab):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        result = build(df, breakdown_tab, "number")
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.parametrize("breakdown_tab", list(BREAKDOWN_MAP.keys()))
    def test_each_breakdown_tab_returns_datatable(self, breakdown_tab):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build
        from dash import dash_table

        df = _make_sample_df()
        _, component = build(df, breakdown_tab, "number")
        assert isinstance(component, dash_table.DataTable)

    @pytest.mark.parametrize("breakdown_tab", list(BREAKDOWN_MAP.keys()))
    def test_first_column_is_breakdown_dimension(self, breakdown_tab):
        """First column of the DataTable should be the breakdown dimension column."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, breakdown_tab, "number")
        expected_col = BREAKDOWN_MAP[breakdown_tab]
        assert component.columns[0]["id"] == expected_col


# ===========================================================================
# Test: Single row DataFrame (edge case)
# ===========================================================================

class TestBuildSingleRow:
    """build() should handle a single-row DataFrame without errors."""

    def test_single_row_returns_datatable(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build
        from dash import dash_table

        df = _make_single_row_df()
        _, component = build(df, "area", "number")
        assert isinstance(component, dash_table.DataTable)

    def test_single_row_has_grand_total(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_single_row_df()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP["area"]
        values = [r[breakdown_col] for r in component.data]
        assert "GRAND TOTAL" in values

    def test_single_row_grand_total_equals_data_row(self):
        """With one data row, GRAND TOTAL should equal that row's values."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_single_row_df()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP["area"]

        data_row = [r for r in component.data if r[breakdown_col] != "GRAND TOTAL"][0]
        total_row = [r for r in component.data if r[breakdown_col] == "GRAND TOTAL"][0]
        data_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]

        for col in data_cols:
            assert data_row[col] == total_row[col]


# ===========================================================================
# Test: DataTable styling
# ===========================================================================

class TestBuildStyling:
    """build() should apply proper styling to the DataTable."""

    def test_table_has_overflow_x_auto(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        assert component.style_table.get("overflowX") == "auto"

    def test_header_has_bold_font(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        assert component.style_header.get("fontWeight") == "bold"

    def test_header_has_blue_background(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        assert component.style_header.get("backgroundColor") == "#2563eb"

    def test_grand_total_row_conditional_style(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        # Should have at least one conditional style for GRAND TOTAL
        assert len(component.style_data_conditional) > 0
        # The filter query should reference GRAND TOTAL
        found = any(
            "GRAND TOTAL" in style.get("if", {}).get("filter_query", "")
            for style in component.style_data_conditional
        )
        assert found, "No conditional style found for GRAND TOTAL row"


# ===========================================================================
# Test: Month column sorting
# ===========================================================================

class TestBuildMonthSorting:
    """Month columns should be sorted chronologically."""

    def test_month_columns_are_sorted(self):
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df(n_months=4)
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP["area"]

        # Extract month column names (excluding breakdown and AVG)
        month_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]
        assert month_cols == sorted(month_cols), (
            f"Month columns not sorted: {month_cols}"
        )

    def test_month_columns_are_string_formatted(self):
        """Month column names should be string-formatted dates, not Timestamps."""
        from src.pages.apac_dot_due_date.charts._ch00_reference_table import build

        df = _make_sample_df()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP["area"]

        month_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]
        for col_name in month_cols:
            assert isinstance(col_name, str), f"Column name should be str, got {type(col_name)}"
            # Should not contain "Timestamp" string representation
            assert "Timestamp" not in col_name, f"Column name looks like a Timestamp: {col_name}"
