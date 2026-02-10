# Frontend Codemap

Freshness (UTC): 2026-02-10T12:00:00Z
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
    - `create_kpi_card`: Basic KPI display
    - `create_kpi_card_with_delta`: KPI with change indicator
  - `src/components/sidebar.py`: navigation from Dash `page_registry`
- Utility modules
  - `src/utils/callback_helpers.py`: `register_clear_callbacks` for bulk filter clear registration; `ensure_list` for normalizing callback values (None -> [], scalar -> [scalar])
  - `src/utils/data_helpers.py`: `safe_load_filter_options`, `strip_timezone`, `resolve_single_dataset_id`
  - `src/utils/filter_helpers.py`: filter construction utilities
- Page packages
  - `cursor_usage`: data load/filter + chart/table builders + KPI cards
  - `apac_dot_due_date`: multi-dataset pivot/table flow + clear callbacks
  - `hamm_overview`: cadence-aware aggregation + table/chart builders + language table + content metadata charts + error analysis
    - New: page_spec.yaml support for YAML-driven page generation (hamm_overview prototype)
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
    - `_layout.py`: set `dcc.Graph` className=`"chart-density-graph"` + `config={"displayModeBar": False, "responsive": True}`; wrap card with className=`"chart-density-card"`; wrap row with className=`"chart-density-row"`
    - `_constants.py`: define `ChartSpec` defaults (`height`, `show_legend`, `text_template`)
    - `_chart_builders.py`: use `apply_compact_chart_layout()` from `src/charts/layout_helpers` for consistent margins and title removal (replaces manual `fig.update_layout()` calls)
    - `assets/05-charts.css`: apply scoped spacing rules via `.chart-density-*` classes (avoid global `.card` overrides)
- Table styling constants
  - `src/charts/specs.py`: `DEFAULT_STYLE_HEADER`, `DEFAULT_STYLE_DATA`, `DEFAULT_STYLE_CELL`, `COMPACT_STYLE_HEADER`, `COMPACT_STYLE_DATA`, `COMPACT_STYLE_CELL`

## Development Tools (Runtime-independent)

- Page generation
  - `tools/page_generator/`: YAML-driven code generator for dashboard pages
    - `schema.py`: Pydantic models (PageSpec, FilterSpec, ComponentSpec, ChartSpecYAML, TableSpecYAML, KPICardSpec)
    - `parser.py`: YAML loader with validation
    - `operations.py`: DataFrame transformation operations (filter, groupby, pivot, merge, etc.)
    - `cli.py`: CLI entrypoint (`python -m tools.page_generator`)
    - `generators/`: 7 file generators (constants, layout, filters, data_loader, custom_logic, callbacks, chart_builders)
  - `scripts/scaffold_page.py`: Template-based page scaffolding CLI
    - Generates 9 canonical files (__init__, _constants, _layout, _filters, _data_loader, _callbacks, _chart_builders, SPEC.md, tests)
    - Uses placeholder replacement for customization

## Architecture Relationships

- Page callbacks orchestrate; data transformations are delegated to each page `_data_loader.py` and helper modules.
- Rendering contracts are centralized in `src/charts/*` and reused across pages.
- Auth decides whether user sees login layout or authenticated shell (`sidebar + page_container`).
- Clear callbacks use `register_clear_callbacks()` from `src/utils/callback_helpers.py`.
