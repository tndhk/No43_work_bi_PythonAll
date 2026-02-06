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

        expected_keys = {"month", "area", "category", "vendor", "amp_av", "order_type"}
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
