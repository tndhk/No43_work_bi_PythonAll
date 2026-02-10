"""Data transformation operations for page generator."""
from typing import Any, Optional
import pandas as pd


def apply_filter_operation(df: pd.DataFrame, op: dict) -> pd.DataFrame:
    """Apply filter operation to DataFrame.

    Supports two forms:
    1. Explicit column + values: {"column": "status", "values": ["Completed"]}
    2. Exclude pattern: {"exclude_status": ["Cancelled"]}

    Args:
        df: Input DataFrame
        op: Operation dict with 'column' and 'values', or 'exclude_*' key

    Returns:
        Filtered DataFrame
    """
    # Check for explicit column + values
    if "column" in op and "values" in op:
        column = op["column"]
        values = op["values"]
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        return df[df[column].isin(values)]

    # Check for exclude_* pattern
    exclude_keys = [k for k in op.keys() if k.startswith("exclude_")]
    if exclude_keys:
        for key in exclude_keys:
            column = key.replace("exclude_", "")
            values = op[key]
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found in DataFrame")
            df = df[~df[column].isin(values)]
        return df

    raise ValueError("Filter operation requires either 'column' and 'values', or 'exclude_*' key")


def apply_groupby_operation(df: pd.DataFrame, op: dict) -> pd.DataFrame:
    """Apply groupby aggregation operation.

    Args:
        df: Input DataFrame
        op: Operation dict with 'columns' (list) and 'agg' (dict of column: func)

    Returns:
        Grouped DataFrame

    Example:
        op = {
            "columns": ["region", "year"],
            "agg": {"id": "nunique", "duration": "sum"}
        }
    """
    if "columns" not in op or "agg" not in op:
        raise ValueError("Groupby operation requires 'columns' and 'agg' keys")

    columns = op["columns"]
    agg_dict = op["agg"]

    if not isinstance(columns, list):
        raise ValueError(f"Groupby 'columns' must be a list, got {type(columns)}")
    if not isinstance(agg_dict, dict):
        raise ValueError(f"Groupby 'agg' must be a dict, got {type(agg_dict)}")

    # Validate columns exist
    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Groupby column '{col}' not found in DataFrame")

    # Validate agg columns exist
    for col in agg_dict.keys():
        if col not in df.columns:
            raise ValueError(f"Aggregation column '{col}' not found in DataFrame")

    return df.groupby(columns, as_index=False).agg(agg_dict)


def apply_pivot_operation(df: pd.DataFrame, op: dict) -> pd.DataFrame:
    """Apply pivot operation.

    Args:
        df: Input DataFrame
        op: Operation dict with 'index', 'columns', 'values', and optional 'fill_value'

    Returns:
        Pivoted DataFrame with reset index

    Example:
        op = {
            "index": ["fiscal_year", "quarter"],
            "columns": "status",
            "values": "count",
            "fill_value": 0
        }
    """
    if "index" not in op or "columns" not in op or "values" not in op:
        raise ValueError("Pivot operation requires 'index', 'columns', and 'values' keys")

    index = op["index"]
    columns = op["columns"]
    values = op["values"]
    fill_value = op.get("fill_value", None)

    # Normalize index to list
    if not isinstance(index, list):
        index = [index]

    # Validate columns exist
    for col in index:
        if col not in df.columns:
            raise ValueError(f"Pivot index column '{col}' not found in DataFrame")

    if columns not in df.columns:
        raise ValueError(f"Pivot columns '{columns}' not found in DataFrame")

    if values not in df.columns:
        raise ValueError(f"Pivot values column '{values}' not found in DataFrame")

    # Use pivot_table instead of pivot to handle duplicate index entries
    # Default aggregation is 'mean', but for most cases we want 'sum'
    pivoted = df.pivot_table(
        index=index,
        columns=columns,
        values=values,
        fill_value=fill_value,
        aggfunc='sum'
    )

    return pivoted.reset_index()


def apply_compute_operation(df: pd.DataFrame, op: dict) -> pd.DataFrame:
    """Apply compute operation using pandas eval.

    Args:
        df: Input DataFrame
        op: Operation dict with 'name' (new column) and 'expression' (pandas expression)

    Returns:
        DataFrame with new computed column

    Example:
        op = {"name": "total", "expression": "col_a + col_b"}
    """
    if "name" not in op or "expression" not in op:
        raise ValueError("Compute operation requires 'name' and 'expression' keys")

    name = op["name"]
    expression = op["expression"]

    df = df.copy()

    try:
        df[name] = df.eval(expression)
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression '{expression}': {e}")

    return df


def apply_rename_operation(df: pd.DataFrame, op: dict) -> pd.DataFrame:
    """Apply rename operation.

    Args:
        df: Input DataFrame
        op: Operation dict with 'mapping' (dict of old_name: new_name)

    Returns:
        DataFrame with renamed columns

    Example:
        op = {"mapping": {"old_col": "New Column", "another": "Better Name"}}
    """
    if "mapping" not in op:
        raise ValueError("Rename operation requires 'mapping' key")

    mapping = op["mapping"]

    if not isinstance(mapping, dict):
        raise ValueError(f"Rename 'mapping' must be a dict, got {type(mapping)}")

    return df.rename(columns=mapping)


def apply_sort_operation(df: pd.DataFrame, op: dict) -> pd.DataFrame:
    """Apply sort operation.

    Supports three modes:
    1. Normal sort: {"by": "column", "ascending": true}
    2. Numeric sort: {"by": "column", "numeric": true, "ascending": true}
    3. Date parse sort: {"parse_date": {"column": "Start Date", "format": "%d-%b-%y", "output": "_temp"}}

    Args:
        df: Input DataFrame
        op: Operation dict with sorting configuration

    Returns:
        Sorted DataFrame
    """
    df = df.copy()

    # Mode 3: Date parse sort
    if "parse_date" in op:
        parse_config = op["parse_date"]
        if "column" not in parse_config or "format" not in parse_config or "output" not in parse_config:
            raise ValueError("parse_date requires 'column', 'format', and 'output' keys")

        column = parse_config["column"]
        fmt = parse_config["format"]
        output = parse_config["output"]

        if column not in df.columns:
            raise ValueError(f"Parse date column '{column}' not found in DataFrame")

        # Create temporary column for sorting
        df[output] = pd.to_datetime(df[column], format=fmt, errors="coerce")
        ascending = op.get("ascending", True)
        df = df.sort_values(by=output, ascending=ascending, kind="mergesort")

        return df

    # Mode 1 and 2: Normal or numeric sort
    if "by" not in op:
        raise ValueError("Sort operation requires 'by' key or 'parse_date' configuration")

    by = op["by"]
    ascending = op.get("ascending", True)
    numeric = op.get("numeric", False)

    if by not in df.columns:
        raise ValueError(f"Sort column '{by}' not found in DataFrame")

    if numeric:
        # Mode 2: Numeric sort
        df = df.sort_values(
            by=by,
            ascending=ascending,
            kind="mergesort",
            key=lambda x: pd.to_numeric(x, errors="coerce").fillna(0)
        )
    else:
        # Mode 1: Normal sort
        df = df.sort_values(by=by, ascending=ascending, kind="mergesort")

    return df


def apply_ensure_columns_operation(df: pd.DataFrame, op: dict) -> pd.DataFrame:
    """Ensure specified columns exist with default values.

    Args:
        df: Input DataFrame
        op: Operation dict with 'columns' (list) and optional 'default_value'

    Returns:
        DataFrame with guaranteed columns

    Example:
        op = {"columns": ["Completed", "Invalid"], "default_value": 0}
    """
    if "columns" not in op:
        raise ValueError("Ensure_columns operation requires 'columns' key")

    columns = op["columns"]
    default_value = op.get("default_value", 0)

    if not isinstance(columns, list):
        raise ValueError(f"Ensure_columns 'columns' must be a list, got {type(columns)}")

    df = df.copy()

    for col in columns:
        if col not in df.columns:
            df[col] = default_value

    return df


def apply_custom_operation(df: pd.DataFrame, op: dict, custom_module: Any) -> pd.DataFrame:
    """Apply custom operation from provided module.

    Args:
        df: Input DataFrame
        op: Operation dict with 'function' (name) and optional 'args' (dict)
        custom_module: Module containing custom functions

    Returns:
        Transformed DataFrame

    Example:
        op = {
            "function": "add_cadence_columns",
            "args": {"cadence": "weekly"}
        }
    """
    if "function" not in op:
        raise ValueError("Custom operation requires 'function' key")

    function_name = op["function"]
    args = op.get("args", {})

    if not isinstance(args, dict):
        raise ValueError(f"Custom operation 'args' must be a dict, got {type(args)}")

    if not hasattr(custom_module, function_name):
        raise ValueError(f"Function '{function_name}' not found in custom module")

    func = getattr(custom_module, function_name)

    # For now, pass args as-is (Phase 4 will handle {{variable}} substitution)
    return func(df, **args)


def execute_transform_pipeline(
    df: pd.DataFrame,
    operations: list[dict],
    custom_module: Optional[Any] = None,
) -> pd.DataFrame:
    """Execute a sequence of data transformation operations.

    Args:
        df: Input DataFrame
        operations: List of operation dicts (each has 'type' key)
        custom_module: Optional module for custom operations

    Returns:
        Transformed DataFrame

    Raises:
        ValueError: If operation type is unknown or operation fails
    """
    for op in operations:
        if "type" not in op:
            raise ValueError(f"Operation missing 'type' key: {op}")

        op_type = op["type"]

        if op_type == "filter":
            df = apply_filter_operation(df, op)
        elif op_type == "groupby":
            df = apply_groupby_operation(df, op)
        elif op_type == "pivot":
            df = apply_pivot_operation(df, op)
        elif op_type == "compute":
            df = apply_compute_operation(df, op)
        elif op_type == "rename":
            df = apply_rename_operation(df, op)
        elif op_type == "sort":
            df = apply_sort_operation(df, op)
        elif op_type == "ensure_columns":
            df = apply_ensure_columns_operation(df, op)
        elif op_type == "custom":
            if custom_module is None:
                raise ValueError(f"Custom operation '{op.get('function')}' requires custom_module")
            df = apply_custom_operation(df, op, custom_module)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")

    return df
