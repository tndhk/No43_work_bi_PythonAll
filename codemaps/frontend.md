# Frontend Codemap

Last Updated: 2026-02-07
Entry Point: `app.py`
Framework: Plotly Dash 2.14+ / Dash Bootstrap Components 1.5+

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
        +-- cursor_usage.py                path=/cursor-usage      order=1
        +-- apac_dot_due_date/__init__.py   path=/apac-dot-due-date order=2
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
  Imports: dash (dcc), dbc
  Exports: create_category_filter(), create_date_range_filter()

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
```

## Pages

### dashboard_home.py (path=/, order=0)

```
Imports: dash, dash (html, dcc, page_registry), dbc
Layout:  H1 + dashboard card grid (links to other pages)
Callbacks: None (static layout from page_registry)
```

### cursor_usage.py (path=/cursor-usage, order=1)

```
Imports: ParquetReader, get_cached_dataset, FilterSet,
         CategoryFilter, DateRangeFilter, apply_filters,
         create_date_range_filter, create_category_filter,
         create_kpi_card, render_line_chart, render_bar_chart,
         render_pie_chart, dash_table
Dataset: "cursor-usage"
Filters: Date range, Model (category)
Outputs: 3 KPI cards + 3 charts + DataTable
```

Callback flow:
```
date-filter / model-filter
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
  _constants.py        -> DATASET_ID, ID_PREFIX, COLUMN_MAP, BREAKDOWN_MAP
  _data_loader.py      -> load_filter_options(), load_and_filter_data()
  _filters.py          -> build_filter_layout() -> 5 dbc.Row
  _layout.py           -> build_layout() -> html.Div
  _callbacks.py        -> update_all_charts() @callback
  charts/
    __init__.py        -> Sub-package docstring
    _ch00_reference_table.py -> build(df, breakdown, mode) -> (title, component)

Dataset: "apac-dot-due-date"
Filters: Num/% toggle, Breakdown tabs (Area/Category/Vendor),
         Month, PRC, Area, Category, Vendor, AMP VS AV, Order Type
Outputs: Pivot table (DataTable) with GRAND TOTAL + AVG
```

Callback flow:
```
num-percent-toggle / breakdown-tabs / filter-month / prc-filter /
area-filter / category-filter / vendor-filter / amp-av-filter / order-type-filter
  -> _callbacks.update_all_charts()
  -> _data_loader.load_and_filter_data()
     -> get_cached_dataset("apac-dot-due-date")
     -> PRC custom filter (job name contains "PRC")
     -> apply_filters(df, FilterSet with COLUMN_MAP)
  -> charts._ch00_reference_table.build(filtered_df, breakdown_tab, num_percent_mode)
     -> Pivot: breakdown_column x Delivery Completed Month
     -> GRAND TOTAL row + AVG column
     -> Optional: convert to percentage mode
     -> DataTable with conditional styling
```

Module naming conventions:
- Private modules: `_` prefix (not part of public API)
- Chart modules: `_ch{NN}_{name}.py` (numbered for ordering)
- Component IDs: `apac-dot-` prefix (namespace isolation)

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

All chart functions accept: `(dataset, filters=None, params=None)`
All go.Figure outputs pass through `apply_theme()` (Warm Professional Light theme).

## Style Architecture

```
assets/
  00-reset.css        CSS reset, custom properties (Warm Professional Light palette)
  01-typography.css    Font families (Noto Sans JP, Inter)
  02-layout.css       Sidebar + main content grid, responsive
  03-components.css   KPI cards, filter cards, dashboard cards, tables, z-index fixes
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
tests/unit/pages/apac_dot_due_date/
  test_constants.py
  test_data_loader.py
  test_filters.py
  test_layout.py
  test_callbacks.py
  charts/
    test_ch00_reference_table.py
tests/unit/test_layout.py
```

## Related Codemaps

- `codemaps/data.md` -- ParquetReader, filter_engine, cache used by pages
- `codemaps/backend.md` -- ETL pipelines that produce the datasets
- `codemaps/architecture.md` -- System overview
