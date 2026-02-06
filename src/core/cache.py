"""TTL cache for dataset caching."""
from flask_caching import Cache
import pandas as pd
from src.data.parquet_reader import ParquetReader

cache = Cache()


def init_cache(server) -> None:
    """
    Initialize cache on Flask server.

    Args:
        server: Flask server instance (app.server)
    """
    cache.init_app(server, config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes
    })


def get_cached_dataset(reader: ParquetReader, dataset_id: str) -> pd.DataFrame:
    """
    Get dataset through cache.
    On cache miss, reads from ParquetReader and stores in cache.

    Cache key: dataset_id only
    (Filters are applied in memory, so cache key doesn't include filter conditions)

    Args:
        reader: ParquetReader instance
        dataset_id: Dataset ID

    Returns:
        DataFrame
    """
    cache_key = f"dataset:{dataset_id}"

    # Try to get from cache
    cached_df = cache.get(cache_key)
    if cached_df is not None:
        return cached_df

    # Cache miss: read from S3
    df = reader.read_dataset(dataset_id)

    # Store in cache
    cache.set(cache_key, df)

    return df
