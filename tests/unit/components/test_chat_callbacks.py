"""Tests for chat callbacks."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock

import pandas as pd
import pandas.testing as pdt
from dash import dcc, html


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


class TestBuildAssistantMessage:
    """Tests for _build_assistant_message helper."""

    def test_build_assistant_message_returns_dcc_markdown(self):
        """assistant応答が dcc.Markdown を含むこと"""
        from src.components.chat_callbacks import _build_assistant_message

        result = _build_assistant_message("## 見出し\n\nテキスト")
        assert isinstance(result, html.Div)
        # The Div should contain a dcc.Markdown as its child
        children = result.children
        assert isinstance(children, dcc.Markdown)

    def test_build_assistant_message_highlight_config(self):
        """highlight_configが設定されていること"""
        from src.components.chat_callbacks import _build_assistant_message

        result = _build_assistant_message("```sql\nSELECT 1;\n```")
        md = result.children
        assert isinstance(md, dcc.Markdown)
        assert md.highlight_config is not None
        assert "theme" in md.highlight_config

    def test_build_assistant_message_link_target_blank(self):
        """link_targetが_blankであること"""
        from src.components.chat_callbacks import _build_assistant_message

        result = _build_assistant_message("https://example.com")
        md = result.children
        assert isinstance(md, dcc.Markdown)
        assert md.link_target == "_blank"

    def test_build_assistant_message_no_dangerous_html(self):
        """dangerously_allow_htmlがFalse/未設定であること"""
        from src.components.chat_callbacks import _build_assistant_message

        result = _build_assistant_message("<script>alert('xss')</script>")
        md = result.children
        assert isinstance(md, dcc.Markdown)
        # dangerously_allow_html should be falsy (default is False)
        assert not getattr(md, "dangerously_allow_html", False)

    def test_build_message_bubble_user_still_plain_div(self):
        """ユーザーメッセージは引き続き html.Div であること"""
        from src.components.chat_callbacks import _build_message_bubble

        result = _build_message_bubble("user", "ユーザーメッセージ")
        assert isinstance(result, html.Div)
        # User messages should be plain text, not dcc.Markdown
        assert result.children == "ユーザーメッセージ"
        assert "chat-message-user" in result.className


class TestSummarizeExecutionResult:
    """Tests for 2-pass LLM flow: code execution + summarization.

    When LLM generates code that executes successfully, a second LLM call
    summarizes the result into natural language. The summary is displayed
    prominently, with code/result in a collapsible section.
    """

    def test_summary_displayed_with_collapsible(self, monkeypatch):
        """コード実行成功時は要約テキスト + 折りたたみ（コード+結果）を表示"""
        # Given: LLM returns code that executes successfully
        # When: Code is executed and summarized
        # Then: Summary text + collapsible with code/result are displayed
        import src.components.chat_callbacks as cb

        app = _DummyApp()
        cb.register_chat_callbacks(app)
        send_chat_message = app.callbacks[1]

        test_df = pd.DataFrame({"language": ["Japanese", "Korean"], "count": [15, 9]})

        monkeypatch.setattr(cb.settings, "gemini_api_key", "dummy-key")
        monkeypatch.setattr(cb.settings, "gemini_model_name", "gemini-2.0-flash")
        monkeypatch.setattr(
            cb,
            "_resolve_dataset_for_page",
            lambda pathname: ("test-dataset", "Test Dataset"),
        )
        monkeypatch.setattr(
            cb,
            "_load_filtered_dataframe_for_chat",
            lambda **kwargs: (test_df, True),
        )
        monkeypatch.setattr(
            cb, "build_llm_context", lambda df, name, **kw: "context"
        )
        monkeypatch.setattr(
            cb, "build_system_prompt", lambda ctx: "system prompt"
        )

        class _Client:
            def __init__(self, api_key, model_name):
                pass

            def send_message(self, user_message, history, system_prompt):
                return "LLM response with code"

            def summarize_result(self, prompt):
                return "Japanese: 15件、Korean: 9件です。"

        monkeypatch.setattr(cb, "GeminiClient", _Client)
        monkeypatch.setattr(
            cb,
            "parse_response",
            lambda raw: _Parsed(
                text="Japanese: 11件\nKorean: 13件",  # Wrong numbers (ignored)
                code="result = df.groupby('language')['count'].sum()",
            ),
        )
        monkeypatch.setattr(
            cb,
            "execute_in_sandbox",
            lambda code, df: "Japanese    15\nKorean       9",
        )
        monkeypatch.setattr(
            "src.data.parquet_reader.ParquetReader",
            lambda: MagicMock(),
        )

        messages, history, cleared = send_chat_message(
            1,
            "言語別に集計して",
            [],
            [],
            "/test-page",
            {},
            {},
            {},
        )

        # Filter out user message
        assistant_messages = [
            m for m in messages
            if hasattr(m, "className") and "chat-message-user" not in m.className
        ]

        class_names = [getattr(m, "className", "") for m in assistant_messages]
        # Summary text should be displayed
        assert any("chat-message-assistant" in cn for cn in class_names)
        # Collapsible should be present
        assert any("chat-code-collapsible" in cn for cn in class_names)

    def test_fallback_to_original_text_on_summarization_failure(self, monkeypatch):
        """要約失敗時は元のテキスト + 折りたたみを表示"""
        # Given: LLM code executes but summarization fails
        # When: summarize_result raises LLMError
        # Then: Original text is displayed as fallback
        import src.components.chat_callbacks as cb
        from src.llm.exceptions import LLMError

        app = _DummyApp()
        cb.register_chat_callbacks(app)
        send_chat_message = app.callbacks[1]

        test_df = pd.DataFrame({"x": [1, 2, 3]})

        monkeypatch.setattr(cb.settings, "gemini_api_key", "dummy-key")
        monkeypatch.setattr(cb.settings, "gemini_model_name", "gemini-2.0-flash")
        monkeypatch.setattr(
            cb,
            "_resolve_dataset_for_page",
            lambda pathname: ("test-dataset", "Test Dataset"),
        )
        monkeypatch.setattr(
            cb,
            "_load_filtered_dataframe_for_chat",
            lambda **kwargs: (test_df, True),
        )
        monkeypatch.setattr(
            cb, "build_llm_context", lambda df, name, **kw: "context"
        )
        monkeypatch.setattr(
            cb, "build_system_prompt", lambda ctx: "system prompt"
        )

        class _Client:
            def __init__(self, api_key, model_name):
                pass

            def send_message(self, user_message, history, system_prompt):
                return "response"

            def summarize_result(self, prompt):
                raise LLMError("Summarization failed")

        monkeypatch.setattr(cb, "GeminiClient", _Client)
        monkeypatch.setattr(
            cb,
            "parse_response",
            lambda raw: _Parsed(
                text="フォールバックテキスト",
                code="result = df.sum()",
            ),
        )
        monkeypatch.setattr(
            cb,
            "execute_in_sandbox",
            lambda code, df: "6",
        )
        monkeypatch.setattr(
            "src.data.parquet_reader.ParquetReader",
            lambda: MagicMock(),
        )

        messages, history, cleared = send_chat_message(
            1,
            "合計して",
            [],
            [],
            "/test-page",
            {},
            {},
            {},
        )

        # Filter out user message
        assistant_messages = [
            m for m in messages
            if hasattr(m, "className") and "chat-message-user" not in m.className
        ]

        class_names = [getattr(m, "className", "") for m in assistant_messages]
        # Fallback text should be displayed
        assert any("chat-message-assistant" in cn for cn in class_names)
        # Collapsible should still be present
        assert any("chat-code-collapsible" in cn for cn in class_names)

    def test_text_shown_when_code_present_but_no_df(self, monkeypatch):
        """dfがない場合はコードがあってもテキストを表示する"""
        # Given: LLM returns text AND code
        # When: df is None (code cannot execute)
        # Then: Text IS displayed (along with code and error message)
        import src.components.chat_callbacks as cb

        app = _DummyApp()
        cb.register_chat_callbacks(app)
        send_chat_message = app.callbacks[1]

        monkeypatch.setattr(cb.settings, "gemini_api_key", "dummy-key")
        monkeypatch.setattr(cb.settings, "gemini_model_name", "gemini-2.0-flash")
        # Return None for dataset resolution (no df available)
        monkeypatch.setattr(
            cb,
            "_resolve_dataset_for_page",
            lambda pathname: None,
        )

        class _Client:
            def __init__(self, api_key, model_name):
                pass

            def send_message(self, user_message, history, system_prompt):
                return "response"

        monkeypatch.setattr(cb, "GeminiClient", _Client)
        monkeypatch.setattr(
            cb,
            "parse_response",
            lambda raw: _Parsed(
                text="説明テキスト",
                code="result = df.sum()",
            ),
        )

        messages, history, cleared = send_chat_message(
            1,
            "集計して",
            [],
            [],
            "/unknown-page",
            {},
            {},
            {},
        )

        # Filter out user message
        assistant_messages = [
            m for m in messages
            if hasattr(m, "className") and "chat-message-user" not in m.className
        ]

        class_names = [getattr(m, "className", "") for m in assistant_messages]
        # Text SHOULD be displayed since code won't execute
        assert any("chat-message-assistant" in cn for cn in class_names)
        # Code block should be shown
        assert any("chat-code-block" in cn for cn in class_names)
        # Error result should be shown
        assert any("chat-code-error" in cn for cn in class_names)

    def test_text_shown_when_no_code(self, monkeypatch):
        """コードがない場合はテキストを表示する"""
        # Given: LLM returns only text (no code)
        # When: Message is processed
        # Then: Text IS displayed
        import src.components.chat_callbacks as cb

        app = _DummyApp()
        cb.register_chat_callbacks(app)
        send_chat_message = app.callbacks[1]

        test_df = pd.DataFrame({"x": [1, 2, 3]})

        monkeypatch.setattr(cb.settings, "gemini_api_key", "dummy-key")
        monkeypatch.setattr(cb.settings, "gemini_model_name", "gemini-2.0-flash")
        monkeypatch.setattr(
            cb,
            "_resolve_dataset_for_page",
            lambda pathname: ("test-dataset", "Test Dataset"),
        )
        monkeypatch.setattr(
            cb,
            "_load_filtered_dataframe_for_chat",
            lambda **kwargs: (test_df, True),
        )
        monkeypatch.setattr(
            cb, "build_llm_context", lambda df, name, **kw: "context"
        )
        monkeypatch.setattr(
            cb, "build_system_prompt", lambda ctx: "system prompt"
        )

        class _Client:
            def __init__(self, api_key, model_name):
                pass

            def send_message(self, user_message, history, system_prompt):
                return "response"

        monkeypatch.setattr(cb, "GeminiClient", _Client)
        # LLM returns only text, no code
        monkeypatch.setattr(
            cb,
            "parse_response",
            lambda raw: _Parsed(text="これは説明テキストです", code=None),
        )
        monkeypatch.setattr(
            "src.data.parquet_reader.ParquetReader",
            lambda: MagicMock(),
        )

        messages, history, cleared = send_chat_message(
            1,
            "説明して",
            [],
            [],
            "/test-page",
            {},
            {},
            {},
        )

        # Filter out user message
        assistant_messages = [
            m for m in messages
            if hasattr(m, "className") and "chat-message-user" not in m.className
        ]

        class_names = [getattr(m, "className", "") for m in assistant_messages]
        # Text SHOULD be displayed
        assert any("chat-message-assistant" in cn for cn in class_names)
        # No code block
        assert not any("chat-code-block" in cn for cn in class_names)
        # No collapsible
        assert not any("chat-code-collapsible" in cn for cn in class_names)
