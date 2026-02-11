"""Data models for dashboard page context in LLM chat."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KPIValue:
    """A single KPI value displayed on the dashboard.

    Attributes:
        name: Display name (e.g. "Total Screens Processed").
        value: Formatted value string (e.g. "23").
        logic: Human-readable description of the calculation logic.
    """

    name: str
    value: str
    logic: str


@dataclass(frozen=True)
class DashboardContext:
    """Dashboard-level context for LLM chat.

    Attributes:
        page_description: One-line summary of the dashboard page.
        kpis: List of KPI values currently displayed.
        active_filters: Map of filter name to selected values (None means all selected).
    """

    page_description: str
    kpis: list[KPIValue]
    active_filters: dict[str, list[str] | str | None]
