"""Tests for Hamm Overview data loader module."""
import pandas as pd
from unittest.mock import MagicMock, patch


def _make_sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "id": ["1", "2"],
        "title": ["A", "B"],
        "status": ["Completed", "Completed"],
        "created_at": pd.to_datetime(["2026-01-05 10:00:00", "2026-02-10 12:00:00"], utc=True),
        "completed_at": pd.to_datetime(["2026-01-06 10:00:00", "2026-02-12 12:00:00"], utc=True),
        "notification_company_name": ["APAC", "APAC"],
        "video_type_description": ["Prelim", "ERV"],
        "original_language_name": ["Japanese", "Korean"],
        "was dialogue provided?": ["Yes", "No"],
        "genre_name": ["Crime", "Drama"],
        "error code": ["E1", "E2"],
        "error user vs system": ["User", "System"],
        "video_duration": ["00:10:00", "00:20:00"],
        "audio location": ["Full mix", "Separate audio"],
    })


@patch("src.pages.hamm_overview._data_loader.get_cached_dataset")
def test_load_filter_options_returns_expected_keys(mock_cache):
    from src.pages.hamm_overview._data_loader import load_filter_options

    mock_cache.return_value = _make_sample_df()
    reader = MagicMock()

    result = load_filter_options(reader, "hamm-dashboard")

    expected = {
        "regions",
        "years",
        "months",
        "task_ids",
        "content_types",
        "original_languages",
        "dialogue_options",
        "genres",
        "error_codes",
        "error_types",
    }
    assert set(result.keys()) == expected


@patch("src.pages.hamm_overview._data_loader.get_cached_dataset")
def test_load_and_filter_data_filters_by_region_and_year(mock_cache):
    from src.pages.hamm_overview._data_loader import load_and_filter_data, FILTER_COLUMN_MAP

    mock_cache.return_value = _make_sample_df()
    reader = MagicMock()

    df = load_and_filter_data(
        reader,
        "hamm-dashboard",
        FILTER_COLUMN_MAP,
        regions=["APAC"],
        years=["2026"],
    )

    assert len(df) == 2
    assert set(df["_year"].unique()) == {"2026"}


@patch("src.pages.hamm_overview._data_loader.get_cached_dataset")
def test_add_cadence_columns_weekly_has_start_end(mock_cache):
    from src.pages.hamm_overview._data_loader import add_cadence_columns

    df = _make_sample_df()
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    result = add_cadence_columns(df, "weekly")

    assert "_start_date" in result.columns
    assert "_end_date" in result.columns


def test_add_cadence_columns_weekly_monday_start():
    """TC-W-01: Monday (weekday=0) should be week start."""
    from src.pages.hamm_overview._data_loader import add_cadence_columns

    # Given: 2026-01-26 is Monday (weekday=0)
    df = pd.DataFrame({
        "created_at": pd.to_datetime(["2026-01-26 10:00:00"], utc=True),
    })

    # When: add weekly cadence columns
    result = add_cadence_columns(df, "weekly")

    # Then: Start Date = 26-Jan-26 (Monday), End Date = 01-Feb-26 (Sunday)
    assert result["_start_date"].iloc[0] == "26-Jan-26"
    assert result["_end_date"].iloc[0] == "01-Feb-26"
    assert result["_iso_week"].iloc[0] == "05"


def test_add_cadence_columns_weekly_sunday_end():
    """TC-W-02: Sunday (weekday=6) should be week end."""
    from src.pages.hamm_overview._data_loader import add_cadence_columns

    # Given: 2026-02-01 is Sunday (weekday=6)
    df = pd.DataFrame({
        "created_at": pd.to_datetime(["2026-02-01 10:00:00"], utc=True),
    })

    # When: add weekly cadence columns
    result = add_cadence_columns(df, "weekly")

    # Then: Start Date = 26-Jan-26 (Monday), End Date = 01-Feb-26 (Sunday)
    assert result["_start_date"].iloc[0] == "26-Jan-26"
    assert result["_end_date"].iloc[0] == "01-Feb-26"
    assert result["_iso_week"].iloc[0] == "05"


def test_add_cadence_columns_weekly_wednesday_midweek():
    """TC-W-03: Wednesday (weekday=2) should have correct week range."""
    from src.pages.hamm_overview._data_loader import add_cadence_columns

    # Given: 2026-02-04 is Wednesday (weekday=2)
    df = pd.DataFrame({
        "created_at": pd.to_datetime(["2026-02-04 10:00:00"], utc=True),
    })

    # When: add weekly cadence columns
    result = add_cadence_columns(df, "weekly")

    # Then: Start Date = 02-Feb-26 (Monday), End Date = 08-Feb-26 (Sunday)
    assert result["_start_date"].iloc[0] == "02-Feb-26"
    assert result["_end_date"].iloc[0] == "08-Feb-26"
    assert result["_iso_week"].iloc[0] == "06"


def test_add_cadence_columns_weekly_saturday():
    """TC-W-04: Saturday (weekday=5) should have correct week range."""
    from src.pages.hamm_overview._data_loader import add_cadence_columns

    # Given: 2026-01-25 is Saturday (weekday=5), ISO Week 04
    df = pd.DataFrame({
        "created_at": pd.to_datetime(["2026-01-25 10:00:00"], utc=True),
    })

    # When: add weekly cadence columns
    result = add_cadence_columns(df, "weekly")

    # Then: Start Date = 19-Jan-26 (Monday), End Date = 25-Jan-26 (Sunday)
    assert result["_start_date"].iloc[0] == "19-Jan-26"
    assert result["_end_date"].iloc[0] == "25-Jan-26"
    assert result["_iso_week"].iloc[0] == "04"


def test_add_cadence_columns_weekly_same_iso_week_same_dates():
    """Same ISO week should have identical Start/End Dates regardless of weekday."""
    from src.pages.hamm_overview._data_loader import add_cadence_columns

    # Given: Multiple dates in ISO Week 05 (2026-01-26 Mon to 2026-02-01 Sun)
    df = pd.DataFrame({
        "created_at": pd.to_datetime([
            "2026-01-26 10:00:00",  # Monday
            "2026-01-28 10:00:00",  # Wednesday
            "2026-02-01 10:00:00",  # Sunday
        ], utc=True),
    })

    # When: add weekly cadence columns
    result = add_cadence_columns(df, "weekly")

    # Then: All rows should have same Start/End dates
    assert result["_start_date"].nunique() == 1
    assert result["_end_date"].nunique() == 1
    assert result["_start_date"].iloc[0] == "26-Jan-26"
    assert result["_end_date"].iloc[0] == "01-Feb-26"


def test_prepare_base_df_converts_video_duration_to_seconds():
    from src.pages.hamm_overview._data_loader import _prepare_base_df

    df = pd.DataFrame({
        "id": ["1", "2", "3"],
        "created_at": pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"], utc=True),
        "completed_at": pd.to_datetime(["2026-01-06", "2026-01-07", "2026-01-08"], utc=True),
        "video_duration": ["00:10:30", "01:05:15", "00:00:45"],
    })

    result = _prepare_base_df(df)

    assert "_video_duration_seconds" in result.columns
    assert result["_video_duration_seconds"].iloc[0] == 630.0  # 10*60 + 30
    assert result["_video_duration_seconds"].iloc[1] == 3915.0  # 1*3600 + 5*60 + 15
    assert result["_video_duration_seconds"].iloc[2] == 45.0


def test_prepare_base_df_handles_invalid_video_duration():
    from src.pages.hamm_overview._data_loader import _prepare_base_df

    df = pd.DataFrame({
        "id": ["1", "2"],
        "created_at": pd.to_datetime(["2026-01-05", "2026-01-06"], utc=True),
        "completed_at": pd.to_datetime(["2026-01-06", "2026-01-07"], utc=True),
        "video_duration": ["invalid", "00:10:00"],
    })

    result = _prepare_base_df(df)

    assert pd.isna(result["_video_duration_seconds"].iloc[0])
    assert result["_video_duration_seconds"].iloc[1] == 600.0


def test_prepare_base_df_preserves_original_video_duration():
    from src.pages.hamm_overview._data_loader import _prepare_base_df

    df = pd.DataFrame({
        "id": ["1"],
        "created_at": pd.to_datetime(["2026-01-05"], utc=True),
        "completed_at": pd.to_datetime(["2026-01-06"], utc=True),
        "video_duration": ["00:10:00"],
    })

    result = _prepare_base_df(df)

    assert "video_duration" in result.columns
    assert result["video_duration"].iloc[0] == "00:10:00"
