"""Data loading and transformation for HAMM Overview dashboard."""
import pandas as pd
from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.utils.data_helpers import (
    resolve_single_dataset_id,
    safe_load_filter_options,
)
from src.utils.filter_helpers import build_filter_set_from_map
from src.data.filter_engine import apply_filters
from ._constants import (
    DASHBOARD_ID,
    COLUMN_MAP,
    DERIVED_YEAR,
    DERIVED_MONTH,
    DERIVED_FISCAL_YEAR,
    KPI_ID_KPI_TOTAL_SCREENS,
    KPI_ID_KPI_TOTAL_ERV,
    KPI_ID_KPI_TOTAL_PRELIM,
    TABLE_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
)

# ---------------------------------------------------------------------------
# Filter column mapping (extends COLUMN_MAP with derived columns)
# ---------------------------------------------------------------------------
FILTER_COLUMN_MAP: dict[str, str] = {
    **COLUMN_MAP,
    "year": DERIVED_YEAR,
    "month": DERIVED_MONTH,
    "fiscal_year": DERIVED_FISCAL_YEAR,
}


def _prepare_base_df(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare base DataFrame with derived columns."""
    df = df.copy()
    created_dt = pd.to_datetime(df[COLUMN_MAP["created_at"]])
    df[DERIVED_YEAR] = created_dt.dt.strftime("%Y")
    df[DERIVED_MONTH] = created_dt.dt.strftime("%b")
    # Fiscal year calculation (assuming April start)
    shifted = created_dt + pd.DateOffset(months=3)
    df[DERIVED_FISCAL_YEAR] = shifted.dt.strftime("%Y").fillna("Null")
    return df


def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """Load unique values for all filters."""
    return safe_load_filter_options(
        reader,
        dataset_id,
        extract_columns={
            "region": COLUMN_MAP["region"],
            "_year": DERIVED_YEAR,
            "_month": DERIVED_MONTH,
        },
        prepare_fn=_prepare_base_df,
    )


def aggregate_volume_table(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate data for Volume Summary table."""
    return df.groupby(
        [DERIVED_FISCAL_YEAR, DERIVED_MONTH, COLUMN_MAP["status"]],
        as_index=False,
    ).agg({COLUMN_MAP["id"]: "nunique"})


def aggregate_volume_chart(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate data for Volume Chart."""
    return df.groupby(
        [DERIVED_MONTH, COLUMN_MAP["status"]],
        as_index=False,
    ).agg({COLUMN_MAP["id"]: "nunique"})


def load_and_filter_data(
    reader: ParquetReader,
    dataset_id: str,
    filter_column_map: dict[str, str],
    filter_pairs: list[tuple[str, list]],
) -> pd.DataFrame:
    """Load dataset and apply all filters."""
    df = get_cached_dataset(reader, dataset_id)
    df = _prepare_base_df(df)
    filters = build_filter_set_from_map(
        column_map=filter_column_map,
        filter_pairs=filter_pairs,
    )
    return apply_filters(df, filters)


def resolve_dataset_id_for_dashboard() -> str:
    """Resolve the dataset ID for all HAMM Overview charts."""
    component_ids = [
        KPI_ID_KPI_TOTAL_SCREENS,
        KPI_ID_KPI_TOTAL_ERV,
        KPI_ID_KPI_TOTAL_PRELIM,
        TABLE_ID_VOLUME_TABLE,
        CHART_ID_VOLUME_CHART,
    ]
    return resolve_single_dataset_id(DASHBOARD_ID, component_ids)
