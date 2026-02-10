"""Chart and table builders for HAMM Overview dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from ._constants import VOLUME_CHART_SPEC, VOLUME_TABLE_SPEC


def build_volume_table(df: pd.DataFrame) -> tuple[str, object]:
    """Render Volume Summary table."""
    return build_table(df, VOLUME_TABLE_SPEC)


def build_volume_chart(df: pd.DataFrame) -> go.Figure:
    """Render Volume Chart."""
    return build_chart(df, VOLUME_CHART_SPEC)
