from dash import html, dcc
import dash_bootstrap_components as dbc


def create_layout() -> dbc.Container:
    """メインレイアウトを作成"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("BI Dashboard", className="mb-4"),
            ])
        ]),
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
    ], fluid=True, className="p-4")
