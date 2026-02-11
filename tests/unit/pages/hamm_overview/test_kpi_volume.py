"""Tests for Volume KPI value computation.

These tests verify that the KPI values (total_screens, total_erv,
total_prelim) are correctly computed from a filtered DataFrame based
on content_type column.

The computation logic is in ``compute_volume_kpis`` function in
``src/pages/hamm_overview/_callbacks.py``.
"""

import pandas as pd
import pytest

from src.pages.hamm_overview._constants import ERV_LABEL, PRELIM_LABEL, COLUMN_MAP
from src.pages.hamm_overview._custom_logic import compute_volume_kpis


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def filtered_df_basic() -> pd.DataFrame:
    """Basic filtered DataFrame with mixed content types and statuses."""
    content_type_col = COLUMN_MAP["content_type"]
    status_col = COLUMN_MAP["status"]
    id_col = COLUMN_MAP["id"]

    return pd.DataFrame(
        {
            id_col: ["1", "2", "3", "4", "5"],
            content_type_col: [PRELIM_LABEL, ERV_LABEL, PRELIM_LABEL, ERV_LABEL, PRELIM_LABEL],
            status_col: ["Completed", "Completed", "Invalid", "Completed", "Completed"],
        }
    )


@pytest.fixture()
def filtered_df_with_cancelled() -> pd.DataFrame:
    """DataFrame with Cancelled status (should be excluded from KPIs)."""
    content_type_col = COLUMN_MAP["content_type"]
    status_col = COLUMN_MAP["status"]
    id_col = COLUMN_MAP["id"]

    return pd.DataFrame(
        {
            id_col: ["1", "2", "3", "4"],
            content_type_col: [PRELIM_LABEL, ERV_LABEL, PRELIM_LABEL, ERV_LABEL],
            status_col: ["Completed", "Cancelled", "Completed", "Cancelled"],
        }
    )


@pytest.fixture()
def filtered_df_empty() -> pd.DataFrame:
    """Empty filtered DataFrame."""
    content_type_col = COLUMN_MAP["content_type"]
    status_col = COLUMN_MAP["status"]
    id_col = COLUMN_MAP["id"]

    return pd.DataFrame(columns=[id_col, content_type_col, status_col])


@pytest.fixture()
def filtered_df_single_type() -> pd.DataFrame:
    """DataFrame with only one content type."""
    content_type_col = COLUMN_MAP["content_type"]
    status_col = COLUMN_MAP["status"]
    id_col = COLUMN_MAP["id"]

    return pd.DataFrame(
        {
            id_col: ["1", "2", "3"],
            content_type_col: [PRELIM_LABEL, PRELIM_LABEL, PRELIM_LABEL],
            status_col: ["Completed", "Completed", "Invalid"],
        }
    )


# ---------------------------------------------------------------------------
# Tests: Return Structure
# ---------------------------------------------------------------------------

class TestComputeVolumeKpisReturnStructure:
    """Verify the return structure of compute_volume_kpis."""

    def test_returns_dict(self, filtered_df_basic):
        result = compute_volume_kpis(filtered_df_basic)
        assert isinstance(result, dict)

    def test_has_total_screens_key(self, filtered_df_basic):
        result = compute_volume_kpis(filtered_df_basic)
        assert "total_screens" in result

    def test_has_total_erv_key(self, filtered_df_basic):
        result = compute_volume_kpis(filtered_df_basic)
        assert "total_erv" in result

    def test_has_total_prelim_key(self, filtered_df_basic):
        result = compute_volume_kpis(filtered_df_basic)
        assert "total_prelim" in result


# ---------------------------------------------------------------------------
# Tests: Basic Computation
# ---------------------------------------------------------------------------

class TestComputeVolumeKpisBasic:
    """Test basic KPI computation logic."""

    def test_total_screens_excludes_cancelled(self, filtered_df_with_cancelled):
        result = compute_volume_kpis(filtered_df_with_cancelled)
        # 4 records total, 2 are Cancelled, so 2 non-cancelled
        assert result["total_screens"] == 2

    def test_total_erv_counts_erv_records(self, filtered_df_basic):
        result = compute_volume_kpis(filtered_df_basic)
        # 2 ERV records in basic fixture
        assert result["total_erv"] == 2

    def test_total_prelim_counts_prelim_records(self, filtered_df_basic):
        result = compute_volume_kpis(filtered_df_basic)
        # 3 Prelim records in basic fixture
        assert result["total_prelim"] == 3


# ---------------------------------------------------------------------------
# Tests: Empty DataFrame
# ---------------------------------------------------------------------------

class TestComputeVolumeKpisEmpty:
    """Test behavior with empty DataFrame."""

    def test_total_screens_zero(self, filtered_df_empty):
        result = compute_volume_kpis(filtered_df_empty)
        assert result["total_screens"] == 0

    def test_total_erv_zero(self, filtered_df_empty):
        result = compute_volume_kpis(filtered_df_empty)
        assert result["total_erv"] == 0

    def test_total_prelim_zero(self, filtered_df_empty):
        result = compute_volume_kpis(filtered_df_empty)
        assert result["total_prelim"] == 0


# ---------------------------------------------------------------------------
# Tests: Single Content Type
# ---------------------------------------------------------------------------

class TestComputeVolumeKpisSingleType:
    """Test with only one content type present."""

    def test_total_screens_all_records(self, filtered_df_single_type):
        result = compute_volume_kpis(filtered_df_single_type)
        # 3 Prelim records, all non-cancelled
        assert result["total_screens"] == 3

    def test_total_erv_zero_when_no_erv(self, filtered_df_single_type):
        result = compute_volume_kpis(filtered_df_single_type)
        # No ERV records
        assert result["total_erv"] == 0

    def test_total_prelim_all_records(self, filtered_df_single_type):
        result = compute_volume_kpis(filtered_df_single_type)
        # All 3 records are Prelim
        assert result["total_prelim"] == 3


# ---------------------------------------------------------------------------
# Tests: Cancelled Status Exclusion
# ---------------------------------------------------------------------------

class TestComputeVolumeKpisCancelledExclusion:
    """Verify that Cancelled status is properly excluded."""

    def test_cancelled_excluded_from_total_screens(self, filtered_df_with_cancelled):
        result = compute_volume_kpis(filtered_df_with_cancelled)
        # 4 records, 2 cancelled = 2 total
        assert result["total_screens"] == 2

    def test_cancelled_erv_excluded(self, filtered_df_with_cancelled):
        result = compute_volume_kpis(filtered_df_with_cancelled)
        # 2 ERV records, 1 is cancelled = 1 ERV (but cancelled is excluded first, so 0)
        # Wait, let me check the fixture: ERV records are at index 1 and 3
        # Index 1: ERV, Cancelled -> excluded
        # Index 3: ERV, Cancelled -> excluded
        # So 0 ERV records remain
        assert result["total_erv"] == 0

    def test_cancelled_prelim_not_excluded_if_completed(self, filtered_df_with_cancelled):
        result = compute_volume_kpis(filtered_df_with_cancelled)
        # 2 Prelim records (index 0 and 2), both Completed (not cancelled)
        assert result["total_prelim"] == 2


# ---------------------------------------------------------------------------
# Tests: Return Types
# ---------------------------------------------------------------------------

class TestComputeVolumeKpisReturnTypes:
    """Verify that returned values are proper numeric types."""

    def test_total_screens_is_int(self, filtered_df_basic):
        result = compute_volume_kpis(filtered_df_basic)
        assert isinstance(result["total_screens"], int)

    def test_total_erv_is_int(self, filtered_df_basic):
        result = compute_volume_kpis(filtered_df_basic)
        assert isinstance(result["total_erv"], int)

    def test_total_prelim_is_int(self, filtered_df_basic):
        result = compute_volume_kpis(filtered_df_basic)
        assert isinstance(result["total_prelim"], int)
