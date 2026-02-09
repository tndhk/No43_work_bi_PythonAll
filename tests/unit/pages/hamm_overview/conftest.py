"""Shared fixtures for hamm_overview test modules."""

import pandas as pd
import plotly.graph_objects as go
import pytest

import src.pages.hamm_overview._callbacks as cb_mod


@pytest.fixture()
def mock_dashboard_deps(monkeypatch):
    """Monkeypatch all external dependencies used by update_dashboard.

    This covers:
    - ParquetReader / resolve_dataset_id_for_dashboard
    - load_and_filter_data, build_volume_summary
    - All prepare_* / build_* data helpers
    - All chart / table builder functions
    - create_kpi_card
    """
    volume_summary = pd.DataFrame(
        {
            "Start Date": ["01-Jan-26"],
            "End Date": ["07-Jan-26"],
            "Completed": [2],
            "Invalid": [1],
            "VOLUME TOTAL": [3],
            "Prelim": [1],
            "ERV": [2],
            "_sort_start_dt": pd.to_datetime(["2026-01-01"]),
        }
    )

    # Infrastructure
    monkeypatch.setattr(cb_mod, "ParquetReader", lambda: object())
    monkeypatch.setattr(
        cb_mod, "resolve_dataset_id_for_dashboard", lambda: "hamm-dashboard"
    )

    # Data helpers
    monkeypatch.setattr(
        cb_mod,
        "load_and_filter_data",
        lambda *args, **kwargs: pd.DataFrame({"id": ["1"]}),
    )
    monkeypatch.setattr(
        cb_mod,
        "build_volume_summary",
        lambda *args, **kwargs: volume_summary,
    )
    monkeypatch.setattr(
        cb_mod,
        "prepare_task_display_df",
        lambda df: pd.DataFrame({"Task ID": ["1"]}),
    )
    monkeypatch.setattr(
        cb_mod,
        "prepare_language_display_df",
        lambda df: pd.DataFrame({"Task ID": ["1"]}),
    )
    monkeypatch.setattr(
        cb_mod,
        "build_issues_ratio",
        lambda df: pd.DataFrame({"error_type": ["User"], "count": [1]}),
    )
    monkeypatch.setattr(
        cb_mod,
        "build_intervention_by_screener",
        lambda df: pd.DataFrame(
            {"video_type_description": ["ERV"], "User": [1], "HAMM": [0]}
        ),
    )
    monkeypatch.setattr(
        cb_mod,
        "build_user_intervention_breakdown",
        lambda df: pd.DataFrame({"error_description": ["e"], "count": [1]}),
    )
    monkeypatch.setattr(
        cb_mod,
        "build_hamm_intervention_breakdown",
        lambda df: pd.DataFrame({"error_description": ["e"], "count": [1]}),
    )
    monkeypatch.setattr(
        cb_mod,
        "build_original_language_distribution",
        lambda df: pd.DataFrame(
            {"original_language": ["Japanese"], "count": [1]}
        ),
    )
    monkeypatch.setattr(
        cb_mod,
        "build_dialogue_by_content_type",
        lambda df: pd.DataFrame(
            {"content_type": ["ERV"], "Yes": [1], "No": [0]}
        ),
    )
    monkeypatch.setattr(
        cb_mod,
        "build_genre_distribution",
        lambda df: pd.DataFrame({"genre": ["Documentary"], "count": [1]}),
    )

    # Chart / table builders
    monkeypatch.setattr(
        cb_mod, "build_volume_table", lambda df: ("Volume Summary", "table")
    )
    monkeypatch.setattr(
        cb_mod, "build_volume_chart", lambda df: go.Figure()
    )
    monkeypatch.setattr(
        cb_mod,
        "build_task_table",
        lambda df: ("Task Details", "task_table"),
    )
    monkeypatch.setattr(
        cb_mod,
        "build_language_table",
        lambda df: ("Language Details", "lang_table"),
    )
    monkeypatch.setattr(
        cb_mod, "build_error_ratio_chart", lambda df: go.Figure()
    )
    monkeypatch.setattr(
        cb_mod, "build_error_by_screener_chart", lambda df: go.Figure()
    )
    monkeypatch.setattr(
        cb_mod, "build_user_breakdown_chart", lambda df: go.Figure()
    )
    monkeypatch.setattr(
        cb_mod, "build_hamm_breakdown_chart", lambda df: go.Figure()
    )
    monkeypatch.setattr(
        cb_mod, "build_original_language_chart", lambda df: go.Figure()
    )
    monkeypatch.setattr(
        cb_mod, "build_dialogue_chart", lambda df: go.Figure()
    )
    monkeypatch.setattr(
        cb_mod, "build_genre_chart", lambda df: go.Figure()
    )

    # KPI
    monkeypatch.setattr(
        cb_mod, "create_kpi_card", lambda *args, **kwargs: "kpi"
    )

    return cb_mod
