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
    from src.pages.hamm_overview._data_loader import load_and_filter_data

    mock_cache.return_value = _make_sample_df()
    reader = MagicMock()

    df = load_and_filter_data(
        reader,
        "hamm-dashboard",
        regions=["APAC"],
        years=["2026"],
        months=[],
        task_ids=[],
        content_types=[],
        original_languages=[],
        dialogue_values=[],
        genres=[],
        error_codes=[],
        error_types=[],
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
