"""Helpers for applying DataTable styles from chart definitions."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_table_style(chart_def: dict[str, Any], breakdown_column: str) -> dict[str, Any]:
    """Return DataTable style kwargs with the breakdown column injected."""
    table_style = deepcopy(chart_def["table_style"])
    conditional = table_style.get("style_data_conditional", [])

    for rule in conditional:
        if not isinstance(rule, dict):
            continue
        condition = rule.get("if")
        if not isinstance(condition, dict):
            continue
        filter_query = condition.get("filter_query")
        if isinstance(filter_query, str):
            condition["filter_query"] = filter_query.replace(
                "{breakdown_col}", f"{{{breakdown_column}}}"
            )

    return table_style
