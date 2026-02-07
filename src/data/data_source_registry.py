"""Registry for mapping dashboard/chart IDs to dataset IDs via YAML configs."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import yaml


DASHBOARD_PAGES_DIR = Path(__file__).resolve().parents[1] / "pages"
DASHBOARD_CONFIG_FILENAME = "data_sources.yml"


def _config_path(dashboard_id: str) -> Path:
    return DASHBOARD_PAGES_DIR / dashboard_id / DASHBOARD_CONFIG_FILENAME


@lru_cache(maxsize=128)
def load_dashboard_config(dashboard_id: str) -> dict[str, Any]:
    """Load YAML config for a dashboard.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If YAML structure is invalid.
    """
    path = _config_path(dashboard_id)
    if not path.exists():
        raise FileNotFoundError(f"Dashboard config not found: {path}")

    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError("Dashboard config must be a mapping")

    charts = data.get("charts", {})
    if not isinstance(charts, dict):
        raise ValueError("Dashboard config 'charts' must be a mapping")

    return {"charts": charts}


def get_dataset_id(dashboard_id: str, chart_id: str) -> str | None:
    """Resolve dataset_id for a chart in a dashboard config.

    Returns:
        dataset_id string if found, otherwise None.
    """
    config = load_dashboard_config(dashboard_id)
    charts = config.get("charts", {})
    if not isinstance(charts, dict):
        return None

    dataset_id = charts.get(chart_id)
    if isinstance(dataset_id, str):
        return dataset_id
    return None


def resolve_dataset_id(
    dashboard_id: str,
    chart_id: str,
    fallback: Optional[str] = None,
) -> str:
    """Resolve dataset ID, raising or falling back when not found.

    Wraps ``get_dataset_id`` with a consistent None-handling policy:
    * If the registry contains the entry, return it.
    * Otherwise, return *fallback* when provided; raise ``ValueError`` when not.

    Args:
        dashboard_id: Dashboard identifier (directory name under pages/).
        chart_id: Chart key inside the dashboard's data_sources.yml.
        fallback: Value to return when the registry lookup yields None.
            When *fallback* is ``None`` (the default), a ``ValueError`` is
            raised instead.

    Returns:
        The resolved dataset ID string.

    Raises:
        ValueError: If the dataset ID is not found and no fallback is given.
        FileNotFoundError: If the dashboard config file does not exist
            (propagated from ``load_dashboard_config``).
    """
    dataset_id = get_dataset_id(dashboard_id, chart_id)
    if dataset_id is not None:
        return dataset_id

    if fallback is not None:
        return fallback

    raise ValueError(
        f"Dataset ID not found for dashboard '{dashboard_id}' "
        f"and chart '{chart_id}'"
    )
