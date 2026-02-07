"""Tests for Cursor Usage constants module.

TDD Step 1 (RED): These tests define the expected constants that should
exist in src/pages/cursor_usage/_constants.py.
The module does not exist yet, so all tests MUST fail with ImportError.
"""
import pytest


class TestDatasetId:
    """DATASET_ID must be the correct S3/Parquet dataset identifier."""

    def test_dataset_id_exists(self):
        from src.pages.cursor_usage._constants import DATASET_ID

        assert DATASET_ID is not None

    def test_dataset_id_value(self):
        from src.pages.cursor_usage._constants import DATASET_ID

        assert DATASET_ID == "cursor-usage"

    def test_dataset_id_is_string(self):
        from src.pages.cursor_usage._constants import DATASET_ID

        assert isinstance(DATASET_ID, str)


class TestIdPrefix:
    """ID_PREFIX must be set for component ID namespacing to avoid collisions."""

    def test_id_prefix_exists(self):
        from src.pages.cursor_usage._constants import ID_PREFIX

        assert ID_PREFIX is not None

    def test_id_prefix_value(self):
        from src.pages.cursor_usage._constants import ID_PREFIX

        assert ID_PREFIX == "cu-"

    def test_id_prefix_is_string(self):
        from src.pages.cursor_usage._constants import ID_PREFIX

        assert isinstance(ID_PREFIX, str)

    def test_id_prefix_ends_with_separator(self):
        """ID_PREFIX should end with a separator character for easy concatenation."""
        from src.pages.cursor_usage._constants import ID_PREFIX

        assert ID_PREFIX.endswith("-")


class TestColumnMap:
    """COLUMN_MAP maps logical filter keys to DataFrame column names."""

    def test_column_map_exists(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP is not None

    def test_column_map_is_dict(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert isinstance(COLUMN_MAP, dict)

    def test_column_map_has_all_expected_keys(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        expected_keys = {"date", "model", "cost", "total_tokens", "user", "kind"}
        assert set(COLUMN_MAP.keys()) == expected_keys

    def test_column_map_date(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["date"] == "Date"

    def test_column_map_model(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["model"] == "Model"

    def test_column_map_cost(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["cost"] == "Cost"

    def test_column_map_total_tokens(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["total_tokens"] == "Total Tokens"

    def test_column_map_user(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["user"] == "User"

    def test_column_map_kind(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["kind"] == "Kind"

    def test_column_map_values_are_all_strings(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        for key, value in COLUMN_MAP.items():
            assert isinstance(value, str), f"COLUMN_MAP['{key}'] is not a string: {value}"

    def test_column_map_keys_are_all_strings(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        for key in COLUMN_MAP.keys():
            assert isinstance(key, str), f"COLUMN_MAP key is not a string: {key}"
