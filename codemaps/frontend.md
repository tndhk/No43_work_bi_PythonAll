# Frontend Codemap

Last Updated: 2026-02-08
Freshness: 2026-02-08T15:30:00Z
Entry Point: `app.py`
Framework: Plotly Dash 4.x / Dash Bootstrap Components / Dash Mantine Components

## Component Hierarchy

```
app.py
  |
  +-> create_layout() [src/layout.py]
  |     Returns: Div(Location#main-location, Div#main-content)
  |
  +-> register_layout_callbacks() [src/auth/layout_callbacks.py]
  |     Callback: main-location.pathname -> main-content.children
  |     If not authenticated -> create_login_layout()
  |     If authenticated -> sidebar + page_container
  |
  +-> register_login_callbacks() [src/auth/login_callbacks.py]
  |     Callback: login-submit/username/password -> login-error, login-location
  |
  +-> register_sidebar_callbacks() [src/components/sidebar_callbacks.py]
        Callback: logout-button.n_clicks -> logout-location.pathname

Authenticated Layout:
  +-- create_sidebar() [src/components/sidebar.py]
  |     Nav links from page_registry (sorted by order)
  |     Logout button
  |
  +-- page_container (Dash Pages API)
        +-- dashboard_home.py              path=/                  order=0
        +-- cursor_usage/__init__.py       path=/cursor-usage      order=1
        +-- apac_dot_due_date/__init__.py  path=/apac-dot-due-date order=2
        +-- hamm_overview/__init__.py      path=/hamm-overview     order=3
```

## Module Dependency Graph

```
src/layout.py
  Imports: dash (html, dcc)
  Exports: create_layout() -> html.Div

src/auth/flask_login_setup.py
  Imports: flask_login (LoginManager, UserMixin)
  Exports: User, init_login_manager()

src/auth/providers.py
  Imports: flask_login_setup.User, data.config.settings
  Exports: AuthProvider (Protocol), FormAuthProvider,
           get_auth_provider(), set_auth_provider()

src/auth/login_layout.py
  Imports: dash (html, dcc), dbc, data.config.settings
  Exports: create_login_layout() -> html.Div

src/auth/login_callbacks.py
  Imports: dash, flask_login, auth.providers
  Exports: register_login_callbacks(app)

src/auth/layout_callbacks.py
  Imports: dash, flask_login, components.sidebar, auth.login_layout
  Exports: register_layout_callbacks(app)

src/components/sidebar.py
  Imports: dash (html, page_registry, dcc), dbc
  Exports: create_sidebar() -> html.Div

src/components/sidebar_callbacks.py
  Imports: dash, flask_login
  Exports: register_sidebar_callbacks(app)

src/components/filters.py
  Imports: dash (dcc, html), dbc, dmc
  Exports: create_category_filter(), create_date_range_filter(),
           create_slicer_filter()

src/components/cards.py
  Imports: dbc, dash (html)
  Exports: create_kpi_card(title, value, subtitle=None)

src/charts/plotly_theme.py
  Imports: plotly.graph_objects
  Exports: PLOTLY_COLOR_PALETTE, PLOTLY_TEMPLATE, apply_theme(fig)

src/charts/templates.py
  Imports: pandas, plotly.express, plotly.graph_objects, dash (html),
           charts.plotly_theme.apply_theme
  Exports: render_summary_number(), render_bar_chart(),
           render_line_chart(), render_pie_chart(),
           render_table(), render_pivot_table(),
           CHART_TEMPLATES (registry dict),
           get_chart_template(), get_all_chart_types()

src/utils/data_helpers.py
  Imports: parquet_reader, cache, filter_engine, data_source_registry
  Exports: safe_load_filter_options(), strip_timezone(),
           resolve_single_dataset_id()

src/utils/filter_helpers.py
  Imports: filter_engine (FilterSet, CategoryFilter, DateRangeFilter)
  Exports: build_filter_set_from_map()
```

## Pages

### dashboard_home.py (path=/, order=0)

```
Imports: dash, dash (html, dcc, page_registry), dbc
Layout:  H1 + dashboard card grid (links to other pages)
Callbacks: None (static layout from page_registry)
```

### cursor_usage/ (path=/cursor-usage, order=1) -- Modularized Package

```
Structure:
  __init__.py          -> Dash register_page + layout() entry
  _constants.py        -> DASHBOARD_ID, DATASET_ID, ID_PREFIX, COLUMN_MAP, chart IDs
  data_sources.yml     -> chart_id -> dataset_id mapping (7 charts -> cursor-usage)
  _data_loader.py      -> load_filter_options(), load_and_filter_data()
  _layout.py           -> build_layout()
  _callbacks.py        -> update_dashboard() @callback

Dataset: "cursor-usage" (via data_sources.yml)
Filters: Date range, Model (category)
Outputs: 3 KPI cards + 3 charts + DataTable
```

Callback flow:
```
date-filter / model-filter
  -> data_source_registry.get_dataset_id(DASHBOARD_ID, CHART_ID_COST_TREND)
  -> _data_loader.load_and_filter_data()
     -> get_cached_dataset("cursor-usage")
     -> apply_filters(df, FilterSet)
  -> KPIs: Total Cost, Total Tokens, Request Count
  -> Charts: Daily Cost Trend (line), Token Efficiency (bar), Model Distribution (pie)
  -> DataTable: Top 100 rows
```

### apac_dot_due_date/ (path=/apac-dot-due-date, order=2) -- Modularized Package

```
Structure:
  __init__.py          -> Dash register_page + layout() entry
  _constants.py        -> DASHBOARD_ID, DATASETS dict (DatasetConfig), ID_PREFIX,
                          CTRL/FILTER/KPI/CHART IDs, DATASET_ID_2
  data_sources.yml     -> chart_id -> dataset_id mapping (2 charts -> 2 datasets)
  _data_loader.py      -> load_filter_options(), load_and_filter_data()
  _filters.py          -> build_filter_layout() -> 2 dbc.Row (RadioItems + Slicers)
  _layout.py           -> build_layout() -> html.Div (with MantineProvider)
  _callbacks.py        -> update_dashboard() + 7 clear callbacks
  charts/
    _table_specs.py    -> TableSpec dataclass + TABLE_SPECS registry
    _pivot_table_builder.py -> build_pivot_table() generic builder

Datasets:
  - "apac-dot-due-date" (reference table, chart-00)
  - "apac-dot-ddd-change-issue-sql" (change+issue table, chart-01)

Controls: Num/% toggle (RadioItems), Breakdown (RadioItems: Area/Category/Vendor)
Filters (Slicer chips): Month, PRC, Area, Category, Vendor, AMP VS AV, Order Type
  - Per-filter clear buttons
Outputs: 1 KPI (Total Work Orders) + 2 pivot DataTables
```

Callback flow:
```
ctrl-num-percent / ctrl-breakdown / filter-month / filter-prc /
filter-area / filter-category / filter-vendor / filter-amp-av / filter-order-type
  -> Loop over DATASETS config (reference, change_issue):
     -> resolve_dataset_id(DASHBOARD_ID, ds_cfg.chart_id)
     -> load_and_filter_data(reader, dataset_id, ds_cfg.column_map, ...)
        -> get_cached_dataset()
        -> _normalize_month_series() (YYYY-MM normalization)
        -> PRC custom filter (job name contains "PRC")
        -> build_filter_set_from_map() + apply_filters()
     -> build_pivot_table(filtered_df, breakdown, mode, column_map,
                          breakdown_map, TABLE_SPECS[spec_key])
        -> Pivot: breakdown_column x Month
        -> GRAND TOTAL row + AVG column
        -> Optional: convert to percentage mode
  -> KPI: nunique(work_order_id) from reference dataset
```

DatasetConfig pattern (in _constants.py):
```python
@dataclass(frozen=True)
class DatasetConfig:
    dataset_id, chart_id, chart_title_id,
    column_map, breakdown_map, table_spec_key,
    skip_filters: frozenset[str]

DATASETS = {"reference": DatasetConfig(...), "change_issue": DatasetConfig(...)}
```

### hamm_overview/ (path=/hamm-overview, order=3) -- Modularized Package

```
Structure:
  __init__.py          -> Dash register_page + layout() entry
  _constants.py        -> DASHBOARD_ID, DATASET_ID, ID_PREFIX, COLUMN_MAP,
                          chart/filter/control/derived-column IDs
  data_sources.yml     -> chart_id -> dataset_id mapping (3 charts -> hamm-dashboard)
  _data_loader.py      -> load_filter_options(), load_and_filter_data(),
                          add_cadence_columns(), FILTER_COLUMN_MAP
  _filters.py          -> build_filter_layout(), build_cadence_filter()
  _layout.py           -> build_layout() (with MantineProvider)
  _callbacks.py        -> update_dashboard() + 7 clear callbacks

Dataset: "hamm-dashboard" (via data_sources.yml)
Filters (10 slicers + 1 cadence):
  Region, Year, Month, Task ID, Content Type, Original Language,
  Dialogue, Genre, Error Code, Error Type, Cadence (weekly/monthly/quarterly/yearly)
  - Per-filter clear buttons (7 slicers)
Outputs: Volume Table (DataTable) + Volume Chart (stacked bar) + Task Details (DataTable)
```

Callback flow:
```
filter-region / filter-year / filter-month / filter-task-id /
filter-content-type / filter-original-language / filter-dialogue /
filter-genre / filter-error-code / filter-error-type / filter-cadence
  -> resolve_dataset_id_for_dashboard() (validates single dataset)
  -> load_and_filter_data(reader, dataset_id, FILTER_COLUMN_MAP, ...)
     -> get_cached_dataset("hamm-dashboard")
     -> _prepare_base_df() (tz strip, video duration parse, derived year/month)
     -> build_filter_set_from_map() + apply_filters()
  -> _build_volume_summary(df, cadence)
     -> add_cadence_columns() (fiscal year/quarter, ISO week, start/end dates)
     -> Exclude Cancelled/Invalid status
     -> Pivot: period x content_type -> Prelim/ERV counts + VOLUME TOTAL
  -> _build_volume_table() -> DataTable (desc order)
  -> _build_volume_chart() -> go.Figure (stacked bar: Prelim + ERV)
  -> _build_task_table() -> DataTable (Task ID, Name, Status, Duration, etc.)
```

Module naming conventions:
- Private modules: `_` prefix (not part of public API)
- Chart modules: `_ch{NN}_{name}.py` (numbered for ordering)
- Component IDs: page-specific ID_PREFIX (namespace isolation)
- Per-filter clear buttons: CTRL_ID_CLEAR_* pattern

## Filter UI Patterns

| Pattern | Component | Used By |
|---------|-----------|---------|
| `create_slicer_filter()` | dmc.ChipGroup (Mantine chips) | APAC DOT, Hamm |
| `create_category_filter()` | dcc.Dropdown | Hamm (Task ID, Month, Error Code) |
| `create_date_range_filter()` | dcc.DatePickerRange | Cursor Usage |
| `build_cadence_filter()` | dmc.ChipGroup (2x2 grid) | Hamm only |
| RadioItems (inline) | dcc.RadioItems | APAC DOT (Num/%, Breakdown) |

All slicer filters support a "Clear" button via `clear_button_id` parameter.

## Authentication Flow

```
Browser Request
  |
  [layout_callbacks: update_layout(pathname)]
  |
  current_user.is_authenticated?
  |
  No                          Yes
  |                           |
  create_login_layout()       create_sidebar() + page_container
  |
  [User submits form]
  |
  [login_callbacks: handle_login()]
  |
  get_auth_provider() -> FormAuthProvider
  |
  authenticate(username, password)
  |
  Match settings.basic_auth_*?
  |
  Yes -> login_user(User) -> redirect to /
  No  -> "Invalid username or password."

Logout:
  sidebar_callbacks: handle_logout()
  -> logout_user() -> redirect to /login
```

## Auth Provider Pattern

```python
class AuthProvider(Protocol):
    authenticate(username, password) -> Optional[User]
    get_user_groups(user_id) -> List[str]
    get_login_url() -> str

class FormAuthProvider:       # Current implementation
    # Validates against settings.basic_auth_username/password

# Future: SAMLAuthProvider
```

## Chart Template Registry

| Type | Function | Returns |
|------|----------|---------|
| summary-number | render_summary_number() | html.Div |
| bar | render_bar_chart() | go.Figure |
| line | render_line_chart() | go.Figure |
| pie | render_pie_chart() | go.Figure |
| table | render_table() | html.Div |
| pivot | render_pivot_table() | html.Div |

All go.Figure outputs pass through `apply_theme()` (Warm Professional Light theme).

## Style Architecture

```
assets/
  00-reset.css        CSS reset, custom properties (Warm Professional Light palette)
  01-typography.css    Font families (Noto Sans JP, Inter)
  02-layout.css       Sidebar + main content grid, responsive
  03-components.css   KPI cards, filter cards, slicer chips, tables, z-index fixes
  04-animations.css   Fade-in, slide-up transitions
  05-charts.css       Chart container styles
  06-login.css        Login page styles
```

Theme: Warm Professional Light
- Background: #f8f9fa (base), #ffffff (surface/card)
- Accent: #2563eb (blue primary)
- Text: #1a1a2e (primary), #64748b (secondary)
- Fonts: Noto Sans JP, Inter

## Testing

```
tests/unit/auth/test_session_auth.py
tests/unit/charts/test_plotly_theme.py
tests/unit/charts/test_templates.py
tests/unit/components/test_cards.py
tests/unit/components/test_filters.py
tests/unit/components/test_sidebar.py
tests/unit/pages/test_dashboard_home.py
tests/unit/pages/test_apac_dot_due_date.py     # Integration test
tests/unit/pages/test_page_imports.py           # Verifies app.py imports all packages
tests/unit/pages/apac_dot_due_date/
  test_constants.py
  test_data_loader.py
  test_data_sources.py
  test_filters.py
  test_layout.py
  test_callbacks.py
tests/unit/pages/cursor_usage/
  test_constants.py
  test_data_loader.py
  test_data_sources.py
  test_callbacks.py
tests/unit/pages/hamm_overview/
  test_constants.py
  test_data_loader.py
  test_data_sources.py
  test_callbacks.py
  test_layout.py
tests/unit/utils/
  test_data_helpers.py
  test_filter_helpers.py
tests/helpers/
  dash_test_utils.py           # Shared test utilities
  test_dash_test_utils.py
```

## Related Codemaps

- `codemaps/data.md` -- ParquetReader, filter_engine, cache used by pages
- `codemaps/backend.md` -- ETL pipelines that produce the datasets
- `codemaps/architecture.md` -- System overview
