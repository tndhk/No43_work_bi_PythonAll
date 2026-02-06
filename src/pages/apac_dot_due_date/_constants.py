"""Constants for the APAC DOT Due Date Dashboard page.

Centralizes dataset identifiers, column name mappings, and ID prefixes
to avoid hardcoded strings scattered across layout and callback code.
"""

# S3/Parquet dataset identifier
DATASET_ID: str = "apac-dot-due-date"

# Component ID namespace prefix (for avoiding collisions with other pages)
ID_PREFIX: str = "apac-dot-"

# Mapping from logical filter ID to the actual DataFrame column name.
# Keys are short identifiers used in code; values are the raw column names
# as they appear in the Parquet/DataFrame.
COLUMN_MAP: dict[str, str] = {
    "month": "Delivery Completed Month",
    "area": "business area",
    "category": "Metric Workstream",
    "vendor": "Vendor: Account Name",
    "amp_av": "AMP VS AV Scope",
    "order_type": "order tags",
}

# Mapping from breakdown tab ID to the DataFrame column used for pivot grouping.
# This is a subset of COLUMN_MAP -- only the columns that make sense as
# breakdown dimensions in the pivot table.
BREAKDOWN_MAP: dict[str, str] = {
    "area": "business area",
    "category": "Metric Workstream",
    "vendor": "Vendor: Account Name",
}
