"""Dashboard home page."""
import dash
from dash import html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
from src.data.parquet_reader import ParquetReader

dash.register_page(__name__, path="/", name="Home", order=0)


def layout():
    """Home page layout."""
    return html.Div([
        html.H1("BI Dashboard", className="mb-4 animate-fade-in-up"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("データセット選択", className="filter-header"),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id="dataset-dropdown",
                            placeholder="データセットを選択...",
                        ),
                    ])
                ], className="filter-card mb-4 animate-fade-in-up-delay-1"),
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("プレビュー", className="filter-header"),
                    dbc.CardBody([
                        html.Div(id="data-preview")
                    ])
                ], className="animate-fade-in-up-delay-2"),
            ], width=12)
        ]),
        dcc.Store(id="dataset-store"),
    ], className="page-container page-load")


@callback(
    Output("dataset-dropdown", "options"),
    Input("dataset-dropdown", "id"),
)
def load_dataset_options(_):
    """Load dataset list."""
    try:
        reader = ParquetReader()
        datasets = reader.list_datasets()
        return [{"label": d, "value": d} for d in datasets]
    except Exception:
        return []


@callback(
    Output("data-preview", "children"),
    Input("dataset-dropdown", "value"),
)
def update_preview(dataset_id):
    """Update dataset preview."""
    if not dataset_id:
        return html.P("データセットを選択してください", className="text-secondary")

    try:
        reader = ParquetReader()
        df = reader.read_dataset(dataset_id)

        return dash_table.DataTable(
            data=df.head(100).to_dict("records"),
            columns=[{"name": c, "id": c} for c in df.columns],
            page_size=20,
            style_table={"overflowX": "auto", "backgroundColor": "var(--bg-card)", "color": "var(--text-primary)"},
            style_cell={"textAlign": "left", "backgroundColor": "var(--bg-card)", "color": "var(--text-secondary)", "border": "1px solid var(--border-subtle)"},
            style_header={"backgroundColor": "var(--bg-elevated)", "color": "var(--text-primary)", "fontWeight": "600"},
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "var(--bg-surface)",
                }
            ],
        )
    except FileNotFoundError:
        return html.P("データセットが見つかりません", className="text-danger")
    except Exception as e:
        return html.P(f"エラー: {str(e)}", className="text-danger")
