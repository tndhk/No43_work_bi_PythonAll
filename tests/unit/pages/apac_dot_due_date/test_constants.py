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


class TestDatasets:
    """DATASETS dict contains DatasetConfig instances for each dataset."""

    def test_datasets_exists(self):
        from src.pages.apac_dot_due_date._constants import DATASETS

        assert DATASETS is not None

    def test_datasets_is_dict(self):
        from src.pages.apac_dot_due_date._constants import DATASETS

        assert isinstance(DATASETS, dict)

    def test_datasets_has_reference_and_change_issue(self):
        from src.pages.apac_dot_due_date._constants import DATASETS

        assert "reference" in DATASETS
        assert "change_issue" in DATASETS

    def test_reference_dataset_config(self):
        from src.pages.apac_dot_due_date._constants import DATASETS, CHART_ID_REFERENCE_TABLE

        ref = DATASETS["reference"]
        assert ref.dataset_id == "apac-dot-due-date"
        assert ref.chart_id == CHART_ID_REFERENCE_TABLE
        assert ref.table_spec_key == "ch00_reference_table"
        assert "order_type" in ref.skip_filters

    def test_change_issue_dataset_config(self):
        from src.pages.apac_dot_due_date._constants import DATASETS, CHART_ID_CHANGE_ISSUE_TABLE

        change = DATASETS["change_issue"]
        assert change.dataset_id == "apac-dot-ddd-change-issue-sql"
        assert change.chart_id == CHART_ID_CHANGE_ISSUE_TABLE
        assert change.table_spec_key == "ch01_change_issue_table"
        assert "amp_av" in change.skip_filters

    def test_reference_column_map_has_all_keys(self):
        from src.pages.apac_dot_due_date._constants import DATASETS

        ref = DATASETS["reference"]
        expected_keys = {
            "month", "area", "category", "vendor",
            "amp_av", "order_type", "job_name", "work_order_id",
        }
        assert set(ref.column_map.keys()) == expected_keys

    def test_change_issue_column_map_has_all_keys(self):
        from src.pages.apac_dot_due_date._constants import DATASETS

        change = DATASETS["change_issue"]
        expected_keys = {
            "month", "area", "category", "vendor",
            "order_type", "job_name", "work_order_id",
        }
        assert set(change.column_map.keys()) == expected_keys
        assert "amp_av" not in change.column_map

    def test_reference_column_map_values(self):
        from src.pages.apac_dot_due_date._constants import DATASETS

        ref = DATASETS["reference"]
        assert ref.column_map["month"] == "Delivery Completed Month"
        assert ref.column_map["area"] == "business area"
        assert ref.column_map["category"] == "Metric Workstream"

    def test_change_issue_column_map_values(self):
        from src.pages.apac_dot_due_date._constants import DATASETS

        change = DATASETS["change_issue"]
        assert change.column_map["month"] == "edit month"
        assert change.column_map["area"] == "business area"
        assert change.column_map["category"] == "metric workstream"

    def test_breakdown_maps_are_subsets(self):
        from src.pages.apac_dot_due_date._constants import DATASETS

        ref = DATASETS["reference"]
        change = DATASETS["change_issue"]

        # Breakdown map keys should be subset of column map keys
        assert set(ref.breakdown_map.keys()).issubset(set(ref.column_map.keys()))
        assert set(change.breakdown_map.keys()).issubset(set(change.column_map.keys()))

        # Breakdown map values should be in column map values
        assert all(v in ref.column_map.values() for v in ref.breakdown_map.values())
        assert all(v in change.column_map.values() for v in change.breakdown_map.values())


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

    def test_ctrl_id_clear_month_exists(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_MONTH
        assert CTRL_ID_CLEAR_MONTH is not None

    def test_ctrl_id_clear_month_value(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_MONTH, ID_PREFIX
        assert CTRL_ID_CLEAR_MONTH == f"{ID_PREFIX}ctrl-clear-month"

    def test_ctrl_id_clear_prc_exists(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_PRC
        assert CTRL_ID_CLEAR_PRC is not None

    def test_ctrl_id_clear_prc_value(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_PRC, ID_PREFIX
        assert CTRL_ID_CLEAR_PRC == f"{ID_PREFIX}ctrl-clear-prc"

    def test_ctrl_id_clear_area_exists(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_AREA
        assert CTRL_ID_CLEAR_AREA is not None

    def test_ctrl_id_clear_area_value(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_AREA, ID_PREFIX
        assert CTRL_ID_CLEAR_AREA == f"{ID_PREFIX}ctrl-clear-area"

    def test_ctrl_id_clear_category_exists(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_CATEGORY
        assert CTRL_ID_CLEAR_CATEGORY is not None

    def test_ctrl_id_clear_category_value(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_CATEGORY, ID_PREFIX
        assert CTRL_ID_CLEAR_CATEGORY == f"{ID_PREFIX}ctrl-clear-category"

    def test_ctrl_id_clear_vendor_exists(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_VENDOR
        assert CTRL_ID_CLEAR_VENDOR is not None

    def test_ctrl_id_clear_vendor_value(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_VENDOR, ID_PREFIX
        assert CTRL_ID_CLEAR_VENDOR == f"{ID_PREFIX}ctrl-clear-vendor"

    def test_ctrl_id_clear_amp_av_exists(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_AMP_AV
        assert CTRL_ID_CLEAR_AMP_AV is not None

    def test_ctrl_id_clear_amp_av_value(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_AMP_AV, ID_PREFIX
        assert CTRL_ID_CLEAR_AMP_AV == f"{ID_PREFIX}ctrl-clear-amp-av"

    def test_ctrl_id_clear_order_type_exists(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_ORDER_TYPE
        assert CTRL_ID_CLEAR_ORDER_TYPE is not None

    def test_ctrl_id_clear_order_type_value(self):
        from src.pages.apac_dot_due_date._constants import CTRL_ID_CLEAR_ORDER_TYPE, ID_PREFIX
        assert CTRL_ID_CLEAR_ORDER_TYPE == f"{ID_PREFIX}ctrl-clear-order-type"

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
            CTRL_ID_CLEAR_MONTH,
            CTRL_ID_CLEAR_PRC,
            CTRL_ID_CLEAR_AREA,
            CTRL_ID_CLEAR_CATEGORY,
            CTRL_ID_CLEAR_VENDOR,
            CTRL_ID_CLEAR_AMP_AV,
            CTRL_ID_CLEAR_ORDER_TYPE,
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
            CTRL_ID_CLEAR_MONTH,
            CTRL_ID_CLEAR_PRC,
            CTRL_ID_CLEAR_AREA,
            CTRL_ID_CLEAR_CATEGORY,
            CTRL_ID_CLEAR_VENDOR,
            CTRL_ID_CLEAR_AMP_AV,
            CTRL_ID_CLEAR_ORDER_TYPE,
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
            CTRL_ID_CLEAR_MONTH,
            CTRL_ID_CLEAR_PRC,
            CTRL_ID_CLEAR_AREA,
            CTRL_ID_CLEAR_CATEGORY,
            CTRL_ID_CLEAR_VENDOR,
            CTRL_ID_CLEAR_AMP_AV,
            CTRL_ID_CLEAR_ORDER_TYPE,
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
            CTRL_ID_CLEAR_MONTH,
            CTRL_ID_CLEAR_PRC,
            CTRL_ID_CLEAR_AREA,
            CTRL_ID_CLEAR_CATEGORY,
            CTRL_ID_CLEAR_VENDOR,
            CTRL_ID_CLEAR_AMP_AV,
            CTRL_ID_CLEAR_ORDER_TYPE,
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


class TestTableSpecs:
    """TABLE_SPECS must be defined in _constants.py using shared TableSpec from src.charts.specs."""

    def test_table_specs_exists(self):
        """TABLE_SPECS dict must be importable from _constants."""
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        assert TABLE_SPECS is not None

    def test_table_specs_is_dict(self):
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        assert isinstance(TABLE_SPECS, dict)

    def test_table_specs_has_expected_keys(self):
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        assert "ch00_reference_table" in TABLE_SPECS
        assert "ch01_change_issue_table" in TABLE_SPECS

    def test_table_specs_uses_shared_table_spec_class(self):
        """TABLE_SPECS values must be instances of the shared TableSpec from src.charts.specs."""
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        from src.charts.specs import TableSpec

        for key, spec in TABLE_SPECS.items():
            assert isinstance(spec, TableSpec), (
                f"TABLE_SPECS['{key}'] is {type(spec).__module__}.{type(spec).__name__}, "
                f"not src.charts.specs.TableSpec"
            )

    def test_reference_table_spec_title(self):
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        assert TABLE_SPECS["ch00_reference_table"].title == "0) Reference : Number of Work Order"

    def test_change_issue_table_spec_title(self):
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        assert TABLE_SPECS["ch01_change_issue_table"].title == "1) DDD Change + Issue : Number of Work Order"

    def test_table_specs_have_style_table(self):
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        for key, spec in TABLE_SPECS.items():
            assert isinstance(spec.style_table, dict), f"TABLE_SPECS['{key}'].style_table missing"

    def test_table_specs_have_style_cell(self):
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        for key, spec in TABLE_SPECS.items():
            assert isinstance(spec.style_cell, dict), f"TABLE_SPECS['{key}'].style_cell missing"

    def test_table_specs_have_style_header(self):
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        for key, spec in TABLE_SPECS.items():
            assert isinstance(spec.style_header, dict), f"TABLE_SPECS['{key}'].style_header missing"

    def test_table_specs_have_style_data_conditional(self):
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        for key, spec in TABLE_SPECS.items():
            assert isinstance(spec.style_data_conditional, list), (
                f"TABLE_SPECS['{key}'].style_data_conditional missing"
            )

    def test_table_specs_consistent_with_datasets(self):
        """Every DATASETS entry's table_spec_key must exist in TABLE_SPECS."""
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS, DATASETS
        for ds_key, ds_cfg in DATASETS.items():
            assert ds_cfg.table_spec_key in TABLE_SPECS, (
                f"DATASETS['{ds_key}'].table_spec_key='{ds_cfg.table_spec_key}' "
                f"not found in TABLE_SPECS"
            )
