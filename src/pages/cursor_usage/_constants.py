"""Constants for the Cursor Usage Dashboard page.

Centralizes dataset identifiers, column name mappings, and ID prefixes
to avoid hardcoded strings scattered across layout and callback code.
"""

# S3/Parquet dataset identifier
DATASET_ID: str = "cursor-usage"

# Component ID namespace prefix (for avoiding collisions with other pages)
ID_PREFIX: str = "cu-"

# Mapping from logical filter/column key to the actual DataFrame column name.
# Keys are short identifiers used in code; values are the raw column names
# as they appear in the Parquet/DataFrame.
COLUMN_MAP: dict[str, str] = {
    "date": "Date",
    "model": "Model",
    "cost": "Cost",
    "total_tokens": "Total Tokens",
    "user": "User",
    "kind": "Kind",
}
