"""Data loading and filtering logic for APAC DOT Due Date Dashboard.

Extracts data access concerns from the page module so that layout()
and update_table() remain thin UI-only functions.
"""
from typing import Optional
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import apply_filters, extract_unique_values
from src.utils.filter_helpers import build_filter_set_from_map
from ._constants import DATASETS

MIN_MONTH_START = pd.Timestamp("2024-01-01")


def _normalize_month_value(value) -> Optional[str]:
    """Normalize raw month-like value to YYYY-MM and apply lower-bound cutoff."""
    if pd.isna(value):
        return None

    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None

    parsed = parsed.tz_convert(None)
    if parsed < MIN_MONTH_START:
        return None

    return parsed.strftime("%Y-%m")


def _normalize_month_series(series: pd.Series) -> pd.Series:
    """Normalize a month-like Series to YYYY-MM strings."""
    return series.apply(_normalize_month_value)


def _extract_normalized_months(df: pd.DataFrame, month_col: str) -> list[str]:
    """Extract unique normalized months from a DataFrame column."""
    if month_col not in df.columns:
        return []
    months = _normalize_month_series(df[month_col]).dropna().unique().tolist()
    return sorted(months)


def load_filter_options(
    reader: ParquetReader,
    dataset_id: str,
    dataset_id_2: Optional[str] = None,
) -> dict:
    """Load filter option values from cached dataset.

    Returns a dict with keys:
        months, areas, workstreams, vendors, amp_vs_av, order_types,
        total_count, prc_count, non_prc_count

    When *dataset_id_2* is provided:
        - ``months`` is the sorted union of months from both datasets.
        - ``order_types`` is extracted from dataset 2.

    On any exception the function returns safe defaults (empty lists / zeros)
    so that the layout can still render.
    """
    try:
        ref_config = DATASETS["reference"]
        change_config = DATASETS["change_issue"]

        df = get_cached_dataset(reader, dataset_id)

        months = _extract_normalized_months(df, ref_config.column_map["month"])
        areas = extract_unique_values(df, ref_config.column_map["area"])
        workstreams = extract_unique_values(df, ref_config.column_map["category"])
        vendors = extract_unique_values(df, ref_config.column_map["vendor"])
        amp_vs_av = extract_unique_values(df, ref_config.column_map["amp_av"])
        order_types = extract_unique_values(df, ref_config.column_map["order_type"])

        # --- Merge with dataset 2 when provided ---
        if dataset_id_2 is not None:
            try:
                df2 = get_cached_dataset(reader, dataset_id_2)
                months_2 = _extract_normalized_months(df2, change_config.column_map["month"])
                months = sorted(set(months + months_2))
                order_types = extract_unique_values(df2, change_config.column_map["order_type"])
            except Exception:
                pass  # dataset 2 failure: keep dataset 1 options

        total_count = len(df)
        job_name_col = ref_config.column_map.get("job_name")
        if job_name_col and job_name_col in df.columns:
            prc_count = len(df[df[job_name_col].str.contains("PRC", case=False, na=False)])
        else:
            prc_count = 0
        non_prc_count = total_count - prc_count

        return {
            "months": months,
            "areas": areas,
            "workstreams": workstreams,
            "vendors": vendors,
            "amp_vs_av": amp_vs_av,
            "order_types": order_types,
            "total_count": total_count,
            "prc_count": prc_count,
            "non_prc_count": non_prc_count,
        }

    except Exception:
        return {
            "months": [],
            "areas": [],
            "workstreams": [],
            "vendors": [],
            "amp_vs_av": [],
            "order_types": [],
            "total_count": 0,
            "prc_count": 0,
            "non_prc_count": 0,
        }


def load_and_filter_data(
    reader: ParquetReader,
    dataset_id: str,
    column_map: dict[str, str],
    selected_months,
    prc_filter_value: str,
    area_values,
    category_values,
    vendor_values,
    amp_av_values: Optional[list] = None,
    order_type_values: Optional[list] = None,
) -> pd.DataFrame:
    """Load dataset and apply all filter criteria.

    Generic function that works with any column_map, eliminating the need
    for separate load_and_filter_data_2() function.

    Args:
        reader: ParquetReader instance.
        dataset_id: S3 dataset identifier.
        column_map: Mapping from logical filter key to DataFrame column name.
        selected_months: List of month values or None/[].
        prc_filter_value: One of "all", "prc_only", "prc_not_included".
        area_values: List of area values or None/[].
        category_values: List of category values or None/[].
        vendor_values: List of vendor values or None/[].
        amp_av_values: Optional list of AMP/AV values or None/[].
        order_type_values: Optional list of order-type values or None/[].

    Returns:
        Filtered DataFrame.
    """
    df = get_cached_dataset(reader, dataset_id)
    month_col = column_map.get("month")

    # Normalize month to YYYY-MM and enforce lower bound.
    if month_col and month_col in df.columns:
        df = df.copy()
        df[month_col] = _normalize_month_series(df[month_col])
        df = df[df[month_col].notna()]

        if selected_months:
            selected_months = sorted({
                month
                for month in (_normalize_month_value(value) for value in selected_months)
                if month
            })

    # --- PRC filter (custom logic, applied before FilterSet) ---
    job_name_col = column_map.get("job_name")
    if job_name_col and job_name_col in df.columns:
        if prc_filter_value == "prc_only":
            df = df[df[job_name_col].str.contains("PRC", case=False, na=False)]
        elif prc_filter_value == "prc_not_included":
            df = df[~df[job_name_col].str.contains("PRC", case=False, na=False)]

    # --- Build FilterSet using helper function ---
    filter_pairs = [
        ("month", selected_months),
        ("area", area_values),
        ("category", category_values),
        ("vendor", vendor_values),
        ("amp_av", amp_av_values),
        ("order_type", order_type_values),
    ]
    filters = build_filter_set_from_map(column_map, filter_pairs)

    return apply_filters(df, filters)
