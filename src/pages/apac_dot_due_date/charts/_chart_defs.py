"""Load and validate chart definitions for APAC DOT Due Date tables."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_CHART_DEFS_PATH = Path(__file__).with_name("chart_defs.yaml")


class ChartDefsError(ValueError):
    """Raised when chart definition YAML is invalid."""


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ChartDefsError(f"{name} must be a mapping")
    return value


def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ChartDefsError(f"{name} must be a list")
    return value


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ChartDefsError(f"{name} must be a string")
    return value


def _validate_column_display(chart_id: str, mapping: dict[str, Any]) -> None:
    for key, value in mapping.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ChartDefsError(
                f"{chart_id}.column_display keys and values must be strings"
            )


def _validate_column_order(chart_id: str, order: list[Any]) -> None:
    for item in order:
        if not isinstance(item, str):
            raise ChartDefsError(
                f"{chart_id}.column_order items must be strings"
            )


def _validate_style_data_conditional(chart_id: str, items: list[Any]) -> None:
    for idx, rule in enumerate(items):
        if not isinstance(rule, dict):
            raise ChartDefsError(
                f"{chart_id}.table_style.style_data_conditional[{idx}] must be a mapping"
            )
        if "if" in rule:
            condition = rule["if"]
            if not isinstance(condition, dict):
                raise ChartDefsError(
                    f"{chart_id}.table_style.style_data_conditional[{idx}].if must be a mapping"
                )
            if "filter_query" in condition:
                _require_string(
                    condition["filter_query"],
                    (
                        f"{chart_id}.table_style.style_data_conditional"
                        f"[{idx}].if.filter_query"
                    ),
                )


def _validate_chart_def(chart_id: str, chart_def: dict[str, Any]) -> None:
    _require_string(chart_def.get("title"), f"{chart_id}.title")
    column_display = chart_def.get("column_display", {})
    _require_mapping(column_display, f"{chart_id}.column_display")
    _validate_column_display(chart_id, column_display)

    column_order = chart_def.get("column_order", [])
    _require_list(column_order, f"{chart_id}.column_order")
    _validate_column_order(chart_id, column_order)

    table_style = _require_mapping(chart_def.get("table_style"), f"{chart_id}.table_style")
    _require_mapping(table_style.get("style_table"), f"{chart_id}.table_style.style_table")
    _require_mapping(table_style.get("style_cell"), f"{chart_id}.table_style.style_cell")
    _require_mapping(table_style.get("style_header"), f"{chart_id}.table_style.style_header")
    style_data_conditional = _require_list(
        table_style.get("style_data_conditional"),
        f"{chart_id}.table_style.style_data_conditional",
    )
    _validate_style_data_conditional(chart_id, style_data_conditional)


@lru_cache(maxsize=1)
def load_chart_defs() -> dict[str, Any]:
    if not _CHART_DEFS_PATH.exists():
        raise ChartDefsError(f"chart_defs.yaml not found: {_CHART_DEFS_PATH}")

    with _CHART_DEFS_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        raise ChartDefsError("chart_defs.yaml is empty")

    root = _require_mapping(data, "chart_defs")
    charts = _require_mapping(root.get("charts"), "chart_defs.charts")

    for chart_id, chart_def in charts.items():
        if not isinstance(chart_id, str):
            raise ChartDefsError("chart_defs.charts keys must be strings")
        chart_def_map = _require_mapping(chart_def, f"chart_defs.charts.{chart_id}")
        _validate_chart_def(chart_id, chart_def_map)

    return root


def get_chart_def(chart_id: str) -> dict[str, Any]:
    charts = load_chart_defs().get("charts", {})
    if chart_id not in charts:
        raise ChartDefsError(f"chart_defs.charts missing: {chart_id}")
    return charts[chart_id]
