"""Chat panel callbacks for LLM interaction."""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from dash import Input, Output, State, callback_context, dcc, html, no_update

from src.data.config import settings
from src.llm.client import GeminiClient
from src.llm.context_builder import build_llm_context
from src.llm.exceptions import LLMError, SandboxError, SandboxTimeoutError
from src.llm.page_context import DashboardContext
from src.llm.prompt_templates import build_system_prompt
from src.llm.response_parser import parse_response
from src.llm.sandbox import execute_in_sandbox

logger = logging.getLogger(__name__)

# URL pathname -> (dashboard_id, dataset_id, display_name) mapping
PAGE_DATASET_MAP: dict[str, tuple[str, str, str]] = {
    "/hamm-overview": ("hamm_overview", "hamm-dashboard", "HAMM Overview"),
    "/cursor-usage": ("cursor_usage", "cursor-usage", "Cursor Usage"),
    "/apac-dot-due-date": (
        "apac_dot_due_date",
        "apac-dot-due-date",
        "APAC DOT Due Date",
    ),
}


def _resolve_dataset_for_page(
    pathname: str | None,
) -> tuple[str, str] | None:
    """Resolve dataset_id and display name from URL pathname.

    Args:
        pathname: Current URL pathname.

    Returns:
        Tuple of (dataset_id, display_name), or None if page not mapped.
    """
    if pathname is None:
        return None
    # Strip trailing slash
    clean = pathname.rstrip("/")
    entry = PAGE_DATASET_MAP.get(clean)
    if entry is None:
        return None
    return (entry[1], entry[2])


def _build_message_bubble(role: str, content: str) -> html.Div:
    """Create a message bubble Div.

    Args:
        role: "user" or "assistant".
        content: Message text.

    Returns:
        Styled Div for the message.
    """
    css_class = f"chat-message chat-message-{role}"
    return html.Div(content, className=css_class)


def _build_assistant_message(content: str) -> html.Div:
    """Create an assistant message bubble with Markdown rendering.

    Uses dcc.Markdown to render tables, headings, lists, code blocks,
    and other Markdown formatting in assistant responses.

    Args:
        content: Markdown-formatted message text.

    Returns:
        Styled Div containing a dcc.Markdown component.
    """
    return html.Div(
        dcc.Markdown(
            content,
            className="chat-markdown-content",
            highlight_config={"theme": "dark"},
            link_target="_blank",
        ),
        className="chat-message chat-message-assistant",
    )


def _build_code_block(code: str) -> html.Div:
    """Create a code block Div.

    Args:
        code: Python code string.

    Returns:
        Styled Div for the code block.
    """
    return html.Div(
        html.Pre(code),
        className="chat-code-block",
    )


def _build_code_result(
    result_str: str, *, is_error: bool = False
) -> html.Div:
    """Create a code execution result Div.

    Args:
        result_str: String representation of the result.
        is_error: Whether this is an error result.

    Returns:
        Styled Div for the code result.
    """
    css = "chat-code-result"
    if is_error:
        css += " chat-code-error"
    return html.Div(
        html.Pre(result_str),
        className=css,
    )


def _coerce_single_value(value: Any, default: str) -> str:
    """Normalize a single-select callback value."""
    if isinstance(value, list):
        return value[0] if value else default
    if value is None:
        return default
    return value


def _load_filtered_dataframe_for_chat(
    reader: Any,
    pathname: str | None,
    dataset_id: str,
    cursor_filter_state: dict[str, Any] | None,
    hamm_filter_state: dict[str, Any] | None,
    apac_filter_state: dict[str, Any] | None,
) -> tuple[pd.DataFrame, bool]:
    """Load filtered DataFrame matching the currently visible dashboard state."""
    from src.core.cache import get_cached_dataset

    clean_path = (pathname or "").rstrip("/")

    if clean_path == "/cursor-usage":
        try:
            from src.pages.cursor_usage._data_loader import (
                load_and_filter_data,
                resolve_dataset_id_for_dashboard,
            )

            state = cursor_filter_state or {}
            resolved_dataset_id = resolve_dataset_id_for_dashboard()
            return (load_and_filter_data(
                reader=reader,
                dataset_id=resolved_dataset_id,
                start_date=state.get("start_date"),
                end_date=state.get("end_date"),
                model_values=state.get("model_values"),
                user_values=state.get("user_values"),
                kind_values=state.get("kind_values"),
            ), True)
        except Exception as e:
            logger.warning("Cursor filter-state load failed, fallback to raw dataset: %s", e)

    if clean_path == "/hamm-overview":
        try:
            from src.pages.hamm_overview._data_loader import (
                FILTER_COLUMN_MAP,
                load_and_filter_data,
                resolve_dataset_id_for_dashboard,
            )

            state = hamm_filter_state or {}
            filter_pairs = [
                ("region", state.get("filter_region_values")),
                ("year", state.get("filter_year_values")),
                ("content_type", state.get("filter_content_type_values")),
                ("original_language", state.get("filter_original_language_values")),
                ("dialogue", state.get("filter_dialogue_values")),
                ("genre", state.get("filter_genre_values")),
                ("error_type", state.get("filter_error_type_values")),
                ("month", state.get("filter_month_values")),
                ("id", state.get("filter_task_id_values")),
                ("error_code", state.get("filter_error_code_values")),
            ]
            resolved_dataset_id = resolve_dataset_id_for_dashboard()
            return (load_and_filter_data(
                reader=reader,
                dataset_id=resolved_dataset_id,
                column_map=FILTER_COLUMN_MAP,
                filter_pairs=filter_pairs,
            ), True)
        except Exception as e:
            logger.warning("HAMM filter-state load failed, fallback to raw dataset: %s", e)

    if clean_path == "/apac-dot-due-date":
        try:
            from src.data.data_source_registry import resolve_dataset_id
            from src.pages.apac_dot_due_date._constants import DASHBOARD_ID, DATASETS
            from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

            state = apac_filter_state or {}
            prc_value = _coerce_single_value(
                state.get("prc_filter_value"),
                "all",
            )
            resolved_dataset_id = resolve_dataset_id(
                DASHBOARD_ID,
                DATASETS["reference"].chart_id,
            )
            return (load_and_filter_data(
                reader=reader,
                dataset_id=resolved_dataset_id,
                column_map=DATASETS["reference"].column_map,
                selected_months=state.get("selected_months"),
                prc_filter_value=prc_value,
                area_values=state.get("area_values"),
                category_values=state.get("category_values"),
                vendor_values=state.get("vendor_values"),
                amp_av_values=state.get("amp_av_values"),
                order_type_values=None,
            ), True)
        except Exception as e:
            logger.warning("APAC filter-state load failed, fallback to raw dataset: %s", e)

    return (get_cached_dataset(reader, dataset_id), False)


def _get_dashboard_context(
    pathname: str | None,
    df: pd.DataFrame,
    hamm_filter_state: dict[str, Any] | None = None,
) -> DashboardContext | None:
    """Build page-specific DashboardContext for LLM chat.

    Uses lazy imports to avoid circular dependencies. Returns None
    for unsupported pages or on error (graceful fallback).
    """
    clean_path = (pathname or "").rstrip("/")

    if clean_path == "/hamm-overview":
        try:
            from src.pages.hamm_overview._context_provider import (
                build_hamm_dashboard_context,
            )

            return build_hamm_dashboard_context(df, hamm_filter_state)
        except Exception as e:
            logger.warning("Failed to build dashboard context for HAMM: %s", e)
            return None

    return None


def register_chat_callbacks(app: Any) -> None:
    """Register all chat panel callbacks.

    Args:
        app: Dash app instance.
    """

    # --- Callback 1: Toggle panel open/close ---
    @app.callback(
        Output("chat-panel", "className"),
        Output("page-content", "className"),
        Output("chat-panel-state", "data"),
        Input("chat-toggle-button", "n_clicks"),
        Input("chat-close-button", "n_clicks"),
        State("chat-panel-state", "data"),
        prevent_initial_call=True,
    )
    def toggle_chat_panel(
        toggle_clicks: int | None,
        close_clicks: int | None,
        is_open: bool,
    ) -> tuple[str, str, bool] | tuple[Any, Any, Any]:
        """Toggle chat panel visibility."""
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id == "chat-toggle-button":
            new_state = not is_open
        elif trigger_id == "chat-close-button":
            new_state = False
        else:
            return no_update, no_update, no_update

        panel_class = (
            "chat-panel chat-panel-open" if new_state else "chat-panel"
        )
        content_class = (
            "main-content main-content-with-chat"
            if new_state
            else "main-content"
        )

        return panel_class, content_class, new_state

    # --- Callback 2: Send message and get response ---
    @app.callback(
        Output("chat-messages", "children"),
        Output("chat-session-store", "data"),
        Output("chat-input", "value"),
        Input("chat-send-button", "n_clicks"),
        State("chat-input", "value"),
        State("chat-session-store", "data"),
        State("chat-messages", "children"),
        State("main-location", "pathname"),
        State("chat-filter-state-cursor", "data"),
        State("chat-filter-state-hamm", "data"),
        State("chat-filter-state-apac", "data"),
        prevent_initial_call=True,
    )
    def send_chat_message(
        n_clicks: int | None,
        user_input: str | None,
        history: list[dict[str, str]] | None,
        current_messages: list[Any] | None,
        pathname: str | None,
        cursor_filter_state: dict[str, Any] | None,
        hamm_filter_state: dict[str, Any] | None,
        apac_filter_state: dict[str, Any] | None,
    ) -> tuple[list[Any], list[dict[str, str]], str] | tuple[Any, Any, Any]:
        """Process user message, call LLM, and display response."""
        if not n_clicks or not user_input or not user_input.strip():
            return no_update, no_update, no_update

        user_msg = user_input.strip()

        # Initialize messages list
        if current_messages is None:
            current_messages = []

        # Add user message bubble
        current_messages.append(_build_message_bubble("user", user_msg))

        # Check API key
        if not settings.gemini_api_key:
            current_messages.append(
                _build_assistant_message(
                    "GEMINI_API_KEY が設定されていません。"
                    ".env ファイルに設定してください。",
                )
            )
            return current_messages, history or [], ""

        # Resolve dataset
        dataset_info = _resolve_dataset_for_page(pathname)

        # Build context (only if dataset is available)
        context_str = (
            "データが利用できません。一般的な質問にのみ回答できます。"
        )
        df = None
        if dataset_info:
            dataset_id, display_name = dataset_info
            try:
                from src.data.parquet_reader import ParquetReader

                reader = ParquetReader()
                df, used_page_filter = _load_filtered_dataframe_for_chat(
                    reader=reader,
                    pathname=pathname,
                    dataset_id=dataset_id,
                    cursor_filter_state=cursor_filter_state,
                    hamm_filter_state=hamm_filter_state,
                    apac_filter_state=apac_filter_state,
                )
                dashboard_ctx = None
                if used_page_filter:
                    dashboard_ctx = _get_dashboard_context(
                        pathname, df, hamm_filter_state=hamm_filter_state,
                    )
                context_str = build_llm_context(
                    df, display_name, dashboard_context=dashboard_ctx,
                )
            except Exception as e:
                logger.warning(
                    "Failed to load dataset for chat context: %s", e
                )
                context_str = f"データの読み込みに失敗しました: {e}"

        # Build system prompt
        system_prompt = build_system_prompt(context_str)

        # Update history
        history = history or []
        history.append({"role": "user", "content": user_msg})

        # Call LLM
        try:
            client = GeminiClient(
                api_key=settings.gemini_api_key,
                model_name=settings.gemini_model_name,
            )
            raw_response = client.send_message(
                user_message=user_msg,
                history=history[:-1],
                system_prompt=system_prompt,
            )
        except LLMError as e:
            logger.error("LLM API error: %s", e)
            error_msg = f"LLMエラー: {e}"
            current_messages.append(
                _build_assistant_message(error_msg)
            )
            return current_messages, history, ""

        # Parse response
        parsed = parse_response(raw_response)

        # Add assistant text
        if parsed.text:
            current_messages.append(
                _build_assistant_message(parsed.text)
            )

        # Handle code execution
        if parsed.code and df is not None:
            current_messages.append(_build_code_block(parsed.code))
            try:
                result = execute_in_sandbox(parsed.code, df)
                result_str = str(result)
                current_messages.append(_build_code_result(result_str))
            except SandboxTimeoutError:
                current_messages.append(
                    _build_code_result(
                        "コード実行がタイムアウトしました。",
                        is_error=True,
                    )
                )
            except SandboxError as e:
                current_messages.append(
                    _build_code_result(
                        f"コード実行エラー: {e}", is_error=True
                    )
                )
        elif parsed.code:
            # Code present but no df
            current_messages.append(_build_code_block(parsed.code))
            current_messages.append(
                _build_code_result(
                    "データが利用できないため、コードを実行できません。",
                    is_error=True,
                )
            )

        # Update history with assistant response
        history.append({"role": "assistant", "content": raw_response})

        return current_messages, history, ""
