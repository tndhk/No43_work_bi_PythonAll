"""Tests for APAC DOT Due Date constants module.

TDD Step 1 (RED): These tests define the expected constants that should
exist in src/pages/apac_dot_due_date/_constants.py.
"""
import pytest


class TestDatasetId:
    """DATASET_ID must be the correct S3/Parquet dataset identifier."""

    def test_dataset_id_exists(self):
        from src.pages.apac_dot_due_date._constants import DATASET_ID

        assert DATASET_ID is not None

    def test_dataset_id_value(self):
        from src.pages.apac_dot_due_date._constants import DATASET_ID

        assert DATASET_ID == "apac-dot-due-date"

    def test_dataset_id_is_string(self):
        from src.pages.apac_dot_due_date._constants import DATASET_ID

        assert isinstance(DATASET_ID, str)


class TestIdPrefix:
    """ID_PREFIX must be set for component ID namespacing to avoid collisions."""

    def test_id_prefix_exists(self):
        from src.pages.apac_dot_due_date._constants import ID_PREFIX

        assert ID_PREFIX is not None

    def test_id_prefix_value(self):
        from src.pages.apac_dot_due_date._constants import ID_PREFIX

        assert ID_PREFIX == "apac-dot-"

    def test_id_prefix_is_string(self):
        from src.pages.apac_dot_due_date._constants import ID_PREFIX

        assert isinstance(ID_PREFIX, str)

    def test_id_prefix_ends_with_separator(self):
        """ID_PREFIX should end with a separator character for easy concatenation."""
        from src.pages.apac_dot_due_date._constants import ID_PREFIX

        assert ID_PREFIX.endswith("-")


class TestColumnMap:
    """COLUMN_MAP maps filter component IDs to DataFrame column names."""

    def test_column_map_exists(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert COLUMN_MAP is not None

    def test_column_map_is_dict(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert isinstance(COLUMN_MAP, dict)

    def test_column_map_has_all_expected_keys(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        expected_keys = {
            "month",
            "area",
            "category",
            "vendor",
            "amp_av",
            "order_type",
            "job_name",
            "work_order_id",
        }
        assert set(COLUMN_MAP.keys()) == expected_keys

    def test_column_map_month(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert COLUMN_MAP["month"] == "Delivery Completed Month"

    def test_column_map_area(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert COLUMN_MAP["area"] == "business area"

    def test_column_map_category(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert COLUMN_MAP["category"] == "Metric Workstream"

    def test_column_map_vendor(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert COLUMN_MAP["vendor"] == "Vendor: Account Name"

    def test_column_map_amp_av(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert COLUMN_MAP["amp_av"] == "AMP VS AV Scope"

    def test_column_map_order_type(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert COLUMN_MAP["order_type"] == "order tags"

    def test_column_map_job_name(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert COLUMN_MAP["job_name"] == "job name"

    def test_column_map_work_order_id(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        assert COLUMN_MAP["work_order_id"] == "work order id"

    def test_column_map_values_are_all_strings(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        for key, value in COLUMN_MAP.items():
            assert isinstance(value, str), f"COLUMN_MAP['{key}'] is not a string: {value}"

    def test_column_map_keys_are_all_strings(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP

        for key in COLUMN_MAP.keys():
            assert isinstance(key, str), f"COLUMN_MAP key is not a string: {key}"


class TestBreakdownMap:
    """BREAKDOWN_MAP maps tab IDs to DataFrame column names for pivot breakdown."""

    def test_breakdown_map_exists(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP

        assert BREAKDOWN_MAP is not None

    def test_breakdown_map_is_dict(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP

        assert isinstance(BREAKDOWN_MAP, dict)

    def test_breakdown_map_has_all_expected_keys(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP

        expected_keys = {"area", "category", "vendor"}
        assert set(BREAKDOWN_MAP.keys()) == expected_keys

    def test_breakdown_map_area(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP

        assert BREAKDOWN_MAP["area"] == "business area"

    def test_breakdown_map_category(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP

        assert BREAKDOWN_MAP["category"] == "Metric Workstream"

    def test_breakdown_map_vendor(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP

        assert BREAKDOWN_MAP["vendor"] == "Vendor: Account Name"

    def test_breakdown_map_values_are_all_strings(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP

        for key, value in BREAKDOWN_MAP.items():
            assert isinstance(value, str), f"BREAKDOWN_MAP['{key}'] is not a string: {value}"


class TestComponentIds:
    """All component IDs must be defined as constants using ID_PREFIX.

    This ensures consistency between _filters.py, _callbacks.py, and _layout.py
    and prevents hardcoded strings from drifting out of sync.
    """

    # --- Control IDs ---

    def test_ctrl_id_num_percent_exists(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_NUM_PERCENT

        assert CTRL_ID_NUM_PERCENT is not None

    def test_ctrl_id_num_percent_value(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_NUM_PERCENT, ID_PREFIX

        assert CTRL_ID_NUM_PERCENT == f"{ID_PREFIX}ctrl-num-percent"

    def test_ctrl_id_breakdown_exists(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_BREAKDOWN

        assert CTRL_ID_BREAKDOWN is not None

    def test_ctrl_id_breakdown_value(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_BREAKDOWN, ID_PREFIX

        assert CTRL_ID_BREAKDOWN == f"{ID_PREFIX}ctrl-breakdown"

    # --- Filter IDs ---

    def test_filter_id_month_exists(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_MONTH

        assert FILTER_ID_MONTH is not None

    def test_filter_id_month_value(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_MONTH, ID_PREFIX

        assert FILTER_ID_MONTH == f"{ID_PREFIX}filter-month"

    def test_filter_id_prc_exists(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_PRC

        assert FILTER_ID_PRC is not None

    def test_filter_id_prc_value(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_PRC, ID_PREFIX

        assert FILTER_ID_PRC == f"{ID_PREFIX}filter-prc"

    def test_filter_id_area_exists(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_AREA

        assert FILTER_ID_AREA is not None

    def test_filter_id_area_value(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_AREA, ID_PREFIX

        assert FILTER_ID_AREA == f"{ID_PREFIX}filter-area"

    def test_filter_id_category_exists(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_CATEGORY

        assert FILTER_ID_CATEGORY is not None

    def test_filter_id_category_value(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_CATEGORY, ID_PREFIX

        assert FILTER_ID_CATEGORY == f"{ID_PREFIX}filter-category"

    def test_filter_id_vendor_exists(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_VENDOR

        assert FILTER_ID_VENDOR is not None

    def test_filter_id_vendor_value(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_VENDOR, ID_PREFIX

        assert FILTER_ID_VENDOR == f"{ID_PREFIX}filter-vendor"

    def test_filter_id_amp_av_exists(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_AMP_AV

        assert FILTER_ID_AMP_AV is not None

    def test_filter_id_amp_av_value(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_AMP_AV, ID_PREFIX

        assert FILTER_ID_AMP_AV == f"{ID_PREFIX}filter-amp-av"

    def test_filter_id_order_type_exists(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_ORDER_TYPE

        assert FILTER_ID_ORDER_TYPE is not None

    def test_filter_id_order_type_value(self):
        from src.pages.apac_dot_due_date._constants import FILTER_ID_ORDER_TYPE, ID_PREFIX

        assert FILTER_ID_ORDER_TYPE == f"{ID_PREFIX}filter-order-type"

    # --- Chart IDs ---

    def test_chart_id_reference_table_title_exists(self):
        from src.pages.apac_dot_due_date._constants import CHART_ID_REFERENCE_TABLE_TITLE

        assert CHART_ID_REFERENCE_TABLE_TITLE is not None

    def test_chart_id_reference_table_title_value(self):
        from src.pages.apac_dot_due_date._constants import (
            CHART_ID_REFERENCE_TABLE_TITLE,
            CHART_ID_REFERENCE_TABLE,
        )

        assert CHART_ID_REFERENCE_TABLE_TITLE == f"{CHART_ID_REFERENCE_TABLE}-title"

    # --- All IDs use ID_PREFIX ---

    def test_all_component_ids_start_with_id_prefix(self):
        from src.pages.apac_dot_due_date._constants import (
            ID_PREFIX,
            CTRL_ID_NUM_PERCENT,
            CTRL_ID_BREAKDOWN,
            FILTER_ID_MONTH,
            FILTER_ID_PRC,
            FILTER_ID_AREA,
            FILTER_ID_CATEGORY,
            FILTER_ID_VENDOR,
            FILTER_ID_AMP_AV,
            FILTER_ID_ORDER_TYPE,
            CHART_ID_REFERENCE_TABLE,
            CHART_ID_REFERENCE_TABLE_TITLE,
            CHART_ID_CHANGE_ISSUE_TABLE,
            CHART_ID_CHANGE_ISSUE_TABLE_TITLE,
        )

        all_ids = [
            CTRL_ID_NUM_PERCENT,
            CTRL_ID_BREAKDOWN,
            FILTER_ID_MONTH,
            FILTER_ID_PRC,
            FILTER_ID_AREA,
            FILTER_ID_CATEGORY,
            FILTER_ID_VENDOR,
            FILTER_ID_AMP_AV,
            FILTER_ID_ORDER_TYPE,
            CHART_ID_REFERENCE_TABLE,
            CHART_ID_REFERENCE_TABLE_TITLE,
            CHART_ID_CHANGE_ISSUE_TABLE,
            CHART_ID_CHANGE_ISSUE_TABLE_TITLE,
        ]
        for component_id in all_ids:
            assert component_id.startswith(ID_PREFIX), (
                f"Component ID '{component_id}' does not start with '{ID_PREFIX}'"
            )

    def test_all_component_ids_are_strings(self):
        from src.pages.apac_dot_due_date._constants import (
            CTRL_ID_NUM_PERCENT,
            CTRL_ID_BREAKDOWN,
            FILTER_ID_MONTH,
            FILTER_ID_PRC,
            FILTER_ID_AREA,
            FILTER_ID_CATEGORY,
            FILTER_ID_VENDOR,
            FILTER_ID_AMP_AV,
            FILTER_ID_ORDER_TYPE,
            CHART_ID_REFERENCE_TABLE_TITLE,
        )

        all_ids = [
            CTRL_ID_NUM_PERCENT,
            CTRL_ID_BREAKDOWN,
            FILTER_ID_MONTH,
            FILTER_ID_PRC,
            FILTER_ID_AREA,
            FILTER_ID_CATEGORY,
            FILTER_ID_VENDOR,
            FILTER_ID_AMP_AV,
            FILTER_ID_ORDER_TYPE,
            CHART_ID_REFERENCE_TABLE_TITLE,
        ]
        for component_id in all_ids:
            assert isinstance(component_id, str), (
                f"Component ID {component_id!r} is not a string"
            )


class TestDatasetId2:
    """DATASET_ID_2 must be the correct S3/Parquet dataset identifier for change-issue data."""

    def test_dataset_id_2_exists(self):
        from src.pages.apac_dot_due_date._constants import DATASET_ID_2

        assert DATASET_ID_2 is not None

    def test_dataset_id_2_value(self):
        from src.pages.apac_dot_due_date._constants import DATASET_ID_2

        assert DATASET_ID_2 == "apac-dot-ddd-change-issue-sql"

    def test_dataset_id_2_is_string(self):
        from src.pages.apac_dot_due_date._constants import DATASET_ID_2

        assert isinstance(DATASET_ID_2, str)


class TestColumnMap2:
    """COLUMN_MAP_2 maps filter component IDs to DataFrame column names for change-issue data."""

    def test_column_map_2_exists(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert COLUMN_MAP_2 is not None

    def test_column_map_2_is_dict(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert isinstance(COLUMN_MAP_2, dict)

    def test_column_map_2_has_7_keys(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert len(COLUMN_MAP_2) == 7

    def test_column_map_2_has_all_expected_keys(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        expected_keys = {
            "month",
            "area",
            "category",
            "vendor",
            "order_type",
            "job_name",
            "work_order_id",
        }
        assert set(COLUMN_MAP_2.keys()) == expected_keys

    def test_column_map_2_does_not_contain_amp_av(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert "amp_av" not in COLUMN_MAP_2

    def test_column_map_2_month(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert COLUMN_MAP_2["month"] == "edit month"

    def test_column_map_2_area(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert COLUMN_MAP_2["area"] == "business area"

    def test_column_map_2_category(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert COLUMN_MAP_2["category"] == "metric workstream"

    def test_column_map_2_vendor(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert COLUMN_MAP_2["vendor"] == "vendor: account name"

    def test_column_map_2_order_type(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert COLUMN_MAP_2["order_type"] == "order types"

    def test_column_map_2_job_name(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert COLUMN_MAP_2["job_name"] == "job name"

    def test_column_map_2_work_order_id(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        assert COLUMN_MAP_2["work_order_id"] == "work order: work order id"

    def test_column_map_2_values_are_all_strings(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        for key, value in COLUMN_MAP_2.items():
            assert isinstance(value, str), (
                f"COLUMN_MAP_2['{key}'] is not a string: {value}"
            )

    def test_column_map_2_keys_are_all_strings(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2

        for key in COLUMN_MAP_2.keys():
            assert isinstance(key, str), f"COLUMN_MAP_2 key is not a string: {key}"


class TestBreakdownMap2:
    """BREAKDOWN_MAP_2 maps tab IDs to DataFrame column names for change-issue pivot breakdown."""

    def test_breakdown_map_2_exists(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP_2

        assert BREAKDOWN_MAP_2 is not None

    def test_breakdown_map_2_is_dict(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP_2

        assert isinstance(BREAKDOWN_MAP_2, dict)

    def test_breakdown_map_2_has_3_keys(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP_2

        assert len(BREAKDOWN_MAP_2) == 3

    def test_breakdown_map_2_has_all_expected_keys(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP_2

        expected_keys = {"area", "category", "vendor"}
        assert set(BREAKDOWN_MAP_2.keys()) == expected_keys

    def test_breakdown_map_2_area(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP_2

        assert BREAKDOWN_MAP_2["area"] == "business area"

    def test_breakdown_map_2_category(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP_2

        assert BREAKDOWN_MAP_2["category"] == "metric workstream"

    def test_breakdown_map_2_vendor(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP_2

        assert BREAKDOWN_MAP_2["vendor"] == "vendor: account name"

    def test_breakdown_map_2_values_are_all_strings(self):
        from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP_2

        for key, value in BREAKDOWN_MAP_2.items():
            assert isinstance(value, str), (
                f"BREAKDOWN_MAP_2['{key}'] is not a string: {value}"
            )

    def test_breakdown_map_2_is_subset_of_column_map_2_values(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2, BREAKDOWN_MAP_2

        column_values = set(COLUMN_MAP_2.values())
        for key, value in BREAKDOWN_MAP_2.items():
            assert value in column_values, (
                f"BREAKDOWN_MAP_2['{key}'] = '{value}' is not found in COLUMN_MAP_2 values"
            )

    def test_breakdown_map_2_keys_are_subset_of_column_map_2_keys(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP_2, BREAKDOWN_MAP_2

        column_keys = set(COLUMN_MAP_2.keys())
        for key in BREAKDOWN_MAP_2.keys():
            assert key in column_keys, (
                f"BREAKDOWN_MAP_2 key '{key}' is not found in COLUMN_MAP_2 keys"
            )


class TestChartId01:
    """CHART_ID_CHANGE_ISSUE_TABLE must use ID_PREFIX and follow naming conventions."""

    def test_chart_id_change_issue_table_exists(self):
        from src.pages.apac_dot_due_date._constants import CHART_ID_CHANGE_ISSUE_TABLE

        assert CHART_ID_CHANGE_ISSUE_TABLE is not None

    def test_chart_id_change_issue_table_value(self):
        from src.pages.apac_dot_due_date._constants import CHART_ID_CHANGE_ISSUE_TABLE

        assert CHART_ID_CHANGE_ISSUE_TABLE == "apac-dot-chart-01"

    def test_chart_id_change_issue_table_uses_id_prefix(self):
        from src.pages.apac_dot_due_date._constants import (
            CHART_ID_CHANGE_ISSUE_TABLE,
            ID_PREFIX,
        )

        assert CHART_ID_CHANGE_ISSUE_TABLE == f"{ID_PREFIX}chart-01"

    def test_chart_id_change_issue_table_is_string(self):
        from src.pages.apac_dot_due_date._constants import CHART_ID_CHANGE_ISSUE_TABLE

        assert isinstance(CHART_ID_CHANGE_ISSUE_TABLE, str)

    def test_chart_id_change_issue_table_title_exists(self):
        from src.pages.apac_dot_due_date._constants import CHART_ID_CHANGE_ISSUE_TABLE_TITLE

        assert CHART_ID_CHANGE_ISSUE_TABLE_TITLE is not None

    def test_chart_id_change_issue_table_title_value(self):
        from src.pages.apac_dot_due_date._constants import (
            CHART_ID_CHANGE_ISSUE_TABLE,
            CHART_ID_CHANGE_ISSUE_TABLE_TITLE,
        )

        assert CHART_ID_CHANGE_ISSUE_TABLE_TITLE == f"{CHART_ID_CHANGE_ISSUE_TABLE}-title"

    def test_chart_id_change_issue_table_title_is_string(self):
        from src.pages.apac_dot_due_date._constants import CHART_ID_CHANGE_ISSUE_TABLE_TITLE

        assert isinstance(CHART_ID_CHANGE_ISSUE_TABLE_TITLE, str)


class TestBreakdownMapIsSubsetOfColumnMap:
    """BREAKDOWN_MAP values should be a subset of COLUMN_MAP values,
    ensuring consistency between filter columns and breakdown columns."""

    def test_breakdown_values_are_subset_of_column_values(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP, BREAKDOWN_MAP

        column_values = set(COLUMN_MAP.values())
        for key, value in BREAKDOWN_MAP.items():
            assert value in column_values, (
                f"BREAKDOWN_MAP['{key}'] = '{value}' is not found in COLUMN_MAP values"
            )

    def test_breakdown_keys_are_subset_of_column_keys(self):
        from src.pages.apac_dot_due_date._constants import COLUMN_MAP, BREAKDOWN_MAP

        column_keys = set(COLUMN_MAP.keys())
        for key in BREAKDOWN_MAP.keys():
            assert key in column_keys, (
                f"BREAKDOWN_MAP key '{key}' is not found in COLUMN_MAP keys"
            )
