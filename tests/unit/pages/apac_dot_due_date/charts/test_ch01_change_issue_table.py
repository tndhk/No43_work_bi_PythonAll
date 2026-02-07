"""Tests for _ch01_change_issue_table.build() -- Change Issue Table chart module.

TDD Step 1 (RED): These tests define the expected behaviour of the
build(filtered_df, breakdown_tab, num_percent_mode) function BEFORE
the implementation exists.

The function should:
- Accept a filtered DataFrame, breakdown_tab key, and num/percent mode
- Return a tuple of (title: str, component: Any)
- Handle empty DataFrames gracefully
- Create a proper pivot table grouped by the breakdown column (BREAKDOWN_MAP_2)
- Use COLUMN_MAP_2 column names
- Support both "number" and "percent" modes
"""
import pandas as pd
import pytest

from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2, BREAKDOWN_MAP_2


# ---------------------------------------------------------------------------
# Helpers -- build sample DataFrames
# ---------------------------------------------------------------------------

def _make_sample_df_2(n_areas=2, n_months=3, n_rows_per_group=5):
    """Create a realistic sample DataFrame matching COLUMN_MAP_2 schema.

    Generates data with:
    - COLUMN_MAP_2['work_order_id']: unique identifiers
    - COLUMN_MAP_2['month']: date values
    - COLUMN_MAP_2['area']: area dimension
    - COLUMN_MAP_2['category']: category dimension
    - COLUMN_MAP_2['vendor']: vendor dimension
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
                    COLUMN_MAP_2["work_order_id"]: f"WO-{wo_id:04d}",
                    COLUMN_MAP_2["month"]: month,
                    COLUMN_MAP_2["area"]: area,
                    COLUMN_MAP_2["category"]: categories[wo_id % 2],
                    COLUMN_MAP_2["vendor"]: vendors[wo_id % 2],
                })
                wo_id += 1
        # Add one duplicate work order id to test nunique
        rows.append({
            COLUMN_MAP_2["work_order_id"]: f"WO-{wo_id - 1:04d}",  # duplicate last id
            COLUMN_MAP_2["month"]: months[0],
            COLUMN_MAP_2["area"]: area,
            COLUMN_MAP_2["category"]: categories[0],
            COLUMN_MAP_2["vendor"]: vendors[0],
        })

    return pd.DataFrame(rows)


def _make_empty_df_2():
    """Create an empty DataFrame with the COLUMN_MAP_2 columns."""
    return pd.DataFrame(columns=[
        COLUMN_MAP_2["work_order_id"],
        COLUMN_MAP_2["month"],
        COLUMN_MAP_2["area"],
        COLUMN_MAP_2["category"],
        COLUMN_MAP_2["vendor"],
    ])


def _make_single_row_df_2():
    """Create a DataFrame with exactly one row using COLUMN_MAP_2 columns."""
    return pd.DataFrame([{
        COLUMN_MAP_2["work_order_id"]: "WO-0001",
        COLUMN_MAP_2["month"]: pd.Timestamp("2024-01-01"),
        COLUMN_MAP_2["area"]: "Area_0",
        COLUMN_MAP_2["category"]: "Cat_A",
        COLUMN_MAP_2["vendor"]: "Vendor_X",
    }])


# ===========================================================================
# Test: Module importability
# ===========================================================================

class TestModuleImport:
    """The charts sub-package and _ch01_change_issue_table module must be importable."""

    def test_charts_package_importable(self):
        import src.pages.apac_dot_due_date.charts  # noqa: F401

    def test_ch01_module_importable(self):
        from src.pages.apac_dot_due_date.charts import _ch01_change_issue_table  # noqa: F401

    def test_build_function_exists(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        assert callable(build)


# ===========================================================================
# Test: Return type and structure
# ===========================================================================

class TestBuildReturnType:
    """build() must return a (str, component) tuple."""

    def test_returns_tuple(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        result = build(df, "area", "number")
        assert isinstance(result, tuple)

    def test_returns_length_two_tuple(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        result = build(df, "area", "number")
        assert len(result) == 2

    def test_first_element_is_string(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        title, _ = build(df, "area", "number")
        assert isinstance(title, str)

    def test_title_contains_change_or_ddd_or_issue(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        title, _ = build(df, "area", "number")
        assert any(kw in title for kw in ("Change", "DDD", "Issue")), (
            f"Title should contain 'Change', 'DDD', or 'Issue', got: {title}"
        )

    def test_title_contains_work_order(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        title, _ = build(df, "area", "number")
        assert "Work Order" in title


# ===========================================================================
# Test: Empty DataFrame handling
# ===========================================================================

class TestBuildEmptyDataFrame:
    """build() must handle empty DataFrames gracefully."""

    def test_empty_df_returns_tuple(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_empty_df_2()
        result = build(df, "area", "number")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_df_returns_title(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_empty_df_2()
        title, _ = build(df, "area", "number")
        assert isinstance(title, str)
        assert any(kw in title for kw in ("Change", "DDD", "Issue"))

    def test_empty_df_returns_html_p(self):
        """When no data, the component should be an html.P element."""
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build
        from dash import html

        df = _make_empty_df_2()
        _, component = build(df, "area", "number")
        assert isinstance(component, html.P)

    def test_zero_length_df_returns_html_p(self):
        """DataFrame with columns but zero rows should also return html.P."""
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build
        from dash import html

        df = _make_empty_df_2()
        assert len(df) == 0
        _, component = build(df, "area", "number")
        assert isinstance(component, html.P)


# ===========================================================================
# Test: Number mode (default)
# ===========================================================================

class TestBuildNumberMode:
    """build() with num_percent_mode='number' should produce count-based pivot."""

    def test_component_is_datatable(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build
        from dash import dash_table

        df = _make_sample_df_2()
        _, component = build(df, "area", "number")
        assert isinstance(component, dash_table.DataTable)

    def test_datatable_has_data(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, "area", "number")
        assert len(component.data) > 0

    def test_datatable_has_columns(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, "area", "number")
        assert len(component.columns) > 0

    def test_datatable_includes_avg_column(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, "area", "number")
        col_names = [c["name"] for c in component.columns]
        assert "AVG" in col_names

    def test_datatable_includes_grand_total_row(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP_2["area"]
        values = [row[breakdown_col] for row in component.data]
        assert "GRAND TOTAL" in values

    def test_grand_total_row_is_last(self):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP_2["area"]
        last_row = component.data[-1]
        assert last_row[breakdown_col] == "GRAND TOTAL"

    def test_grand_total_equals_sum_of_other_rows(self):
        """GRAND TOTAL row values should equal the sum of non-total rows."""
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP_2["area"]

        non_total_rows = [r for r in component.data if r[breakdown_col] != "GRAND TOTAL"]
        grand_total_row = [r for r in component.data if r[breakdown_col] == "GRAND TOTAL"][0]

        # Check all month columns (exclude breakdown and AVG)
        data_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]
        for col in data_cols:
            expected_sum = sum(r[col] for r in non_total_rows)
            assert grand_total_row[col] == expected_sum, (
                f"GRAND TOTAL for '{col}': expected {expected_sum}, got {grand_total_row[col]}"
            )

    def test_number_mode_values_are_counts(self):
        """In number mode, values should be non-negative integers (counts)."""
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP_2["area"]
        data_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]

        for row in component.data:
            for col in data_cols:
                val = row[col]
                assert val >= 0, f"Count should be >= 0, got {val}"

    def test_nunique_counts_work_order_ids(self):
        """Values should be nunique(work order id), not raw row counts."""
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        # Our sample has one duplicate per area in the first month
        df = _make_sample_df_2(n_areas=1, n_months=1, n_rows_per_group=3)
        _, component = build(df, "area", "number")
        breakdown_col = BREAKDOWN_MAP_2["area"]

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
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build
        from dash import dash_table

        df = _make_sample_df_2()
        _, component = build(df, "area", "percent")
        assert isinstance(component, dash_table.DataTable)

    def test_percent_mode_grand_total_is_100(self):
        """In percent mode, GRAND TOTAL for each month column should be 100.0."""
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, "area", "percent")
        breakdown_col = BREAKDOWN_MAP_2["area"]

        grand_total_row = [r for r in component.data if r[breakdown_col] == "GRAND TOTAL"][0]
        data_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]

        for col in data_cols:
            assert grand_total_row[col] == 100.0, (
                f"GRAND TOTAL percent for '{col}' should be 100.0, got {grand_total_row[col]}"
            )

    def test_percent_mode_values_between_0_and_100(self):
        """All percentage values should be between 0 and 100."""
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, "area", "percent")
        breakdown_col = BREAKDOWN_MAP_2["area"]
        data_cols = [c["id"] for c in component.columns if c["id"] not in (breakdown_col, "AVG")]

        for row in component.data:
            for col in data_cols:
                val = row[col]
                assert 0 <= val <= 100, f"Percent value should be 0-100, got {val}"


# ===========================================================================
# Test: Breakdown tab variations
# ===========================================================================

class TestBuildBreakdownTabs:
    """build() should work for all BREAKDOWN_MAP_2 keys."""

    @pytest.mark.parametrize("breakdown_tab", list(BREAKDOWN_MAP_2.keys()))
    def test_each_breakdown_tab_returns_tuple(self, breakdown_tab):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        result = build(df, breakdown_tab, "number")
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.parametrize("breakdown_tab", list(BREAKDOWN_MAP_2.keys()))
    def test_each_breakdown_tab_returns_datatable(self, breakdown_tab):
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build
        from dash import dash_table

        df = _make_sample_df_2()
        _, component = build(df, breakdown_tab, "number")
        assert isinstance(component, dash_table.DataTable)

    @pytest.mark.parametrize("breakdown_tab", list(BREAKDOWN_MAP_2.keys()))
    def test_first_column_is_breakdown_dimension(self, breakdown_tab):
        """First column of the DataTable should be the breakdown dimension column."""
        from src.pages.apac_dot_due_date.charts._ch01_change_issue_table import build

        df = _make_sample_df_2()
        _, component = build(df, breakdown_tab, "number")
        expected_col = BREAKDOWN_MAP_2[breakdown_tab]
        assert component.columns[0]["id"] == expected_col
