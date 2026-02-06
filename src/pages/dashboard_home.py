"""Dashboard home page."""
import dash
from dash import html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
from src.data.parquet_reader import ParquetReader

dash.register_page(__name__, path="/", name="Home", order=0)


def layout():
    """Home page layout."""
    return html.Div([
        html.H1("BI Dashboard", className="mb-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("データセット選択"),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id="dataset-dropdown",
                            placeholder="データセットを選択...",
                        ),
                    ])
                ], className="mb-4"),
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("プレビュー"),
                    dbc.CardBody([
                        html.Div(id="data-preview")
                    ])
                ]),
            ], width=12)
        ]),
        dcc.Store(id="dataset-store"),
    ])


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
        return html.P("データセットを選択してください", className="text-muted")

    try:
        reader = ParquetReader()
        df = reader.read_dataset(dataset_id)

        return dash_table.DataTable(
            data=df.head(100).to_dict("records"),
            columns=[{"name": c, "id": c} for c in df.columns],
            page_size=20,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
        )
    except FileNotFoundError:
        return html.P("データセットが見つかりません", className="text-danger")
    except Exception as e:
        return html.P(f"エラー: {str(e)}", className="text-danger")
