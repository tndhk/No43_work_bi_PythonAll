from dash import Input, Output, callback, html, dash_table
import pandas as pd

from src.data.parquet_reader import ParquetReader


def register_callbacks():
    """コールバックを登録"""
    
    @callback(
        Output("dataset-dropdown", "options"),
        Input("dataset-dropdown", "id"),  # 初期化トリガー
    )
    def load_dataset_options(_):
        """データセット一覧を読み込む"""
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
        """データセットプレビューを更新"""
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
