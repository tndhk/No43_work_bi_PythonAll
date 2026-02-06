# Frontend Architecture Codemap

Generated: 2026-02-06

## Overview

The frontend is a multi-page Plotly Dash application with sidebar navigation, interactive charts, filters, and KPI cards. It uses Dash's Pages API for multi-page routing and Dash Bootstrap Components for responsive UI.

## Component Hierarchy

```
app.py (Entry Point)
    ↓
create_layout() [src/layout.py]
    ├── create_sidebar() [src/components/sidebar.py]
    │   ├── Navigation links to pages
    │   └── Logo/branding
    │
    └── page_container (Dash Pages API)
        ├── src/pages/dashboard_home.py
        ├── src/pages/...
        └── etc.

Components [src/components/]
├── sidebar.py
│   └── create_sidebar() → Div
│
├── filters.py
│   ├── create_category_filter() → dcc.Dropdown
│   ├── create_date_range_filter() → dcc.DatePickerRange
│   └── create_custom_filter() → html.Div
│
└── cards.py
    └── create_kpi_card(value, label, icon) → dbc.Card
```

## Module Dependency Map

```
src/layout.py
├── Imports: dash, src.components.sidebar
└── Exports: create_layout() → html.Div

src/components/sidebar.py
├── Imports: dash, dash_bootstrap_components
└── Exports: create_sidebar() → html.Div

src/components/filters.py
├── Imports: dash, src.data.filter_engine
└── Exports:
    ├── create_category_filter()
    ├── create_date_range_filter()
    └── create_custom_filter()

src/components/cards.py
├── Imports: dash_bootstrap_components
└── Exports: create_kpi_card()

src/pages/*.py
├── Imports: dash, src.data.parquet_reader, src.charts.templates
└── Exports: layout (dcc.Location → page content)
```

## Page Structure Template

Each page in `src/pages/` follows this pattern:

```python
# src/pages/page_name.py
import dash
from dash import dcc, html, callback, Input, Output
from src.data.parquet_reader import read_parquet
from src.charts.templates import create_line_chart

dash.register_page(__name__)

layout = html.Div([
    html.H1("Page Title"),
    # Filters
    dcc.Dropdown(id="filter-1", ...),
    # Charts
    dcc.Graph(id="chart-1"),
])

@callback(
    Output("chart-1", "figure"),
    Input("filter-1", "value"),
)
def update_chart(selected_value):
    df = read_parquet("s3://bucket/dataset.parquet")
    filtered_df = df[df["column"] == selected_value]
    return create_line_chart(filtered_df)
```

## Callback Pattern

```
User Interaction (click, select, change)
    ↓
[Input trigger]
    ↓
[Callback function]
    ├─ Read data from S3/cache
    ├─ Apply filters
    └─ Compute aggregations
    ↓
[Output update]
    ├─ Chart figure
    ├─ Table data
    └─ Card values
    ↓
Browser Re-render
```

## Data Access Flow

```
Page Callback
    ↓
[parquet_reader.read_parquet()]
    ├─ Check cache (TTL)
    ├─ If miss: fetch from S3
    └─ Load into pandas DataFrame
    ↓
[filter_engine.apply_filters()]
    ├─ Category filter
    ├─ Date range filter
    └─ Custom predicates
    ↓
[dataset_summarizer.summarize()]
    ├─ Count, sum, avg
    └─ Groupby aggregations
    ↓
[charts.templates]
    ├─ Format data for Plotly
    └─ Return figure
```

## Key Exports

### src/layout.py

```python
def create_layout() → html.Div
    # Main layout with sidebar + page_container
```

### src/components/sidebar.py

```python
def create_sidebar() → html.Div
    # Navigation sidebar with links to pages
```

### src/components/filters.py

```python
def create_category_filter(id, options) → dcc.Dropdown
def create_date_range_filter(id, start_date, end_date) → dcc.DatePickerRange
def create_custom_filter(id, component_type) → html.Div
```

### src/components/cards.py

```python
def create_kpi_card(value, label, icon="") → dbc.Card
    # KPI display card
```

### src/charts/templates.py

```python
def create_line_chart(df, x, y) → go.Figure
def create_bar_chart(df, x, y) → go.Figure
def create_pie_chart(df, labels, values) → go.Figure
def create_scatter_plot(df, x, y) → go.Figure
# ... etc.
```

## Style & Theming

- **Theme**: Bootstrap (dbc.themes.BOOTSTRAP)
- **Colors**: Dash Bootstrap color palette
- **Responsive**: Mobile-friendly via Bootstrap grid
- **Layout**: Sidebar + main content area

## Authentication Integration

```
Browser Request
    ↓
[Dash-Auth Middleware]
    ├─ Check session cookie
    └─ If not authenticated:
        ├─ Redirect to login
        └─ Basic auth dialog
    ↓
[User authenticates]
    ├─ Verify credentials (from .env)
    └─ Create session
    ↓
[Access granted to pages]
```

## Performance Optimizations

1. **Caching**: TTL cache in memory (300-3600s)
2. **Lazy Loading**: Load Parquet partitions on demand
3. **Column Selection**: Read only needed columns from Parquet
4. **Aggregation Pushdown**: Compute in Parquet layer if possible
5. **Callback Debouncing**: Use `dash_defer` for expensive operations

## Page Registry

Pages are auto-discovered from `src/pages/` directory:
- Each `.py` file in `src/pages/` is a page
- Must include `dash.register_page(__name__)`
- URL path = filename (e.g., `page_name.py` → `/page_name`)

Example:
```
src/pages/
├── __init__.py
├── dashboard_home.py → /
├── sales_analysis.py → /sales-analysis
└── inventory_report.py → /inventory-report
```

## Phase 2: LLM Chat Panel

Chat UI will be added as a reusable component:

```python
# src/components/chat_panel.py
def create_chat_panel(dataset_id) → html.Div
    # Chat interface + message history
```

Integrated into pages via:
```python
dcc.Tabs([
    dcc.Tab(label="Dashboard", children=[...]),
    dcc.Tab(label="Ask AI", children=[create_chat_panel(dataset_id)]),
])
```
