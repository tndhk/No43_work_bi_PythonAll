"""Tests for Hamm Overview data loader module."""
import numpy as np
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
        "error description": ["Requested audio track does not exist", "SRT file truncated"],
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
    """load_and_filter_data accepts filter_pairs list instead of named kwargs."""
    from src.pages.hamm_overview._data_loader import load_and_filter_data, FILTER_COLUMN_MAP

    mock_cache.return_value = _make_sample_df()
    reader = MagicMock()

    filter_pairs = [
        ("region", ["APAC"]),
        ("year", ["2026"]),
    ]
    df = load_and_filter_data(
        reader,
        "hamm-dashboard",
        FILTER_COLUMN_MAP,
        filter_pairs,
    )

    assert len(df) == 2
    assert set(df["_year"].unique()) == {"2026"}


@patch("src.pages.hamm_overview._data_loader.get_cached_dataset")
def test_load_and_filter_data_with_empty_filter_pairs(mock_cache):
    """Empty filter_pairs should return all rows (no filtering)."""
    from src.pages.hamm_overview._data_loader import load_and_filter_data, FILTER_COLUMN_MAP

    mock_cache.return_value = _make_sample_df()
    reader = MagicMock()

    df = load_and_filter_data(
        reader,
        "hamm-dashboard",
        FILTER_COLUMN_MAP,
        filter_pairs=[],
    )

    assert len(df) == 2


@patch("src.pages.hamm_overview._data_loader.get_cached_dataset")
def test_load_and_filter_data_none_values_in_filter_pairs(mock_cache):
    """filter_pairs with None values should be treated as no filter (skip)."""
    from src.pages.hamm_overview._data_loader import load_and_filter_data, FILTER_COLUMN_MAP

    mock_cache.return_value = _make_sample_df()
    reader = MagicMock()

    filter_pairs = [
        ("region", None),
        ("year", ["2026"]),
    ]
    df = load_and_filter_data(
        reader,
        "hamm-dashboard",
        FILTER_COLUMN_MAP,
        filter_pairs,
    )

    assert len(df) == 2
    assert set(df["_year"].unique()) == {"2026"}


@patch("src.pages.hamm_overview._data_loader.get_cached_dataset")
def test_load_and_filter_data_empty_list_values_in_filter_pairs(mock_cache):
    """filter_pairs with empty list values should be treated as no filter (skip)."""
    from src.pages.hamm_overview._data_loader import load_and_filter_data, FILTER_COLUMN_MAP

    mock_cache.return_value = _make_sample_df()
    reader = MagicMock()

    filter_pairs = [
        ("region", []),
        ("year", ["2026"]),
    ]
    df = load_and_filter_data(
        reader,
        "hamm-dashboard",
        FILTER_COLUMN_MAP,
        filter_pairs,
    )

    assert len(df) == 2


@patch("src.pages.hamm_overview._data_loader.get_cached_dataset")
def test_load_and_filter_data_multiple_filters(mock_cache):
    """Multiple filter_pairs should all be applied."""
    from src.pages.hamm_overview._data_loader import load_and_filter_data, FILTER_COLUMN_MAP

    mock_cache.return_value = _make_sample_df()
    reader = MagicMock()

    filter_pairs = [
        ("region", ["APAC"]),
        ("year", ["2026"]),
        ("content_type", ["Prelim"]),
    ]
    df = load_and_filter_data(
        reader,
        "hamm-dashboard",
        FILTER_COLUMN_MAP,
        filter_pairs,
    )

    # Only row 1 is Prelim (row 2 is ERV)
    assert len(df) == 1
    assert df["video_type_description"].iloc[0] == "Prelim"


@patch("src.pages.hamm_overview._data_loader.get_cached_dataset")
def test_load_and_filter_data_filter_narrows_results(mock_cache):
    """A filter that matches no rows should return empty DataFrame."""
    from src.pages.hamm_overview._data_loader import load_and_filter_data, FILTER_COLUMN_MAP

    mock_cache.return_value = _make_sample_df()
    reader = MagicMock()

    filter_pairs = [
        ("region", ["EMEA"]),  # No EMEA in sample data
    ]
    df = load_and_filter_data(
        reader,
        "hamm-dashboard",
        FILTER_COLUMN_MAP,
        filter_pairs,
    )

    assert len(df) == 0


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


# ---------------------------------------------------------------------------
# build_volume_summary tests (moved from _callbacks.py to _data_loader.py)
# ---------------------------------------------------------------------------

def _make_prepared_df() -> pd.DataFrame:
    """Create a DataFrame that has already been through _prepare_base_df.

    This means: timezone-naive datetimes, string id, derived _year/_month.
    """
    return pd.DataFrame({
        "id": ["1", "2", "3", "4"],
        "title": ["A", "B", "C", "D"],
        "status": ["Completed", "Completed", "Cancelled", "Completed"],
        "created_at": pd.to_datetime([
            "2026-01-05 10:00:00",
            "2026-01-06 12:00:00",
            "2026-01-07 14:00:00",
            "2026-01-08 09:00:00",
        ]),
        "completed_at": pd.to_datetime([
            "2026-01-06 10:00:00",
            "2026-01-07 12:00:00",
            "2026-01-08 14:00:00",
            "2026-01-09 09:00:00",
        ]),
        "notification_company_name": ["APAC", "APAC", "APAC", "APAC"],
        "video_type_description": ["Prelim", "ERV", "Prelim", "Prelim"],
        "original_language_name": ["Japanese", "Korean", "Japanese", "Korean"],
        "was dialogue provided?": ["Yes", "No", "Yes", "No"],
        "genre_name": ["Crime", "Drama", "Crime", "Drama"],
        "error code": ["E1", "E2", "E1", "E2"],
        "error user vs system": ["User", "System", "User", "System"],
        "error description": [
            "Requested audio track does not exist",
            "SRT file truncated",
            "File upload failed",
            "Network error",
        ],
        "video_duration": ["00:10:00", "00:20:00", "00:15:00", "00:25:00"],
        "audio location": ["Full mix", "Separate audio", "Full mix", "Separate audio"],
    })


# ---------------------------------------------------------------------------
# prepare_task_display_df tests
# ---------------------------------------------------------------------------

def _make_task_df() -> pd.DataFrame:
    """Create a DataFrame simulating post-_prepare_base_df data for task display.

    Timezone-naive datetimes, string id, has all COLUMN_MAP columns.
    """
    return pd.DataFrame({
        "id": ["300", "100", "200"],
        "title": ["Task C", "Task A", "Task B"],
        "status": ["Complete", "Complete", "Error"],
        "created_at": pd.to_datetime([
            "2025-06-01 10:00:00",
            "2025-06-01 10:00:00",
            "2025-06-01 10:00:00",
        ]),
        "completed_at": pd.to_datetime([
            "2025-06-01 12:30:00",
            "2025-06-01 12:30:00",
            "2025-06-01 12:30:00",
        ]),
        "notification_company_name": ["APAC", "APAC", "APAC"],
        "video_type_description": ["Prelim", "ERV", "Prelim"],
        "original_language_name": ["Japanese", "Korean", "Japanese"],
        "was dialogue provided?": ["Yes", "No", "Yes"],
        "genre_name": ["Crime", "Drama", "Crime"],
        "error code": ["E1", "E2", "E1"],
        "error user vs system": ["User", "System", "User"],
        "error description": [
            "Requested audio track does not exist",
            "SRT file truncated",
            "File upload failed",
        ],
        "video_duration": ["00:10:00", "00:20:00", "00:30:00"],
        "audio location": ["Full mix", "Separate audio", "Stereo"],
    })


class TestPrepareTaskDisplayDf:
    """prepare_task_display_df should transform raw data into display-ready DataFrame."""

    def test_importable_from_data_loader(self):
        """prepare_task_display_df must be importable from _data_loader."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        assert callable(prepare_task_display_df)

    def test_returns_dataframe(self):
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        assert isinstance(result, pd.DataFrame)

    def test_has_expected_columns(self):
        """Output should have exactly the display column names in TASK_TABLE_SPEC order."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        expected_cols = [
            "Task ID",
            "Task Name",
            "Content Type",
            "Task Status",
            "Source File Duration",
            "Audio Details",
            "Job Created",
            "Completed / Err",
            "Total Duration",
        ]
        assert list(result.columns) == expected_cols

    def test_job_created_format(self):
        """Job Created should be formatted as YYYY-MM-DD HH:MM."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        # All rows have created_at = 2025-06-01 10:00:00
        for val in result["Job Created"]:
            assert val == "2025-06-01 10:00"

    def test_completed_err_format(self):
        """Completed / Err should be formatted as YYYY-MM-DD HH:MM."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        # All rows have completed_at = 2025-06-01 12:30:00
        for val in result["Completed / Err"]:
            assert val == "2025-06-01 12:30"

    def test_total_duration_format(self):
        """Total Duration should be in HH:MM:SS format."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        # 2.5 hours = 02:30:00
        for val in result["Total Duration"]:
            assert val == "02:30:00"

    def test_total_duration_with_nat_completed(self):
        """When completed_at is NaT, Total Duration should be empty string."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = pd.DataFrame({
            "id": ["1001"],
            "title": ["Sample Task"],
            "status": ["In Progress"],
            "created_at": pd.to_datetime(["2025-06-01 10:00:00"]),
            "completed_at": [pd.NaT],
            "notification_company_name": ["APAC"],
            "video_type_description": ["Prelim"],
            "original_language_name": ["Japanese"],
            "was dialogue provided?": ["Yes"],
            "genre_name": ["Crime"],
            "error code": ["E1"],
            "error user vs system": ["User"],
            "error description": ["Requested audio track does not exist"],
            "video_duration": ["00:45:00"],
            "audio location": ["Stereo"],
        })
        result = prepare_task_display_df(df)
        assert result["Total Duration"].iloc[0] == ""

    def test_sorts_by_task_id_numerically(self):
        """Rows should be sorted by Task ID as numeric values (100, 200, 300)."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()  # IDs: 300, 100, 200 (unsorted)
        result = prepare_task_display_df(df)
        task_ids = result["Task ID"].tolist()
        assert task_ids == ["100", "200", "300"]

    def test_column_mapping_task_id(self):
        """Task ID should contain values from COLUMN_MAP['id'] column."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        assert set(result["Task ID"].tolist()) == {"100", "200", "300"}

    def test_column_mapping_task_name(self):
        """Task Name should contain values from COLUMN_MAP['title'] column."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        assert set(result["Task Name"].tolist()) == {"Task A", "Task B", "Task C"}

    def test_column_mapping_content_type(self):
        """Content Type should contain values from COLUMN_MAP['content_type'] column."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        assert set(result["Content Type"].tolist()) == {"Prelim", "ERV"}

    def test_column_mapping_task_status(self):
        """Task Status should contain values from COLUMN_MAP['status'] column."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        assert set(result["Task Status"].tolist()) == {"Complete", "Error"}

    def test_column_mapping_source_file_duration(self):
        """Source File Duration should contain values from COLUMN_MAP['video_duration']."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        assert set(result["Source File Duration"].tolist()) == {
            "00:10:00", "00:20:00", "00:30:00"
        }

    def test_column_mapping_audio_details(self):
        """Audio Details should contain values from COLUMN_MAP['audio_details']."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df()
        result = prepare_task_display_df(df)
        assert set(result["Audio Details"].tolist()) == {
            "Full mix", "Separate audio", "Stereo"
        }

    def test_empty_df_returns_empty_dataframe(self):
        """Empty input should return an empty DataFrame with expected columns."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = _make_task_df().head(0)
        result = prepare_task_display_df(df)
        assert len(result) == 0
        expected_cols = [
            "Task ID", "Task Name", "Content Type", "Task Status",
            "Source File Duration", "Audio Details",
            "Job Created", "Completed / Err", "Total Duration",
        ]
        assert list(result.columns) == expected_cols

    def test_total_duration_over_24_hours(self):
        """Total Duration should handle durations exceeding 24 hours."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = pd.DataFrame({
            "id": ["1"],
            "title": ["Long Task"],
            "status": ["Complete"],
            "created_at": pd.to_datetime(["2025-06-01 00:00:00"]),
            "completed_at": pd.to_datetime(["2025-06-02 02:15:30"]),
            "notification_company_name": ["APAC"],
            "video_type_description": ["Prelim"],
            "original_language_name": ["Japanese"],
            "was dialogue provided?": ["Yes"],
            "genre_name": ["Crime"],
            "error code": ["E1"],
            "error user vs system": ["User"],
            "video_duration": ["00:10:00"],
            "audio location": ["Stereo"],
        })
        result = prepare_task_display_df(df)
        # 1 day + 2 hours + 15 min + 30 sec = 26:15:30
        assert result["Total Duration"].iloc[0] == "26:15:30"

    def test_completed_err_nat_shows_nat_string(self):
        """When completed_at is NaT, Completed / Err should show NaT string."""
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = pd.DataFrame({
            "id": ["1001"],
            "title": ["Sample Task"],
            "status": ["In Progress"],
            "created_at": pd.to_datetime(["2025-06-01 10:00:00"]),
            "completed_at": [pd.NaT],
            "notification_company_name": ["APAC"],
            "video_type_description": ["Prelim"],
            "original_language_name": ["Japanese"],
            "was dialogue provided?": ["Yes"],
            "genre_name": ["Crime"],
            "error code": ["E1"],
            "error user vs system": ["User"],
            "error description": ["Requested audio track does not exist"],
            "video_duration": ["00:45:00"],
            "audio location": ["Stereo"],
        })
        result = prepare_task_display_df(df)
        # NaT.strftime returns NaN in pandas (not a string)
        assert pd.isna(result["Completed / Err"].iloc[0])


class TestBuildVolumeSummaryInDataLoader:
    """build_volume_summary should be importable from _data_loader and work correctly."""

    def test_importable_from_data_loader(self):
        """build_volume_summary must be importable from _data_loader."""
        from src.pages.hamm_overview._data_loader import build_volume_summary
        assert callable(build_volume_summary)

    def test_returns_dataframe(self):
        from src.pages.hamm_overview._data_loader import build_volume_summary
        df = _make_prepared_df()
        result = build_volume_summary(df, "weekly")
        assert isinstance(result, pd.DataFrame)

    def test_has_expected_columns(self):
        from src.pages.hamm_overview._data_loader import build_volume_summary
        df = _make_prepared_df()
        result = build_volume_summary(df, "weekly")
        expected_cols = {
            "Fiscal Year", "Fiscal Quarter", "ISO Week",
            "Start Date", "End Date", "Prelim", "ERV", "VOLUME TOTAL",
        }
        # _sort_start_dt is an internal column that may or may not be present
        result_cols = set(result.columns) - {"_sort_start_dt"}
        assert result_cols == expected_cols

    def test_excludes_cancelled_status(self):
        """Cancelled status rows should be excluded from volume summary."""
        from src.pages.hamm_overview._data_loader import build_volume_summary
        df = _make_prepared_df()
        result = build_volume_summary(df, "weekly")
        # We have 4 rows, 1 Cancelled. So 3 non-cancelled tasks should be counted.
        total = result["VOLUME TOTAL"].sum()
        assert total == 3  # IDs 1, 2, 4 (ID 3 is Cancelled)

    def test_volume_total_is_sum_of_prelim_and_erv(self):
        from src.pages.hamm_overview._data_loader import build_volume_summary
        df = _make_prepared_df()
        result = build_volume_summary(df, "weekly")
        for _, row in result.iterrows():
            assert row["VOLUME TOTAL"] == row["Prelim"] + row["ERV"]

    def test_sorted_by_start_date(self):
        from src.pages.hamm_overview._data_loader import build_volume_summary
        df = _make_prepared_df()
        result = build_volume_summary(df, "weekly")
        if "_sort_start_dt" in result.columns:
            sort_vals = result["_sort_start_dt"].dropna().tolist()
            assert sort_vals == sorted(sort_vals)

    def test_empty_df_returns_empty_result(self):
        from src.pages.hamm_overview._data_loader import build_volume_summary
        df = _make_prepared_df().head(0)
        result = build_volume_summary(df, "weekly")
        assert len(result) == 0


# ---------------------------------------------------------------------------
# Vectorization equivalence tests (Task #4)
# ---------------------------------------------------------------------------

def _make_cadence_test_df() -> pd.DataFrame:
    """Create a DataFrame with diverse dates for cadence column tests.

    Covers:
    - Each quarter (Q1-Q4) for quarterly logic
    - Different months for monthly logic
    - NaT values for null handling
    - Dates spanning multiple years
    """
    return pd.DataFrame({
        "created_at": pd.to_datetime([
            "2025-01-15 10:00:00",   # Q1 Jan
            "2025-03-31 23:59:59",   # Q1 Mar (end of quarter)
            "2025-04-01 00:00:00",   # Q2 Apr (start of quarter)
            "2025-06-15 12:00:00",   # Q2 Jun
            "2025-07-20 08:30:00",   # Q3 Jul
            "2025-09-30 18:00:00",   # Q3 Sep (end of quarter)
            "2025-10-05 09:00:00",   # Q4 Oct
            "2025-12-31 23:59:59",   # Q4 Dec (end of year)
            "2026-02-14 14:00:00",   # Q1 Feb (next year)
            pd.NaT,                  # NaT
        ]),
    })


class TestFormatStartDateMonthlyVectorized:
    """_format_start_date_monthly_vec should match scalar _format_start_date_monthly."""

    def test_normal_dates_match_scalar(self):
        from src.pages.hamm_overview._data_loader import (
            _format_start_date_monthly,
            _format_start_date_monthly_vec,
        )
        df = _make_cadence_test_df()
        series = df["created_at"]

        scalar_result = series.apply(_format_start_date_monthly)
        vec_result = _format_start_date_monthly_vec(series)

        pd.testing.assert_series_equal(
            vec_result, scalar_result, check_names=False,
        )

    def test_nat_returns_null_string(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_monthly_vec
        series = pd.Series([pd.NaT])
        result = _format_start_date_monthly_vec(series)
        assert result.iloc[0] == "Null"

    def test_format_example(self):
        """Jan 2025 should produce '1-Jan-25'."""
        from src.pages.hamm_overview._data_loader import _format_start_date_monthly_vec
        series = pd.Series(pd.to_datetime(["2025-01-15 10:00:00"]))
        result = _format_start_date_monthly_vec(series)
        assert result.iloc[0] == "1-Jan-25"

    def test_empty_series(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_monthly_vec
        series = pd.Series([], dtype="datetime64[ns]")
        result = _format_start_date_monthly_vec(series)
        assert len(result) == 0


class TestFormatStartDateQuarterlyVectorized:
    """_format_start_date_quarterly_vec should match scalar version."""

    def test_all_dates_match_scalar(self):
        from src.pages.hamm_overview._data_loader import (
            _format_start_date_quarterly,
            _format_start_date_quarterly_vec,
        )
        df = _make_cadence_test_df()
        series = df["created_at"]

        scalar_result = series.apply(_format_start_date_quarterly)
        vec_result = _format_start_date_quarterly_vec(series)

        pd.testing.assert_series_equal(
            vec_result, scalar_result, check_names=False,
        )

    def test_q1_returns_1_jan(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_quarterly_vec
        series = pd.Series(pd.to_datetime(["2025-02-15"]))
        result = _format_start_date_quarterly_vec(series)
        assert result.iloc[0] == "1-Jan-25"

    def test_q2_returns_1_apr(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_quarterly_vec
        series = pd.Series(pd.to_datetime(["2025-05-01"]))
        result = _format_start_date_quarterly_vec(series)
        assert result.iloc[0] == "1-Apr-25"

    def test_q3_returns_1_jul(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_quarterly_vec
        series = pd.Series(pd.to_datetime(["2025-08-20"]))
        result = _format_start_date_quarterly_vec(series)
        assert result.iloc[0] == "1-Jul-25"

    def test_q4_returns_1_oct(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_quarterly_vec
        series = pd.Series(pd.to_datetime(["2025-11-30"]))
        result = _format_start_date_quarterly_vec(series)
        assert result.iloc[0] == "1-Oct-25"

    def test_nat_returns_null_string(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_quarterly_vec
        series = pd.Series([pd.NaT])
        result = _format_start_date_quarterly_vec(series)
        assert result.iloc[0] == "Null"

    def test_empty_series(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_quarterly_vec
        series = pd.Series([], dtype="datetime64[ns]")
        result = _format_start_date_quarterly_vec(series)
        assert len(result) == 0


class TestFormatEndDateQuarterlyVectorized:
    """_format_end_date_quarterly_vec should match scalar version."""

    def test_all_dates_match_scalar(self):
        from src.pages.hamm_overview._data_loader import (
            _format_end_date_quarterly,
            _format_end_date_quarterly_vec,
        )
        df = _make_cadence_test_df()
        series = df["created_at"]

        scalar_result = series.apply(_format_end_date_quarterly)
        vec_result = _format_end_date_quarterly_vec(series)

        pd.testing.assert_series_equal(
            vec_result, scalar_result, check_names=False,
        )

    def test_q1_returns_31_mar(self):
        from src.pages.hamm_overview._data_loader import _format_end_date_quarterly_vec
        series = pd.Series(pd.to_datetime(["2025-02-15"]))
        result = _format_end_date_quarterly_vec(series)
        assert result.iloc[0] == "31-Mar-25"

    def test_q2_returns_30_jun(self):
        from src.pages.hamm_overview._data_loader import _format_end_date_quarterly_vec
        series = pd.Series(pd.to_datetime(["2025-05-01"]))
        result = _format_end_date_quarterly_vec(series)
        assert result.iloc[0] == "30-Jun-25"

    def test_q3_returns_30_sep(self):
        from src.pages.hamm_overview._data_loader import _format_end_date_quarterly_vec
        series = pd.Series(pd.to_datetime(["2025-08-20"]))
        result = _format_end_date_quarterly_vec(series)
        assert result.iloc[0] == "30-Sep-25"

    def test_q4_returns_31_dec(self):
        from src.pages.hamm_overview._data_loader import _format_end_date_quarterly_vec
        series = pd.Series(pd.to_datetime(["2025-11-30"]))
        result = _format_end_date_quarterly_vec(series)
        assert result.iloc[0] == "31-Dec-25"

    def test_nat_returns_null_string(self):
        from src.pages.hamm_overview._data_loader import _format_end_date_quarterly_vec
        series = pd.Series([pd.NaT])
        result = _format_end_date_quarterly_vec(series)
        assert result.iloc[0] == "Null"


class TestFormatStartDateYearlyVectorized:
    """_format_start_date_yearly_vec should match scalar version."""

    def test_all_dates_match_scalar(self):
        from src.pages.hamm_overview._data_loader import (
            _format_start_date_yearly,
            _format_start_date_yearly_vec,
        )
        df = _make_cadence_test_df()
        series = df["created_at"]

        scalar_result = series.apply(_format_start_date_yearly)
        vec_result = _format_start_date_yearly_vec(series)

        pd.testing.assert_series_equal(
            vec_result, scalar_result, check_names=False,
        )

    def test_format_example(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_yearly_vec
        series = pd.Series(pd.to_datetime(["2025-06-15"]))
        result = _format_start_date_yearly_vec(series)
        assert result.iloc[0] == "1-Jan-25"

    def test_nat_returns_null_string(self):
        from src.pages.hamm_overview._data_loader import _format_start_date_yearly_vec
        series = pd.Series([pd.NaT])
        result = _format_start_date_yearly_vec(series)
        assert result.iloc[0] == "Null"


class TestFormatEndDateYearlyVectorized:
    """_format_end_date_yearly_vec should match scalar version."""

    def test_all_dates_match_scalar(self):
        from src.pages.hamm_overview._data_loader import (
            _format_end_date_yearly,
            _format_end_date_yearly_vec,
        )
        df = _make_cadence_test_df()
        series = df["created_at"]

        scalar_result = series.apply(_format_end_date_yearly)
        vec_result = _format_end_date_yearly_vec(series)

        pd.testing.assert_series_equal(
            vec_result, scalar_result, check_names=False,
        )

    def test_format_example(self):
        from src.pages.hamm_overview._data_loader import _format_end_date_yearly_vec
        series = pd.Series(pd.to_datetime(["2025-06-15"]))
        result = _format_end_date_yearly_vec(series)
        assert result.iloc[0] == "31-Dec-25"

    def test_nat_returns_null_string(self):
        from src.pages.hamm_overview._data_loader import _format_end_date_yearly_vec
        series = pd.Series([pd.NaT])
        result = _format_end_date_yearly_vec(series)
        assert result.iloc[0] == "Null"


class TestTotalDurationVectorized:
    """_compute_total_duration_vec should match the .apply(lambda) approach."""

    def test_normal_durations(self):
        from src.pages.hamm_overview._data_loader import _compute_total_duration_vec
        created = pd.Series(pd.to_datetime([
            "2025-06-01 10:00:00",
            "2025-06-01 00:00:00",
            "2025-06-01 08:00:00",
        ]))
        completed = pd.Series(pd.to_datetime([
            "2025-06-01 12:30:00",   # 2h 30m
            "2025-06-02 02:15:30",   # 26h 15m 30s
            "2025-06-01 08:00:45",   # 0h 0m 45s
        ]))
        result = _compute_total_duration_vec(created, completed)
        assert result.iloc[0] == "02:30:00"
        assert result.iloc[1] == "26:15:30"
        assert result.iloc[2] == "00:00:45"

    def test_nat_completed_returns_empty_string(self):
        from src.pages.hamm_overview._data_loader import _compute_total_duration_vec
        created = pd.Series(pd.to_datetime(["2025-06-01 10:00:00"]))
        completed = pd.Series([pd.NaT])
        result = _compute_total_duration_vec(created, completed)
        assert result.iloc[0] == ""

    def test_zero_duration(self):
        from src.pages.hamm_overview._data_loader import _compute_total_duration_vec
        ts = pd.to_datetime("2025-06-01 10:00:00")
        created = pd.Series([ts])
        completed = pd.Series([ts])
        result = _compute_total_duration_vec(created, completed)
        assert result.iloc[0] == "00:00:00"

    def test_empty_series(self):
        from src.pages.hamm_overview._data_loader import _compute_total_duration_vec
        created = pd.Series([], dtype="datetime64[ns]")
        completed = pd.Series([], dtype="datetime64[ns]")
        result = _compute_total_duration_vec(created, completed)
        assert len(result) == 0

    def test_mixed_nat_and_valid(self):
        """Mix of valid and NaT completed_at values."""
        from src.pages.hamm_overview._data_loader import _compute_total_duration_vec
        created = pd.Series(pd.to_datetime([
            "2025-06-01 10:00:00",
            "2025-06-01 10:00:00",
            "2025-06-01 10:00:00",
        ]))
        completed = pd.Series(pd.to_datetime([
            "2025-06-01 12:30:00",
            pd.NaT,
            "2025-06-01 11:00:00",
        ]))
        result = _compute_total_duration_vec(created, completed)
        assert result.iloc[0] == "02:30:00"
        assert result.iloc[1] == ""
        assert result.iloc[2] == "01:00:00"

    def test_multi_day_duration(self):
        """Duration spanning multiple days."""
        from src.pages.hamm_overview._data_loader import _compute_total_duration_vec
        created = pd.Series(pd.to_datetime(["2025-06-01 00:00:00"]))
        completed = pd.Series(pd.to_datetime(["2025-06-04 03:45:15"]))
        result = _compute_total_duration_vec(created, completed)
        # 3 days + 3h 45m 15s = 75:45:15
        assert result.iloc[0] == "75:45:15"


class TestAddCadenceColumnsVectorizedEquivalence:
    """add_cadence_columns output should be identical after vectorization.

    These tests capture the exact output of the current (scalar .apply)
    implementation so we can verify the vectorized version is equivalent.
    """

    def test_monthly_start_date_values(self):
        from src.pages.hamm_overview._data_loader import add_cadence_columns
        df = _make_cadence_test_df()
        result = add_cadence_columns(df, "monthly")

        # Expected: "1-Mon-YY" for valid dates, "Null" for NaT
        expected_start = [
            "1-Jan-25", "1-Mar-25", "1-Apr-25", "1-Jun-25",
            "1-Jul-25", "1-Sep-25", "1-Oct-25", "1-Dec-25",
            "1-Feb-26", "Null",
        ]
        assert result["_start_date"].tolist() == expected_start

    def test_monthly_end_date_is_last_day_of_month(self):
        from src.pages.hamm_overview._data_loader import add_cadence_columns
        df = _make_cadence_test_df()
        result = add_cadence_columns(df, "monthly")

        # End date should be last day of the month formatted as dd-Mon-yy
        expected_end = [
            "31-Jan-25", "31-Mar-25", "30-Apr-25", "30-Jun-25",
            "31-Jul-25", "30-Sep-25", "31-Oct-25", "31-Dec-25",
            "28-Feb-26", "Null",
        ]
        assert result["_end_date"].tolist() == expected_end

    def test_quarterly_start_date_values(self):
        from src.pages.hamm_overview._data_loader import add_cadence_columns
        df = _make_cadence_test_df()
        result = add_cadence_columns(df, "quarterly")

        expected_start = [
            "1-Jan-25", "1-Jan-25", "1-Apr-25", "1-Apr-25",
            "1-Jul-25", "1-Jul-25", "1-Oct-25", "1-Oct-25",
            "1-Jan-26", "Null",
        ]
        assert result["_start_date"].tolist() == expected_start

    def test_quarterly_end_date_values(self):
        from src.pages.hamm_overview._data_loader import add_cadence_columns
        df = _make_cadence_test_df()
        result = add_cadence_columns(df, "quarterly")

        expected_end = [
            "31-Mar-25", "31-Mar-25", "30-Jun-25", "30-Jun-25",
            "30-Sep-25", "30-Sep-25", "31-Dec-25", "31-Dec-25",
            "31-Mar-26", "Null",
        ]
        assert result["_end_date"].tolist() == expected_end

    def test_yearly_start_date_values(self):
        from src.pages.hamm_overview._data_loader import add_cadence_columns
        df = _make_cadence_test_df()
        result = add_cadence_columns(df, "yearly")

        expected_start = [
            "1-Jan-25", "1-Jan-25", "1-Jan-25", "1-Jan-25",
            "1-Jan-25", "1-Jan-25", "1-Jan-25", "1-Jan-25",
            "1-Jan-26", "Null",
        ]
        assert result["_start_date"].tolist() == expected_start

    def test_yearly_end_date_values(self):
        from src.pages.hamm_overview._data_loader import add_cadence_columns
        df = _make_cadence_test_df()
        result = add_cadence_columns(df, "yearly")

        expected_end = [
            "31-Dec-25", "31-Dec-25", "31-Dec-25", "31-Dec-25",
            "31-Dec-25", "31-Dec-25", "31-Dec-25", "31-Dec-25",
            "31-Dec-26", "Null",
        ]
        assert result["_end_date"].tolist() == expected_end

    def test_weekly_unchanged_by_vectorization(self):
        """Weekly cadence uses no .apply() so should remain identical."""
        from src.pages.hamm_overview._data_loader import add_cadence_columns
        df = _make_cadence_test_df()
        result = add_cadence_columns(df, "weekly")
        assert "_start_date" in result.columns
        assert "_end_date" in result.columns


class TestPrepareTaskDisplayDfTotalDurationVectorized:
    """Total Duration in prepare_task_display_df should be identical after vectorization."""

    def test_various_durations(self):
        from src.pages.hamm_overview._data_loader import prepare_task_display_df
        df = pd.DataFrame({
            "id": ["1", "2", "3", "4"],
            "title": ["A", "B", "C", "D"],
            "status": ["Done", "Done", "Done", "Pending"],
            "created_at": pd.to_datetime([
                "2025-06-01 10:00:00",
                "2025-06-01 00:00:00",
                "2025-06-01 08:00:00",
                "2025-06-01 10:00:00",
            ]),
            "completed_at": pd.to_datetime([
                "2025-06-01 12:30:00",   # 2h 30m
                "2025-06-02 02:15:30",   # 26h 15m 30s
                "2025-06-01 08:00:45",   # 0h 0m 45s
                pd.NaT,
            ]),
            "notification_company_name": ["APAC"] * 4,
            "video_type_description": ["Prelim"] * 4,
            "original_language_name": ["Japanese"] * 4,
            "was dialogue provided?": ["Yes"] * 4,
            "genre_name": ["Crime"] * 4,
            "error code": ["E1"] * 4,
            "error user vs system": ["User"] * 4,
            "error description": ["Requested audio track does not exist"] * 4,
            "video_duration": ["00:10:00"] * 4,
            "audio location": ["Stereo"] * 4,
        })
        result = prepare_task_display_df(df)
        # sorted by Task ID: 1, 2, 3, 4
        durations = result["Total Duration"].tolist()
        assert durations[0] == "02:30:00"
        assert durations[1] == "26:15:30"
        assert durations[2] == "00:00:45"
        assert durations[3] == ""


# ---------------------------------------------------------------------------
# Error Details aggregation function tests
# ---------------------------------------------------------------------------

def _make_error_analysis_df() -> pd.DataFrame:
    """Create a DataFrame for error analysis tests."""
    return pd.DataFrame({
        "id": ["1", "2", "3", "4", "5", "6"],
        "title": ["A", "B", "C", "D", "E", "F"],
        "status": ["Completed"] * 6,
        "created_at": pd.to_datetime([
            "2026-01-05 10:00:00",
            "2026-01-06 10:00:00",
            "2026-01-07 10:00:00",
            "2026-01-08 10:00:00",
            "2026-01-09 10:00:00",
            "2026-01-10 10:00:00",
        ]),
        "completed_at": pd.to_datetime([
            "2026-01-06 10:00:00",
            "2026-01-07 10:00:00",
            "2026-01-08 10:00:00",
            "2026-01-09 10:00:00",
            "2026-01-10 10:00:00",
            "2026-01-11 10:00:00",
        ]),
        "notification_company_name": ["APAC"] * 6,
        "video_type_description": ["Prelim", "ERV", "Prelim", "ERV", "Prelim", "ERV"],
        "original_language_name": ["Japanese"] * 6,
        "was dialogue provided?": ["Yes"] * 6,
        "genre_name": ["Crime"] * 6,
        "error code": ["E1", "E2", "E1", "E3", "E1", "E2"],
        "error user vs system": ["User", "HAMM", "User", "HAMM", "User", "HAMM"],
        "error description": [
            "Requested audio track does not exist",
            "SRT file truncated",
            "Requested audio track does not exist",
            "Network error",
            "File upload failed",
            "SRT file truncated",
        ],
        "video_duration": ["00:10:00"] * 6,
        "audio location": ["Full mix"] * 6,
    })


class TestBuildIssuesRatio:
    """build_issues_ratio should count User vs HAMM records."""

    def test_importable(self):
        from src.pages.hamm_overview._data_loader import build_issues_ratio
        assert callable(build_issues_ratio)

    def test_counts_user_and_hamm(self):
        from src.pages.hamm_overview._data_loader import build_issues_ratio, _prepare_base_df
        df = _make_error_analysis_df()
        df = _prepare_base_df(df)
        result = build_issues_ratio(df)
        
        assert len(result) == 2
        assert set(result["error_type"].tolist()) == {"User", "HAMM"}
        user_count = result[result["error_type"] == "User"]["count"].iloc[0]
        hamm_count = result[result["error_type"] == "HAMM"]["count"].iloc[0]
        assert user_count == 3
        assert hamm_count == 3

    def test_filters_out_non_user_hamm(self):
        from src.pages.hamm_overview._data_loader import build_issues_ratio, _prepare_base_df
        df = _make_error_analysis_df()
        df.loc[0, "error user vs system"] = "System"  # Change first to System
        df = _prepare_base_df(df)
        result = build_issues_ratio(df)
        
        # Should only have User and HAMM, not System
        assert len(result) == 2
        assert "System" not in result["error_type"].tolist()

    def test_empty_when_no_user_hamm(self):
        from src.pages.hamm_overview._data_loader import build_issues_ratio, _prepare_base_df
        df = _make_error_analysis_df()
        df["error user vs system"] = "System"  # All System
        df = _prepare_base_df(df)
        result = build_issues_ratio(df)
        
        assert len(result) == 0
        assert list(result.columns) == ["error_type", "count"]


class TestBuildInterventionByScreener:
    """build_intervention_by_screener should aggregate by screener type and error type."""

    def test_importable(self):
        from src.pages.hamm_overview._data_loader import build_intervention_by_screener
        assert callable(build_intervention_by_screener)

    def test_pivots_correctly(self):
        from src.pages.hamm_overview._data_loader import build_intervention_by_screener, _prepare_base_df
        df = _make_error_analysis_df()
        df = _prepare_base_df(df)
        result = build_intervention_by_screener(df)
        
        assert "video_type_description" in result.columns
        assert "User" in result.columns
        assert "HAMM" in result.columns
        
        # Prelim: 3 records (2 User, 1 HAMM)
        prelim_row = result[result["video_type_description"] == "Prelim"].iloc[0]
        assert prelim_row["User"] == 2
        assert prelim_row["HAMM"] == 1
        
        # ERV: 3 records (1 User, 2 HAMM)
        erv_row = result[result["video_type_description"] == "ERV"].iloc[0]
        assert erv_row["User"] == 1
        assert erv_row["HAMM"] == 2

    def test_empty_when_no_user_hamm(self):
        from src.pages.hamm_overview._data_loader import build_intervention_by_screener, _prepare_base_df
        df = _make_error_analysis_df()
        df["error user vs system"] = "System"  # All System
        df = _prepare_base_df(df)
        result = build_intervention_by_screener(df)
        
        assert len(result) == 0
        assert list(result.columns) == ["video_type_description", "User", "HAMM"]


class TestBuildUserInterventionBreakdown:
    """build_user_intervention_breakdown should filter User and group by error description."""

    def test_importable(self):
        from src.pages.hamm_overview._data_loader import build_user_intervention_breakdown
        assert callable(build_user_intervention_breakdown)

    def test_filters_to_user_only(self):
        from src.pages.hamm_overview._data_loader import build_user_intervention_breakdown, _prepare_base_df
        df = _make_error_analysis_df()
        df = _prepare_base_df(df)
        result = build_user_intervention_breakdown(df)
        
        assert "error_description" in result.columns
        assert "count" in result.columns
        
        # Should only have User errors (3 records)
        assert len(result) == 3
        assert result["count"].sum() == 3
        
        # Check specific error descriptions
        desc_counts = result.set_index("error_description")["count"].to_dict()
        assert desc_counts["Requested audio track does not exist"] == 2
        assert desc_counts["File upload failed"] == 1

    def test_sorted_by_count_descending(self):
        from src.pages.hamm_overview._data_loader import build_user_intervention_breakdown, _prepare_base_df
        df = _make_error_analysis_df()
        df = _prepare_base_df(df)
        result = build_user_intervention_breakdown(df)
        
        counts = result["count"].tolist()
        assert counts == sorted(counts, reverse=True)

    def test_empty_when_no_user(self):
        from src.pages.hamm_overview._data_loader import build_user_intervention_breakdown, _prepare_base_df
        df = _make_error_analysis_df()
        df["error user vs system"] = "HAMM"  # All HAMM
        df = _prepare_base_df(df)
        result = build_user_intervention_breakdown(df)
        
        assert len(result) == 0
        assert list(result.columns) == ["error_description", "count"]


class TestBuildHammInterventionBreakdown:
    """build_hamm_intervention_breakdown should filter HAMM and group by error description."""

    def test_importable(self):
        from src.pages.hamm_overview._data_loader import build_hamm_intervention_breakdown
        assert callable(build_hamm_intervention_breakdown)

    def test_filters_to_hamm_only(self):
        from src.pages.hamm_overview._data_loader import build_hamm_intervention_breakdown, _prepare_base_df
        df = _make_error_analysis_df()
        df = _prepare_base_df(df)
        result = build_hamm_intervention_breakdown(df)
        
        assert "error_description" in result.columns
        assert "count" in result.columns
        
        # Should only have HAMM errors (3 records)
        assert len(result) == 2  # 2 unique error descriptions
        assert result["count"].sum() == 3
        
        # Check specific error descriptions
        desc_counts = result.set_index("error_description")["count"].to_dict()
        assert desc_counts["SRT file truncated"] == 2
        assert desc_counts["Network error"] == 1

    def test_sorted_by_count_descending(self):
        from src.pages.hamm_overview._data_loader import build_hamm_intervention_breakdown, _prepare_base_df
        df = _make_error_analysis_df()
        df = _prepare_base_df(df)
        result = build_hamm_intervention_breakdown(df)
        
        counts = result["count"].tolist()
        assert counts == sorted(counts, reverse=True)

    def test_empty_when_no_hamm(self):
        from src.pages.hamm_overview._data_loader import build_hamm_intervention_breakdown, _prepare_base_df
        df = _make_error_analysis_df()
        df["error user vs system"] = "User"  # All User
        df = _prepare_base_df(df)
        result = build_hamm_intervention_breakdown(df)
        
        assert len(result) == 0
        assert list(result.columns) == ["error_description", "count"]
