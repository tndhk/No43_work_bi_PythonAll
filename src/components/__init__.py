"""UI components.

Public API:
    - create_category_filter: Category filter (Dropdown) component
    - create_date_range_filter: Date range filter (DatePickerRange) component
    - create_slicer_filter: Slicer filter (ChipGroup) component
    - create_numeric_range_filter: Numeric range filter (RangeSlider) component
    - create_kpi_card: KPI display card component
    - create_kpi_card_with_delta: KPI card with delta indicator
    - create_sidebar: Sidebar navigation component
    - register_sidebar_callbacks: Register sidebar callbacks
"""
from src.components.filters import (
    create_category_filter,
    create_date_range_filter,
    create_slicer_filter,
    create_numeric_range_filter,
)
from src.components.cards import create_kpi_card, create_kpi_card_with_delta
from src.components.sidebar import create_sidebar
from src.components.sidebar_callbacks import register_sidebar_callbacks

__all__ = [
    "create_category_filter",
    "create_date_range_filter",
    "create_slicer_filter",
    "create_numeric_range_filter",
    "create_kpi_card",
    "create_kpi_card_with_delta",
    "create_sidebar",
    "register_sidebar_callbacks",
]
