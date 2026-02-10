"""Pydantic models for page_spec.yaml validation."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------
class MetadataSpec(BaseModel):
    """Dashboard metadata."""

    dashboard_id: str = Field(..., description="Unique identifier for the dashboard (e.g., 'hamm_overview')")
    id_prefix: str = Field(..., description="Prefix for all component IDs (e.g., 'hamm-')")
    dataset_id: str = Field(..., description="Dataset ID to load data from")
    title: str = Field(..., description="Dashboard display title")
    description: str | None = Field(None, description="Dashboard description for SPEC.md")


# ---------------------------------------------------------------------------
# Derived Columns
# ---------------------------------------------------------------------------
class DerivedColumnSpec(BaseModel):
    """Derived column definition."""

    name: str = Field(..., description="Derived column name (e.g., '_year')")
    type: Literal[
        "year",
        "month",
        "fiscal_year",
        "fiscal_quarter",
        "iso_week",
        "date_extract",
        "datetime_year",
        "datetime_month",
        "timedelta_to_seconds",
        "custom",
    ] = Field(..., description="Type of derived column")
    source_column: str | None = Field(None, description="Source column name in DataFrame")
    format: str | None = Field(None, description="Format string for custom derivation")
    expression: str | None = Field(None, description="Custom expression for derived column")
    function: str | None = Field(None, description="Custom function name for complex derivations")
    depends_on: list[str] | None = Field(None, description="List of dependencies (e.g., ['cadence'])")


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
class FilterSpec(BaseModel):
    """Filter configuration."""

    type: Literal["slicer", "category", "date", "dropdown", "chip_group"] = Field(
        ..., description="Filter type"
    )
    id: str = Field(..., description="Filter component ID (must be unique)")
    label: str = Field(..., description="Display label for the filter")
    column: str | None = Field(None, description="Column name to filter on")
    options: list[str] | None = Field(None, description="Predefined options for category/slicer filters")
    has_clear_button: bool = Field(False, description="Whether to show clear button (for slicer)")
    multi: bool = Field(False, description="Whether to allow multiple selections")
    default: str | list[str] | None = Field(None, description="Default filter value (alias)")
    default_value: str | list[str] | None = Field(None, description="Default filter value")
    placeholder: str | None = Field(None, description="Placeholder text for dropdown")
    clear_button_id: str | None = Field(None, description="ID for clear button (if has_clear_button=True)")

    @model_validator(mode="after")
    def validate_column_requirement(self) -> FilterSpec:
        """Validate that column is provided when required."""
        if self.type in ("slicer", "category", "dropdown") and not self.column:
            raise ValueError(f"Filter type '{self.type}' requires a 'column' field")
        return self


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
class LayoutItemSpec(BaseModel):
    """Single component placement in a layout row."""

    component_id: str = Field(..., description="ID of the component to place")
    md: int = Field(12, description="Bootstrap column width (1-12)")
    className: str | None = Field(None, description="Additional CSS classes")


class LayoutRowSpec(BaseModel):
    """A single row in layout."""

    items: list[LayoutItemSpec] = Field(..., description="Components in this row")
    className: str | None = Field(None, description="CSS classes for the row")


class LayoutSectionSpec(BaseModel):
    """A logical section grouping multiple rows."""

    rows: list[LayoutRowSpec] = Field(..., description="Rows in this section")
    className: str | None = Field(None, description="CSS classes for the section")
    title: str | None = Field(None, description="Section title")
    description: str | None = Field(None, description="Section description")


class LayoutSpec(BaseModel):
    """Top-level layout definition."""

    sections: list[LayoutSectionSpec] = Field(..., description="Layout sections")


# ---------------------------------------------------------------------------
# Data Transformation
# ---------------------------------------------------------------------------
class DataTransformSpec(BaseModel):
    """Data transformation specification."""

    params: list[str] | None = Field(None, description="Parameter names to extract from context")
    operations: list[DataTransformOperationSpec] = Field(..., description="Transformation operations")


class DataTransformOperationSpec(BaseModel):
    """Single data transformation operation."""

    type: Literal[
        "filter",
        "group_by",
        "groupby",  # Alias for group_by
        "pivot",
        "melt",
        "sort",
        "rename",
        "add_column",
        "drop_column",
        "ensure_columns",
        "count_rows",
        "custom",
    ] = Field(..., description="Type of transformation")

    # Common fields
    columns: list[str] | str | None = Field(None, description="Columns involved in the operation")

    # Filter operation
    filter_query: str | None = Field(None, description="Pandas query string for filtering")
    include: dict[str, list[str]] | None = Field(None, description="Include filter (column: [values])")
    exclude: dict[str, list[str]] | None = Field(None, description="Exclude filter (column: [values])")
    exclude_null: list[str] | None = Field(None, description="Columns to exclude null values from")

    # Group by operation
    group_columns: list[str] | None = Field(None, description="Columns to group by")
    agg_funcs: dict[str, str] | None = Field(None, description="Aggregation functions per column")
    agg: dict[str, str] | None = Field(None, description="Alias for agg_funcs")
    output_name: str | None = Field(None, description="Output column name for aggregation")

    # Pivot operation
    index: list[str] | str | None = Field(None, description="Index columns for pivot")
    columns_pivot: list[str] | str | None = Field(None, description="Columns to pivot")
    values: list[str] | str | None = Field(None, description="Values for pivot", alias="values")
    values_pivot: list[str] | str | None = Field(None, description="Values for pivot (alias)")
    fill_value: int | float | str | None = Field(None, description="Fill value for missing pivot values")

    # Sort operation
    by: str | None = Field(None, description="Column to sort by")
    ascending: bool = Field(True, description="Sort order")
    parse_date: dict[str, str] | None = Field(None, description="Parse date for sorting")

    # Rename operation
    rename_map: dict[str, str] | None = Field(None, description="Column rename mapping")
    mapping: dict[str, str] | None = Field(None, description="Alias for rename_map")

    # Add column operation
    column_name: str | None = Field(None, description="New column name")
    name: str | None = Field(None, description="Alias for column_name")
    expression: str | None = Field(None, description="Expression to compute new column")
    left: str | None = Field(None, description="Left operand for binary operation")
    operator: str | None = Field(None, description="Operator for binary operation (+, -, *, /)")
    right: str | int | float | None = Field(None, description="Right operand for binary operation")

    # Ensure columns operation
    default_value: int | float | str | None = Field(None, description="Default value for missing columns")

    # Count rows operation
    output_key: str | None = Field(None, description="Output key for count_rows operation")

    # Custom operation
    custom_code: str | None = Field(None, description="Custom Python code for transformation")
    function: str | None = Field(None, description="Custom function name to call")
    args: dict[str, Any] | None = Field(None, description="Arguments to pass to custom function")
    params: list[str] | None = Field(None, description="Parameter names to extract from context")


# ---------------------------------------------------------------------------
# Chart and Table Specs (matching existing src/charts/specs.py)
# ---------------------------------------------------------------------------
class ChartSpecYAML(BaseModel):
    """Chart specification matching ChartSpec dataclass."""

    title: str = Field(..., description="Chart title")
    chart_type: Literal["bar", "line", "pie", "stacked_bar", "grouped_bar", "scatter"] = Field(
        ..., description="Chart type"
    )
    x_column: str = Field(..., description="X-axis column")
    y_columns: list[str] = Field(..., description="Y-axis columns")

    # Optional fields
    color_map: dict[str, str] | None = Field(None, description="Color mapping for series")
    height: int = Field(400, description="Chart height in pixels")
    barmode: Literal["group", "stack", "overlay"] | None = Field(None, description="Bar chart mode")
    labels: dict[str, str] | None = Field(None, description="Axis labels")
    show_legend: bool = Field(True, description="Whether to show legend")
    orientation: Literal["v", "h"] = Field("v", description="Chart orientation (v=vertical, h=horizontal)")
    text_template: str | None = Field(None, description="Data labels template (e.g., '%{y}')")
    hover_template: str | None = Field(None, description="Hover tooltip template")


class TableSpecYAML(BaseModel):
    """Table specification matching TableSpec dataclass."""

    title: str = Field(..., description="Table title")

    # Style fields
    style_table: dict[str, Any] = Field(default_factory=dict, description="Table container style")
    style_cell: dict[str, Any] = Field(default_factory=dict, description="Cell style")
    style_header: dict[str, Any] = Field(default_factory=dict, description="Header style")
    style_data_conditional: list[dict[str, Any]] = Field(
        default_factory=list, description="Conditional styling rules"
    )

    # Optional fields
    column_display: dict[str, str] = Field(default_factory=dict, description="Column name display mapping")
    column_order: list[str] = Field(default_factory=list, description="Column display order")
    sort_action: Literal["none", "native", "custom"] = Field("none", description="Sort behavior")
    page_size: int = Field(0, description="Number of rows per page (0 = no pagination)")
    filter_action: Literal["none", "native", "custom"] = Field("none", description="Filter behavior")


class KPICardSpec(BaseModel):
    """KPI card specification."""

    value_column: str | None = Field(None, description="Column containing the KPI value")
    agg_func: Literal["sum", "count", "mean", "median", "max", "min", "nunique"] = Field(
        "sum", description="Aggregation function"
    )
    format: str | None = Field(None, description="Format string for value (e.g., '{:,.0f}')")
    color_bg: str | None = Field(None, description="Background color")
    color_accent: str | None = Field(None, description="Accent color")
    subtitle: str | None = Field(None, description="Optional subtitle")


# ---------------------------------------------------------------------------
# Component
# ---------------------------------------------------------------------------
class ComponentSpec(BaseModel):
    """Component definition (chart, table, or KPI)."""

    type: Literal["kpi", "chart", "table"] = Field(..., description="Component type")
    id: str = Field(..., description="Component ID (must be unique)")
    title: str = Field(..., description="Component display title")

    # Component-specific spec
    spec: ChartSpecYAML | TableSpecYAML | KPICardSpec = Field(
        ..., description="Type-specific specification"
    )

    # Data transformation
    data_transform: DataTransformSpec | dict[str, Any] | None = Field(
        None, description="Data transformation operations"
    )

    # Additional fields for KPI cards (top-level, outside of spec)
    bg_color: str | None = Field(None, description="Background color for KPI card")
    accent_color: str | None = Field(None, description="Accent color for KPI card")

    # Data source specification
    data_source: str | None = Field(None, description="Data source identifier (e.g., 'filtered_data')")

    # Layout customization for charts
    layout_overrides: dict[str, Any] | None = Field(
        None, description="Chart layout overrides (margin, legend, textposition, etc.)"
    )

    @model_validator(mode="after")
    def validate_spec_type(self) -> ComponentSpec:
        """Validate that spec matches component type."""
        if self.type == "kpi" and not isinstance(self.spec, KPICardSpec):
            raise ValueError(f"Component type 'kpi' requires KPICardSpec, got {type(self.spec)}")
        elif self.type == "chart" and not isinstance(self.spec, ChartSpecYAML):
            raise ValueError(f"Component type 'chart' requires ChartSpecYAML, got {type(self.spec)}")
        elif self.type == "table" and not isinstance(self.spec, TableSpecYAML):
            raise ValueError(f"Component type 'table' requires TableSpecYAML, got {type(self.spec)}")
        return self


# ---------------------------------------------------------------------------
# Top-level Page Spec
# ---------------------------------------------------------------------------
class PageSpec(BaseModel):
    """Top-level page specification."""

    metadata: MetadataSpec = Field(..., description="Dashboard metadata")
    column_map: dict[str, str] = Field(..., description="Logical key to DataFrame column mapping")
    derived_columns: list[DerivedColumnSpec] | None = Field(None, description="Derived columns")
    filters: list[FilterSpec] = Field(..., description="Filter definitions")
    layout: LayoutSpec = Field(..., description="Layout structure")
    components: list[ComponentSpec] = Field(..., description="Component definitions")
    custom_logic: dict[str, Any] | None = Field(None, description="Custom callback logic")

    @model_validator(mode="after")
    def validate_unique_ids(self) -> PageSpec:
        """Validate that all IDs are unique across filters and components."""
        all_ids: list[str] = []

        # Collect filter IDs
        for f in self.filters:
            all_ids.append(f.id)
            if f.clear_button_id:
                all_ids.append(f.clear_button_id)

        # Collect component IDs
        for c in self.components:
            all_ids.append(c.id)

        # Check for duplicates
        seen = set()
        duplicates = set()
        for id_val in all_ids:
            if id_val in seen:
                duplicates.add(id_val)
            seen.add(id_val)

        if duplicates:
            raise ValueError(f"Duplicate IDs found: {sorted(duplicates)}")

        return self

    @model_validator(mode="after")
    def validate_column_references(self) -> PageSpec:
        """Validate that columns referenced in components exist in column_map.

        Note: Components with data_transform are skipped from validation, as they may
        create new columns through transformations (group_by, pivot, etc.).
        """
        available_columns = set(self.column_map.keys())

        # Add derived column names
        if self.derived_columns:
            for dc in self.derived_columns:
                available_columns.add(dc.name)

        errors: list[str] = []

        # Check filter columns (skip filters without a column, e.g. chip_group)
        for f in self.filters:
            if f.column is not None and f.column not in available_columns:
                errors.append(f"Filter '{f.id}' references unknown column '{f.column}'")

        # Check component spec columns (skip if component has data_transform)
        for comp in self.components:
            # Skip validation if component has data transformations
            if comp.data_transform:
                continue

            if comp.type == "chart":
                spec = comp.spec
                if isinstance(spec, ChartSpecYAML):
                    if spec.x_column not in available_columns:
                        errors.append(
                            f"Chart '{comp.id}' references unknown x_column '{spec.x_column}'"
                        )
                    for y_col in spec.y_columns:
                        if y_col not in available_columns:
                            errors.append(
                                f"Chart '{comp.id}' references unknown y_column '{y_col}'"
                            )
            elif comp.type == "kpi":
                spec = comp.spec
                if isinstance(spec, KPICardSpec):
                    if spec.value_column not in available_columns:
                        errors.append(
                            f"KPI '{comp.id}' references unknown value_column '{spec.value_column}'"
                        )

        if errors:
            raise ValueError("Column reference errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return self

    @model_validator(mode="after")
    def validate_layout_references(self) -> PageSpec:
        """Validate that layout references valid component IDs."""
        component_ids = {c.id for c in self.components}
        errors: list[str] = []

        for section_idx, section in enumerate(self.layout.sections):
            for row_idx, row in enumerate(section.rows):
                for item_idx, item in enumerate(row.items):
                    if item.component_id not in component_ids:
                        errors.append(
                            f"Layout section[{section_idx}].row[{row_idx}].item[{item_idx}] "
                            f"references unknown component_id '{item.component_id}'"
                        )

        if errors:
            raise ValueError("Layout reference errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return self
