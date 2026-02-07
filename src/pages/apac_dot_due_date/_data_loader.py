"""Data loading and filtering logic for APAC DOT Due Date Dashboard.

Extracts data access concerns from the page module so that layout()
and update_table() remain thin UI-only functions.
"""
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import FilterSet, CategoryFilter, apply_filters, extract_unique_values
from ._constants import COLUMN_MAP


def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """Load filter option values from cached dataset.

    Returns a dict with keys:
        months, areas, workstreams, vendors, amp_vs_av, order_types,
        total_count, prc_count, non_prc_count

    On any exception the function returns safe defaults (empty lists / zeros)
    so that the layout can still render.
    """
    try:
        df = get_cached_dataset(reader, dataset_id)

        months = extract_unique_values(df, COLUMN_MAP["month"])
        areas = extract_unique_values(df, COLUMN_MAP["area"])
        workstreams = extract_unique_values(df, COLUMN_MAP["category"])
        vendors = extract_unique_values(df, COLUMN_MAP["vendor"])
        amp_vs_av = extract_unique_values(df, COLUMN_MAP["amp_av"])
        order_types = extract_unique_values(df, COLUMN_MAP["order_type"])

        total_count = len(df)
        job_name_col = COLUMN_MAP["job_name"]
        prc_count = (
            len(df[df[job_name_col].str.contains("PRC", case=False, na=False)])
            if job_name_col in df.columns
            else 0
        )
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
    selected_months,
    prc_filter_value: str,
    area_values,
    category_values,
    vendor_values,
    amp_av_values,
    order_type_values,
) -> pd.DataFrame:
    """Load dataset and apply all filter criteria.

    Args:
        reader: ParquetReader instance.
        dataset_id: S3 dataset identifier.
        selected_months: List of month values or None/[].
        prc_filter_value: One of "all", "prc_only", "prc_not_included".
        area_values: List of area values or None/[].
        category_values: List of category values or None/[].
        vendor_values: List of vendor values or None/[].
        amp_av_values: List of AMP/AV values or None/[].
        order_type_values: List of order-type values or None/[].

    Returns:
        Filtered DataFrame.
    """
    df = get_cached_dataset(reader, dataset_id)

    # --- PRC filter (custom logic, applied before FilterSet) ---
    job_name_col = COLUMN_MAP["job_name"]
    if job_name_col in df.columns:
        if prc_filter_value == "prc_only":
            df = df[df[job_name_col].str.contains("PRC", case=False, na=False)]
        elif prc_filter_value == "prc_not_included":
            df = df[~df[job_name_col].str.contains("PRC", case=False, na=False)]

    # --- Build FilterSet for remaining category filters ---
    filters = FilterSet()

    if selected_months:
        filters.category_filters.append(
            CategoryFilter(column=COLUMN_MAP["month"], values=selected_months)
        )

    if area_values:
        filters.category_filters.append(
            CategoryFilter(column=COLUMN_MAP["area"], values=area_values)
        )

    if category_values:
        filters.category_filters.append(
            CategoryFilter(column=COLUMN_MAP["category"], values=category_values)
        )

    if vendor_values:
        filters.category_filters.append(
            CategoryFilter(column=COLUMN_MAP["vendor"], values=vendor_values)
        )

    if amp_av_values:
        filters.category_filters.append(
            CategoryFilter(column=COLUMN_MAP["amp_av"], values=amp_av_values)
        )

    if order_type_values:
        filters.category_filters.append(
            CategoryFilter(column=COLUMN_MAP["order_type"], values=order_type_values)
        )

    return apply_filters(df, filters)
