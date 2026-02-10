# Architecture Codemap

Freshness (UTC): 2026-02-10T15:30:00Z
Analysis Scope: `app.py`, `src/`, `backend/`, `tools/`

## High-Level Structure

1. Runtime app: `app.py` (Dash app init, auth wiring, callback registration, page imports)
2. Frontend/UI: `src/pages/`, `src/components/`, `src/auth/`, `src/layout.py`
3. Data access: `src/data/`, `src/core/cache.py`, `src/utils/`
4. Visualization contracts: `src/charts/`
5. Offline ingestion: `backend/etl/`, `backend/scripts/`, `backend/config/`
6. CI/CD: `.github/workflows/ci.yml` (lint, typecheck, test -- 3 parallel jobs)
7. Development tools: `tools/page_generator/`, `scripts/`

## Architecture Relationships

```text
Browser
  -> app.py (Dash/Flask)
    -> src/auth/* (login/session)
    -> src/layout.py + src/auth/layout_callbacks.py (authenticated shell)
    -> src/pages/* (Dash Pages)
      -> src/components/* (filters/cards/sidebar)
      -> src/data/* + src/core/cache.py (dataset load/filter)
      -> src/charts/* (figure/table build, layout_helpers)
      -> src/utils/* (callback_helpers, data_helpers, filter_helpers)
    -> S3/MinIO via src/data/s3_client.py + src/data/parquet_reader.py

backend/scripts/*
  -> backend/etl/*
    -> src/data/{s3_client,type_inferrer,csv_parser,config}
    -> S3/MinIO (Parquet write)

tools/page_generator/cli.py (dev-time)
  -> tools/page_generator/parser.py (load page_spec.yaml)
  -> tools/page_generator/schema.py (Pydantic validation: PageSpec model)
  -> tools/page_generator/operations.py (data transform runtime)
  -> tools/page_generator/generators/* (code generation per module)
  -> tools/page_generator/templates/*.j2 (Jinja2 templates)
  -> generates src/pages/{name}/* (canonical files + _custom_logic.py)

scripts/scaffold_page.py (dev-time)
  -> generates src/pages/{name}/* (template-based)
```

## Page Package Structure (Tier 2)

Tier 2 pages use a canonical package layout. The hamm_overview page is the reference implementation.

```text
src/pages/{name}/
  __init__.py          -> dash.register_page + build_layout + import _callbacks
  page_spec.yaml       -> declarative spec (metadata, columns, filters, layout, components, custom_logic)
  data_sources.yml     -> dataset binding
  SPEC.md              -> user-facing documentation
  _constants.py        -> IDs, COLUMN_MAP, ChartSpec/TableSpec instances, CLEAR_PAIRS
  _layout.py           -> build_layout(), _chart_card(), _table_card()
  _filters.py          -> build_filter_layout(opts)
  _data_loader.py      -> load_filter_options, load_and_filter_data, aggregation builders
  _callbacks.py        -> update_dashboard callback, KPI computation, register_clear_callbacks
  _chart_builders.py   -> build_*_table, build_*_chart (delegates to shared builders)
  _custom_logic.py     -> complex transformations not expressible in page_spec.yaml
```

`_custom_logic.py` is optional. It contains domain-specific transformation functions (e.g., cadence column generation, date formatting, display DataFrame preparation) that are imported and re-exported by `_data_loader.py`. The page_spec.yaml `custom_logic.imports` section declares which functions are needed.

## Dependency Listing (Top-Level Imports)

- `app.py` imports `src.auth.*`, `src.components.sidebar_callbacks`, `src.core.cache`, `src.layout`, `src.data.config`, and explicit page packages (`src.pages.apac_dot_due_date`, `src.pages.cursor_usage`, `src.pages.hamm_overview`).
- `src/pages/*` imports primarily from:
  - `src.data.parquet_reader`, `src.core.cache`, `src.data.filter_engine`, `src.data.data_source_registry`
  - `src.charts.chart_builder`, `src.charts.table_builder`, `src.charts.empty_states`, `src.charts.layout_helpers`
  - `src.charts.specs` (ChartSpec, TableSpec, COMPACT_STYLE_CELL, COMPACT_STYLE_HEADER)
  - `src.components.filters`, `src.components.cards`
  - `src.utils.callback_helpers`, `src.utils.data_helpers`, `src.utils.filter_helpers`
  - Intra-package: `_constants`, `_data_loader`, `_chart_builders`, `_filters`, `_custom_logic`
- `backend/etl/*` imports:
  - shared base `backend.etl.base_etl`
  - transformation helpers `src.data.csv_parser`, `src.data.type_inferrer`
  - masking `backend.etl.masking`
  - storage config/client `src.data.config`, `src.data.s3_client`
- `tools/page_generator/*` imports:
  - schema validation via `pydantic` (PageSpec, MetadataSpec, ComponentSpec, etc.)
  - YAML parsing via `yaml`
  - Jinja2 templates (`.j2` files in `templates/`)
  - code generation modules in `generators/` (constants, layout, filters, data_loader, callbacks, chart_builders)
  - runtime operations via `operations.py`
- `scripts/scaffold_page.py` uses template strings (no external page imports)
- `scripts/upload_csv.py` imports `backend.etl.etl_csv.CsvETL`

## Export Surface (Major Entrypoints)

- App/runtime: `create_layout`, `register_*_callbacks`, `init_login_manager`, `init_cache`
- Data layer: `ParquetReader`, `get_dataset_id`/`resolve_dataset_id`, `get_cached_dataset`, `apply_filters`
- UI builders: `build_chart`, `build_table`, `create_*_filter`, `create_kpi_card`, `create_kpi_card_with_delta`
- Chart layout: `apply_compact_chart_layout`
- Chart types: `bar`, `line`, `pie`, `stacked_bar`, `scatter`, `area`, `horizontal_bar`
- Callback helpers: `register_clear_callbacks`, `ensure_list`
- Data helpers: `safe_load_filter_options`, `strip_timezone`, `resolve_single_dataset_id`, `extract_unique_values`
- Filter helpers: `build_filter_set_from_map`
- ETL: `BaseETL`, `CsvETL`, `DomoApiETL`, `resolve_csv_path`, script `main()` functions
- Dev tools: `load_page_spec`, `cli_main` (page_generator), `scaffold_page.py` main(), `upload_csv.py` main()
- Page generator schema: `PageSpec`, `MetadataSpec`, `FilterSpec`, `ComponentSpec`, `ChartSpecYAML`, `TableSpecYAML`, `KPICardSpec`, `DataTransformSpec`

## Page Generator Detail

```text
tools/page_generator/
  __main__.py          -> entry point
  cli.py               -> CLI interface (cli_main)
  parser.py            -> load_page_spec (YAML -> PageSpec)
  schema.py            -> Pydantic models with cross-validators
  operations.py        -> data transform operation runtime
  generators/
    __init__.py
    constants_gen.py   -> generate _constants.py
    layout_gen.py      -> generate _layout.py
    filters_gen.py     -> generate _filters.py
    data_loader_gen.py -> generate _data_loader.py
    callbacks_gen.py   -> generate _callbacks.py
    chart_builders_gen.py -> generate _chart_builders.py
  templates/
    constants.py.j2
    layout.py.j2
    filters.py.j2
    data_loader.py.j2  -> supports custom_logic imports, derived column generation
    callbacks.py.j2
    chart_builders.py.j2
    custom_logic.py.j2
    new_page_spec.yaml -> starter template for new pages

schema.py validates:
  - Unique IDs across filters and components
  - Column references against column_map + derived_columns
  - Layout component_id references against defined components
  - Filter type requirements (column field for slicer/category/dropdown)
```

## CI/CD Pipeline

```text
.github/workflows/ci.yml
  triggers: push(main), pull_request(main)
  concurrency: cancel-in-progress per branch

  jobs (parallel):
    lint       -> ruff check src/
    typecheck  -> pip install requirements.txt + requirements-dev.txt -> mypy src/
    test       -> pip install requirements.txt + requirements-dev.txt -> pytest -v --tb=short
```

## Dependency Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Runtime dependencies (Dash, pandas, boto3, etc.) |
| `requirements-dev.txt` | Dev/test dependencies (pytest, ruff, mypy, moto) |
| `pyproject.toml` | Project metadata, tool configs (pytest, ruff, mypy, coverage) |
| `Dockerfile.dev` | Dev container (installs both requirements files) |

## Notes

- This codemap is derived from current repository imports/definitions only.
- No unverified external infrastructure assumptions are included.
- The `_custom_logic.py` pattern was introduced to separate non-declarative transformation logic from generated code, allowing page_generator to regenerate other files without overwriting custom logic.
