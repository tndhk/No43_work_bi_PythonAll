"""Tests for chat callbacks."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock

import pandas as pd
import pandas.testing as pdt


class _DummyApp:
    """Minimal Dash-like app for callback registration tests."""

    def __init__(self) -> None:
        self.callbacks = []

    def callback(self, *args, **kwargs):  # noqa: ANN002, ANN003
        def _decorator(func):
            self.callbacks.append(func)
            return func

        return _decorator


@dataclass
class _Parsed:
    text: str
    code: str | None


def test_load_filtered_dataframe_for_chat_cursor_uses_filter_state(monkeypatch):
    """Cursor page should reconstruct context DataFrame from active filters."""
    from src.components.chat_callbacks import _load_filtered_dataframe_for_chat

    raw_df = pd.DataFrame({"x": [1, 2, 3]})
    filtered_df = pd.DataFrame({"x": [2]})

    def _fake_get_cached_dataset(reader, dataset_id):
        return raw_df

    def _fake_resolve_dataset_id_for_dashboard():
        return "cursor-usage"

    captured = {}

    def _fake_load_and_filter_data(
        reader,
        dataset_id,
        start_date,
        end_date,
        model_values,
        user_values,
        kind_values,
    ):
        captured["dataset_id"] = dataset_id
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        captured["model_values"] = model_values
        captured["user_values"] = user_values
        captured["kind_values"] = kind_values
        return filtered_df

    monkeypatch.setattr(
        "src.core.cache.get_cached_dataset",
        _fake_get_cached_dataset,
    )
    monkeypatch.setattr(
        "src.pages.cursor_usage._data_loader.resolve_dataset_id_for_dashboard",
        _fake_resolve_dataset_id_for_dashboard,
    )
    monkeypatch.setattr(
        "src.pages.cursor_usage._data_loader.load_and_filter_data",
        _fake_load_and_filter_data,
    )

    result = _load_filtered_dataframe_for_chat(
        reader=MagicMock(),
        pathname="/cursor-usage",
        dataset_id="cursor-usage",
        cursor_filter_state={
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "model_values": ["gpt-4"],
            "user_values": ["alice"],
            "kind_values": ["chat"],
        },
        hamm_filter_state=None,
        apac_filter_state=None,
    )

    assert isinstance(result, tuple)
    pdt.assert_frame_equal(result[0], filtered_df)
    assert result[1] is True
    assert captured["dataset_id"] == "cursor-usage"
    assert captured["start_date"] == "2024-01-01"
    assert captured["end_date"] == "2024-01-31"
    assert captured["model_values"] == ["gpt-4"]
    assert captured["user_values"] == ["alice"]
    assert captured["kind_values"] == ["chat"]


def test_load_filtered_dataframe_for_chat_falls_back_to_raw_dataset(monkeypatch):
    """When page-specific filter load fails, fallback dataset should be used."""
    from src.components.chat_callbacks import _load_filtered_dataframe_for_chat

    raw_df = pd.DataFrame({"x": [1, 2, 3]})

    def _fake_get_cached_dataset(reader, dataset_id):
        return raw_df

    def _raise(*args, **kwargs):  # noqa: ANN002, ANN003
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "src.core.cache.get_cached_dataset",
        _fake_get_cached_dataset,
    )
    monkeypatch.setattr(
        "src.pages.cursor_usage._data_loader.load_and_filter_data",
        _raise,
    )

    result = _load_filtered_dataframe_for_chat(
        reader=MagicMock(),
        pathname="/cursor-usage",
        dataset_id="cursor-usage",
        cursor_filter_state={},
        hamm_filter_state=None,
        apac_filter_state=None,
    )

    assert isinstance(result, tuple)
    pdt.assert_frame_equal(result[0], raw_df)
    assert result[1] is False


def test_send_chat_message_builds_context_from_filtered_dataframe(monkeypatch):
    """Chat callback should build context from filtered DataFrame."""
    import src.components.chat_callbacks as cb

    app = _DummyApp()
    cb.register_chat_callbacks(app)
    send_chat_message = app.callbacks[1]

    filtered_df = pd.DataFrame({"value": [10, 20]})
    captured = {"context_df": None, "system_prompt": None}

    monkeypatch.setattr(cb.settings, "gemini_api_key", "dummy-key")
    monkeypatch.setattr(cb.settings, "gemini_model_name", "gemini-2.0-flash")
    monkeypatch.setattr(
        cb,
        "_resolve_dataset_for_page",
        lambda pathname: ("cursor-usage", "Cursor Usage"),
    )
    monkeypatch.setattr(
        cb,
        "_load_filtered_dataframe_for_chat",
        lambda **kwargs: (filtered_df, True),
    )

    def _fake_build_llm_context(df, dataset_name, **kwargs):
        captured["context_df"] = df
        captured["dashboard_context_kwarg"] = kwargs.get("dashboard_context")
        return f"context for {dataset_name}"

    monkeypatch.setattr(cb, "build_llm_context", _fake_build_llm_context)
    monkeypatch.setattr(
        cb,
        "build_system_prompt",
        lambda context_str: f"SP::{context_str}",
    )

    class _Client:
        def __init__(self, api_key, model_name):
            pass

        def send_message(self, user_message, history, system_prompt):
            captured["system_prompt"] = system_prompt
            return "assistant answer"

    monkeypatch.setattr(cb, "GeminiClient", _Client)
    monkeypatch.setattr(cb, "parse_response", lambda raw: _Parsed(text="ok", code=None))
    monkeypatch.setattr(
        "src.data.parquet_reader.ParquetReader",
        lambda: MagicMock(),
    )

    messages, history, cleared = send_chat_message(
        1,
        "集計して",
        [],
        [],
        "/cursor-usage",
        {},
        {},
        {},
    )

    pdt.assert_frame_equal(captured["context_df"], filtered_df)
    assert captured["system_prompt"] == "SP::context for Cursor Usage"
    assert isinstance(messages, list)
    assert isinstance(history, list)
    assert cleared == ""


def test_get_dashboard_context_hamm_page(monkeypatch):
    """HAMM overview page should return DashboardContext."""
    from src.components.chat_callbacks import _get_dashboard_context
    from src.llm.page_context import DashboardContext, KPIValue

    fake_ctx = DashboardContext(
        page_description="test",
        kpis=[KPIValue(name="Total", value="5", logic="logic")],
        active_filters={},
    )

    monkeypatch.setattr(
        "src.pages.hamm_overview._context_provider.build_hamm_dashboard_context",
        lambda df, filter_state: fake_ctx,
    )

    df = pd.DataFrame({"x": [1]})
    result = _get_dashboard_context(
        "/hamm-overview", df, hamm_filter_state={"filter_region_values": None}
    )
    assert result is not None
    assert isinstance(result, DashboardContext)
    assert result.kpis[0].name == "Total"


def test_get_dashboard_context_unknown_page():
    """Unknown page should return None."""
    from src.components.chat_callbacks import _get_dashboard_context

    df = pd.DataFrame({"x": [1]})
    result = _get_dashboard_context("/unknown-page", df)
    assert result is None


def test_get_dashboard_context_error_returns_none(monkeypatch):
    """On error, _get_dashboard_context should return None gracefully."""
    from src.components.chat_callbacks import _get_dashboard_context

    def _raise_on_call(df, filter_state):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "src.pages.hamm_overview._context_provider.build_hamm_dashboard_context",
        _raise_on_call,
    )

    df = pd.DataFrame({"x": [1]})
    result = _get_dashboard_context("/hamm-overview", df, hamm_filter_state={})
    assert result is None


def test_send_chat_message_fallback_no_dashboard_context(monkeypatch):
    """When filter load falls back to raw dataset, dashboard_context should be None."""
    import src.components.chat_callbacks as cb

    app = _DummyApp()
    cb.register_chat_callbacks(app)
    send_chat_message = app.callbacks[1]

    raw_df = pd.DataFrame({"value": [10, 20]})
    captured = {"dashboard_context_kwarg": "NOT_SET"}

    monkeypatch.setattr(cb.settings, "gemini_api_key", "dummy-key")
    monkeypatch.setattr(cb.settings, "gemini_model_name", "gemini-2.0-flash")
    monkeypatch.setattr(
        cb,
        "_resolve_dataset_for_page",
        lambda pathname: ("hamm-dashboard", "HAMM Overview"),
    )
    monkeypatch.setattr(
        cb,
        "_load_filtered_dataframe_for_chat",
        lambda **kwargs: (raw_df, False),
    )

    def _fake_build_llm_context(df, dataset_name, **kwargs):
        captured["dashboard_context_kwarg"] = kwargs.get("dashboard_context")
        return f"context for {dataset_name}"

    monkeypatch.setattr(cb, "build_llm_context", _fake_build_llm_context)
    monkeypatch.setattr(
        cb,
        "build_system_prompt",
        lambda context_str: f"SP::{context_str}",
    )

    class _Client:
        def __init__(self, api_key, model_name):
            pass

        def send_message(self, user_message, history, system_prompt):
            return "assistant answer"

    monkeypatch.setattr(cb, "GeminiClient", _Client)
    monkeypatch.setattr(cb, "parse_response", lambda raw: _Parsed(text="ok", code=None))
    monkeypatch.setattr(
        "src.data.parquet_reader.ParquetReader",
        lambda: MagicMock(),
    )

    messages, history, cleared = send_chat_message(
        1,
        "テスト質問",
        [],
        [],
        "/hamm-overview",
        {},
        {},
        {},
    )

    assert captured["dashboard_context_kwarg"] is None
