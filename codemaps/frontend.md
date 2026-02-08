# Frontend Codemap

Freshness (UTC): 2026-02-08T07:50:11Z
Analysis Scope: `app.py`, `src/layout.py`, `src/auth/`, `src/components/`, `src/pages/`, `src/charts/`

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
  - `src/components/filters.py`: `create_category_filter`, `create_date_range_filter`, `create_slicer_filter`
  - `src/components/cards.py`: `create_kpi_card`
  - `src/components/sidebar.py`: navigation from Dash `page_registry`
- Page packages
  - `cursor_usage`: data load/filter + chart/table builders + KPI cards
  - `apac_dot_due_date`: multi-dataset pivot/table flow + clear callbacks
  - `hamm_overview`: cadence-aware aggregation + table/chart builders
  - `dashboard_home.py`: static home navigation
- Chart surface
  - `src/charts/chart_builder.py`: generic figure builder
  - `src/charts/table_builder.py`: generic DataTable builder
  - `src/charts/empty_states.py`: empty/error placeholders
  - `src/charts/specs.py`: `ChartSpec`, `TableSpec`

## Architecture Relationships

- Page callbacks orchestrate; data transformations are delegated to each page `_data_loader.py` and helper modules.
- Rendering contracts are centralized in `src/charts/*` and reused across pages.
- Auth decides whether user sees login layout or authenticated shell (`sidebar + page_container`).
