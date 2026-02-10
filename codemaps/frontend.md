# Frontend Codemap

Freshness (UTC): 2026-02-10T15:30:00Z
Analysis Scope: `app.py`, `src/layout.py`, `src/auth/`, `src/components/`, `src/pages/`, `src/charts/`, `src/utils/`, `assets/`

## UI Composition

```text
app.py
  -> src/layout.create_layout()
  -> src/auth.register_login_callbacks()
  -> src/auth.register_layout_callbacks()
  -> src/components.register_sidebar_callbacks()
  -> Dash Pages
     - src/pages/dashboard_home.py
     - src/pages/cursor_usage/
     - src/pages/apac_dot_due_date/
     - src/pages/hamm_overview/
```

## Frontend Dependency Listing

- Authentication shell
  - `src/auth/layout_callbacks.py` -> `src.components.sidebar`, `src.auth.login_layout`
  - `src/auth/login_callbacks.py` -> `src.auth.providers`
  - `src/auth/providers.py` -> `src.auth.flask_login_setup`, `src.data.config`
- Shared UI components
  - `src/components/filters.py`:
    - `create_category_filter`: Dropdown filter
    - `create_date_range_filter`: DatePickerRange filter
    - `create_slicer_filter`: ChipGroup slicer with optional clear button
    - `create_numeric_range_filter`: RangeSlider filter
  - `src/components/cards.py`:
    - `create_kpi_card`: Basic KPI display (supports bg_color, accent_color)
    - `create_kpi_card_with_delta`: KPI with change indicator
    - `create_chart_card`: Chart card with chart-density-card, chart-density-graph, default config
    - `create_table_card`: Table card with standard header/body (header_id for dynamic titles)
  - `src/components/sidebar.py`: navigation from Dash `page_registry`
- Utility modules
  - `src/utils/callback_helpers.py`: `register_clear_callbacks` for bulk filter clear registration; `ensure_list` for normalizing callback values (None -> [], scalar -> [scalar])
  - `src/utils/data_helpers.py`: `safe_load_filter_options`, `strip_timezone`, `resolve_single_dataset_id`
  - `src/utils/filter_helpers.py`: `build_filter_set_from_map` for constructing FilterSet from column maps and filter pairs
- Page packages
  - `cursor_usage`: data load/filter + chart/table builders + KPI cards
  - `apac_dot_due_date`: multi-dataset pivot/table flow + clear callbacks
  - `hamm_overview`: see dedicated section below
  - `dashboard_home.py`: static home navigation
- Chart surface
  - `src/charts/chart_builder.py`: generic figure builder
    - Supported types: `bar`, `line`, `pie`, `stacked_bar`, `scatter`, `area`, `horizontal_bar`
  - `src/charts/table_builder.py`: generic DataTable builder
  - `src/charts/empty_states.py`: `create_empty_figure`, `create_empty_table`, `create_error_figure`
  - `src/charts/specs.py`:
    - `ChartSpec`: title, chart_type, x/y columns, color_map, height, barmode, labels, orientation, text_template, hover_template
    - `TableSpec`: title, styles, column_display, column_order, sort_action, page_size, filter_action
  - `src/charts/plotly_theme.py`: `apply_theme` for consistent styling
  - `src/charts/layout_helpers.py`: `apply_compact_chart_layout(fig, margin, legend)` -- removes title, axis labels, sets uniform text; used by all chart builders that render inside `dbc.Card`
- Chart styling
  - `assets/05-charts.css`: Plotly theme overrides + chart density classes
    - `.chart-density-row`, `.chart-density-card`, `.chart-density-graph` for compact layouts
    - `.plotly-container`, `.modebar` styling
  - Reusable Chart Density pattern (reference: `src/pages/hamm_overview/`)
    - `_layout.py`: use `create_chart_card` / `create_table_card` from `src/components/cards`; wrap row with `row-gap-sm` / `row-gap-md` + `chart-density-row` for chart rows
    - Tokens: `assets/00-reset.css` defines `--gap-section-sm/md`, `--z-dropdown`, `--transition-base`, `--spacing-compact`; adjust spacing centrally there
    - `_constants.py`: define `ChartSpec` defaults (`height`, `show_legend`, `text_template`)
    - `_chart_builders.py`: use `apply_compact_chart_layout()` from `src/charts/layout_helpers` for consistent margins and title removal (replaces manual `fig.update_layout()` calls)
    - `assets/05-charts.css`: apply scoped spacing rules via `.chart-density-*` classes (avoid global `.card` overrides)
- Table styling constants
  - `src/charts/specs.py`: `DEFAULT_STYLE_HEADER`, `DEFAULT_STYLE_DATA`, `DEFAULT_STYLE_CELL`, `COMPACT_STYLE_HEADER`, `COMPACT_STYLE_DATA`, `COMPACT_STYLE_CELL`

## hamm_overview Page Structure (Detailed)

Package: `src/pages/hamm_overview/` -- 7 source files + page_spec.yaml

```text
__init__.py           register_page, imports build_layout + _callbacks
_constants.py         IDs, COLUMN_MAP, ChartSpec/TableSpec instances, CLEAR_PAIRS, derived column names
_layout.py            build_layout() -> filter rows + content sections (Volume, Content Metadata, Error Details, Language)
_filters.py           build_filter_layout(opts, title_element) -> 2 filter rows (7 slicers + 3 category + 1 cadence chip_group)
_data_loader.py       load_filter_options, load_and_filter_data, build_volume_summary, aggregation builders; re-exports from _custom_logic
_custom_logic.py      Complex transformations not expressible in page_spec.yaml (cadence columns, date formatters, display prep)
_chart_builders.py    build_* wrappers calling shared chart_builder/table_builder + apply_compact_chart_layout
_callbacks.py         Single update_dashboard callback (14 outputs, 11 inputs), compute_volume_kpis, register_clear_callbacks
page_spec.yaml        Declarative spec: metadata, column_map, derived_columns, filters, layout (LayoutSectionSpec), components, custom_logic
```

File-level exports:

- `_constants.py`:
  - IDs: FILTER_ID_FILTER_{REGION,YEAR,CONTENT_TYPE,ORIGINAL_LANGUAGE,DIALOGUE,GENRE,ERROR_TYPE,MONTH,TASK_ID,ERROR_CODE,CADENCE}, KPI_ID_*, TABLE_ID_*, CHART_ID_*
  - COLUMN_MAP: 18 logical keys -> DataFrame column names
  - Derived column names: DERIVED_{YEAR,MONTH,FISCAL_YEAR,FISCAL_QUARTER,ISO_WEEK,START_DATE,END_DATE,VIDEO_DURATION_SECONDS}
  - ChartSpecs: VOLUME_CHART_SPEC, ERROR_RATIO_SPEC, ERROR_BY_SCREENER_SPEC, USER_BREAKDOWN_SPEC, BREAKDOWN_SPEC, METADATA_ORIGINAL_LANGUAGE_SPEC, METADATA_DIALOGUE_SPEC, METADATA_GENRE_SPEC
  - TableSpecs: VOLUME_TABLE_SPEC, TASK_TABLE_SPEC, LANGUAGE_TABLE_SPEC
  - CLEAR_PAIRS: 7 (filter_id, clear_button_id) tuples
  - Content type labels: ERV_LABEL, PRELIM_LABEL
  - Short aliases for backward compat: FILTER_ID_{short}, CTRL_ID_CLEAR_{short}, CHART_ID_{alias}

- `_custom_logic.py`:
  - `add_cadence_columns(df, cadence)`: weekly/monthly/quarterly/yearly period columns
  - `prepare_task_display_df(df)`: Task details table (9 display columns, numeric sort)
  - `prepare_language_display_df(df)`: Language table (6 display columns, NaN -> "N/A")
  - Scalar date formatters: `_format_start_date_monthly`, `_format_start_date_quarterly`, `_format_end_date_quarterly`, `_format_start_date_yearly`, `_format_end_date_yearly`
  - Vectorized date formatters: `_format_*_vec` variants of each scalar formatter
  - `_compute_total_duration_vec(created, completed)`: HH:MM:SS duration strings

- `_data_loader.py`:
  - FILTER_COLUMN_MAP: extends COLUMN_MAP with derived column mappings
  - `_prepare_base_df(df)`: strip timezone, add _year, _month, _fiscal_year, _video_duration_seconds
  - `load_filter_options(reader, dataset_id)`: 10 filter option sets
  - `load_and_filter_data(reader, dataset_id, column_map, filter_pairs)`: load + prepare + filter
  - `build_volume_summary(df, cadence)`: cadence-aware pivot (Completed/Invalid/VOLUME TOTAL)
  - `build_issues_ratio(df)`: User vs HAMM error counts
  - `build_intervention_by_screener(df)`: pivot by content type and error type
  - `build_user_intervention_breakdown(df)`, `build_hamm_intervention_breakdown(df)`: breakdown by error description
  - `build_original_language_distribution(df)`, `build_genre_distribution(df)`: distribution counts
  - `build_dialogue_by_content_type(df)`: Yes/No pivot by content type
  - `resolve_dataset_id_for_dashboard()`: validates single dataset across 14 components
  - Re-exports from `_custom_logic`: add_cadence_columns, prepare_task_display_df, prepare_language_display_df, date formatters, _compute_total_duration_vec

- `_chart_builders.py`:
  - Layout constants: _PIE_MARGIN, _PIE_LEGEND, _RIGHT_LEGEND_MARGIN, _RIGHT_LEGEND, _SIMPLE_BAR_MARGIN
  - Helpers: `_set_bar_textposition_inside`, `_set_pie_text_details`
  - Table builders: `build_volume_table`, `build_task_table`, `build_language_table`
  - Chart builders: `build_volume_chart`, `build_error_ratio`, `build_error_by_screener`, `build_user_breakdown`, `build_hamm_breakdown`, `build_metadata_original_language`, `build_metadata_dialogue`, `build_metadata_genre`
  - Aliases: build_error_ratio_chart, build_error_by_screener_chart, build_user_breakdown_chart, build_hamm_breakdown_chart, build_original_language_chart, build_dialogue_chart, build_genre_chart

- `_callbacks.py`:
  - `update_dashboard()`: single callback, 14 outputs (3 KPI + 4 table/chart containers + 7 chart figures), 11 filter inputs
  - `compute_volume_kpis(df)`: total_screens / total_erv / total_prelim (excludes Cancelled)
  - `register_clear_callbacks(CLEAR_PAIRS)`: 7 slicer clear bindings

- `page_spec.yaml`:
  - metadata: dashboard_id=hamm_overview, id_prefix=hamm-, dataset_id=hamm-dashboard
  - column_map: 18 entries (id, title, status, created_at, completed_at, region, content_type, original_language, dialogue, genre, error_code, error_type, error_description, video_duration, audio_details, language_count, additional_languages, year, month)
  - derived_columns: 8 entries (datetime_year, datetime_month, custom fiscal_year/quarter/iso_week/start_date/end_date, timedelta_to_seconds)
  - filters: 11 (7 slicer with clear, 3 category dropdown, 1 chip_group for cadence)
  - layout: 4 sections (Volume, Content Metadata, Error Details, Language Details) using LayoutSectionSpec
  - components: 14 (3 KPI, 3 tables, 8 charts) with data_transform operations and layout_overrides
  - custom_logic.imports: add_cadence_columns, prepare_task_display_df, prepare_language_display_df

## Development Tools (Runtime-independent)

- Page generation
  - `tools/page_generator/`: YAML-driven code generator for dashboard pages
    - `schema.py`: Pydantic models for page_spec.yaml validation
      - `PageSpec`: top-level model with cross-validation (unique IDs, column references, layout references)
      - `MetadataSpec`: dashboard_id, id_prefix, dataset_id, title, description
      - `DerivedColumnSpec`: type (datetime_year, datetime_month, fiscal_year, timedelta_to_seconds, custom, etc.), source_column, format, function, depends_on
      - `FilterSpec`: type (slicer, category, date, dropdown, chip_group), column, has_clear_button, multi, default_value
      - `LayoutSpec` / `LayoutSectionSpec` / `LayoutRowSpec` / `LayoutItemSpec`: section-based layout with title/description/className
      - `DataTransformSpec` / `DataTransformOperationSpec`: params, operations (filter, groupby, pivot, sort, rename, add_column, ensure_columns, count_rows, custom)
      - `ComponentSpec`: type (kpi, chart, table), spec (ChartSpecYAML/TableSpecYAML/KPICardSpec), data_transform, layout_overrides, data_source, bg_color, accent_color
      - `ChartSpecYAML`, `TableSpecYAML`, `KPICardSpec`: mirror runtime specs with Pydantic validation
    - `parser.py`: YAML loader with validation
    - `operations.py`: DataFrame transformation operations (filter, groupby, pivot, merge, etc.)
    - `cli.py`: CLI entrypoint (`python -m tools.page_generator`)
    - `generators/`: 7 file generators (constants, layout, filters, data_loader, custom_logic, callbacks, chart_builders)
    - `templates/data_loader.py.j2`: Jinja2 template for _data_loader.py generation
      - Supports: derived column generation, custom_logic imports, filter options, per-component build functions, resolve_dataset_id_for_dashboard
  - `scripts/scaffold_page.py`: Template-based page scaffolding CLI
    - Generates 9 canonical files (__init__, _constants, _layout, _filters, _data_loader, _callbacks, _chart_builders, SPEC.md, tests)
    - Uses placeholder replacement for customization

## Architecture Relationships

- Page callbacks orchestrate; data transformations are delegated to each page `_data_loader.py` and helper modules.
- Complex transformations that cannot be expressed declaratively in page_spec.yaml live in `_custom_logic.py` and are re-exported through `_data_loader.py`.
- Rendering contracts are centralized in `src/charts/*` and reused across pages.
- Auth decides whether user sees login layout or authenticated shell (`sidebar + page_container`).
- Clear callbacks use `register_clear_callbacks()` from `src/utils/callback_helpers.py`.
- page_spec.yaml serves as the declarative source of truth; generated code is then manually extended with aliases and custom logic.
