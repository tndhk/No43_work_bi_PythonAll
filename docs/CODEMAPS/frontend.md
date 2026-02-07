# Frontend Codemap

Last Updated: 2026-02-07
Framework: Plotly Dash 4.x + dash-bootstrap-components
Entry Point: `app.py` -> `src/layout.py`

## Component Hierarchy

```
app.layout (src/layout.py)
  +-- dcc.Location (id="main-location")
  +-- html.Div (id="main-content")
        |
        +-- [unauthenticated] --> create_login_layout()
        |                           +-- login-username (dbc.Input)
        |                           +-- login-password (dbc.Input)
        |                           +-- login-submit (dbc.Button)
        |                           +-- login-error (html.Div)
        |                           +-- login-location (dcc.Location)
        |
        +-- [authenticated] --> sidebar + page_container
                                  +-- create_sidebar()
                                  |     +-- sidebar-brand
                                  |     +-- NavLinks (from page_registry)
                                  |     +-- logout-button
                                  +-- html.Div.main-content
                                        +-- dash.page_container
```

## Auth Layer

| File | Purpose | Exports |
|------|---------|---------|
| `src/auth/flask_login_setup.py` | User model, LoginManager init | `User`, `init_login_manager()` |
| `src/auth/providers.py` | Auth protocol + FormAuth impl | `AuthProvider`, `FormAuthProvider`, `get_auth_provider()`, `set_auth_provider()` |
| `src/auth/login_layout.py` | Login page UI | `create_login_layout()` |
| `src/auth/login_callbacks.py` | Login form handler | `register_login_callbacks()` |
| `src/auth/layout_callbacks.py` | Auth-based routing | `register_layout_callbacks()` |

Auth flow:
```
Browser -> main-location (pathname change)
  -> layout_callbacks.update_layout()
    -> current_user.is_authenticated?
      No  -> create_login_layout()
      Yes -> sidebar + page_container
```

## Shared Components

| File | Exports | Usage |
|------|---------|-------|
| `src/components/cards.py` | `create_kpi_card(title, value, subtitle)` | Cursor Usage KPIs |
| `src/components/filters.py` | `create_category_filter(...)`, `create_date_range_filter(...)` | Both Tier-2 pages |
| `src/components/sidebar.py` | `create_sidebar()` | Main layout (authenticated) |
| `src/components/sidebar_callbacks.py` | `register_sidebar_callbacks()` | Logout handling |

## Chart Layer

| File | Exports | Lines |
|------|---------|-------|
| `src/charts/plotly_theme.py` | `PLOTLY_COLOR_PALETTE`, `PLOTLY_TEMPLATE`, `apply_theme()` | 84 |
| `src/charts/templates.py` | `render_bar_chart()`, `render_line_chart()`, `render_pie_chart()` | 114 |

All chart functions follow the signature:
```python
def render_*_chart(dataset: DataFrame, filters=None, params=None) -> go.Figure
```

## Pages

### Tier 1: dashboard_home.py

| Attribute | Value |
|-----------|-------|
| Route | `/` |
| Registration | `dash.register_page(__name__, path="/", name="Home", order=0)` |
| Callbacks | None |
| Data | None (reads from `page_registry`) |
| Lines | 53 |

### Tier 2: cursor_usage/

| File | Purpose | Lines |
|------|---------|-------|
| `__init__.py` | Page registration, layout delegate | 15 |
| `_constants.py` | `DASHBOARD_ID`, `DATASET_ID`, `ID_PREFIX="cu-"`, `COLUMN_MAP`, chart IDs | 36 |
| `_data_loader.py` | `load_filter_options()`, `load_and_filter_data()` | 101 |
| `_layout.py` | `build_layout()` -- filters, KPI placeholders, chart placeholders, table | 84 |
| `_callbacks.py` | `update_dashboard()` -- 3 KPIs + 3 charts + 1 table | 190 |

Data sources config: `data_sources.yml`
```yaml
charts:
  cu-chart-cost-trend: cursor-usage
  cu-kpi-total-cost: cursor-usage
  # ... (7 chart-id -> dataset-id mappings)
```

Callback inputs/outputs:
```
Inputs:  cu-filter-date (start/end), cu-filter-model (value)
Outputs: cu-kpi-total-cost, cu-kpi-total-tokens, cu-kpi-request-count,
         cu-chart-cost-trend, cu-chart-token-efficiency,
         cu-chart-model-distribution, cu-data-table
```

### Tier 2: apac_dot_due_date/

| File | Purpose | Lines |
|------|---------|-------|
| `__init__.py` | Page registration, layout delegate | 17 |
| `_constants.py` | `DASHBOARD_ID`, `DATASET_ID`, `ID_PREFIX="apac-dot-"`, `COLUMN_MAP`, `BREAKDOWN_MAP`, all IDs | 53 |
| `_data_loader.py` | `load_filter_options()`, `load_and_filter_data()` (PRC custom filter) | 137 |
| `_layout.py` | `build_layout()` -- delegates to `_filters.build_filter_layout()` | 52 |
| `_filters.py` | `build_filter_layout()` -- 5 filter rows | 175 |
| `_callbacks.py` | `update_all_charts()` -- title + table | 90 |
| `charts/_ch00_reference_table.py` | `build()` -- pivot table (pure function) | 147 |

Data sources config: `data_sources.yml`
```yaml
charts:
  apac-dot-chart-00: apac-dot-due-date
```

Callback inputs/outputs:
```
Inputs:  apac-dot-ctrl-num-percent, apac-dot-ctrl-breakdown,
         apac-dot-filter-month, apac-dot-filter-prc,
         apac-dot-filter-area, apac-dot-filter-category,
         apac-dot-filter-vendor, apac-dot-filter-amp-av,
         apac-dot-filter-order-type
Outputs: apac-dot-chart-00-title, apac-dot-chart-00
```

## CSS Architecture

Files loaded in alphabetical order:

| File | Purpose |
|------|---------|
| `00-reset.css` | CSS reset / normalization |
| `01-typography.css` | Font stacks, heading sizes |
| `02-layout.css` | Grid, sidebar, main-content layout |
| `03-components.css` | Cards, filters, buttons, z-index fixes |
| `04-animations.css` | Fade-in, slide-up transitions |
| `05-charts.css` | Chart container styling |
| `06-login.css` | Login page layout |

Theme: Warm Professional Light (Noto Sans JP / Inter)

## Testing

| Directory | Tests | Coverage |
|-----------|-------|----------|
| `tests/unit/auth/` | `test_session_auth.py` | Auth flow |
| `tests/unit/charts/` | `test_plotly_theme.py`, `test_templates.py` | Theme + chart builders |
| `tests/unit/components/` | `test_cards.py`, `test_filters.py`, `test_sidebar.py` | UI components |
| `tests/unit/pages/apac_dot_due_date/` | 6 test files (constants, data_loader, layout, filters, callbacks, charts) | Full page coverage |
| `tests/unit/pages/cursor_usage/` | 3 test files (constants, data_loader, callbacks) | Core logic |
| `tests/unit/pages/` | `test_dashboard_home.py`, `test_apac_dot_due_date.py` | Page registration |
| `tests/unit/` | `test_layout.py` | Main layout |
| `tests/helpers/` | `dash_test_utils.py`, `test_dash_test_utils.py` | Shared test utilities |

Test helper exports (`tests/helpers/dash_test_utils.py`):
- `find_component_by_id(component, target_id)`
- `find_components_by_type(component, target_type)`
- `extract_text_recursive(component)`
- `extract_dropdown_options(component, dropdown_id)`
- `extract_dropdown_value(component, dropdown_id)`

## Related Codemaps

- [Architecture](./architecture.md) -- System overview
- [Data](./data.md) -- Data layer used by page data loaders
- [Backend](./backend.md) -- ETL that feeds data to pages
