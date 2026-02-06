from dash import Dash
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

from src.auth.basic_auth import setup_auth
from src.layout import create_layout
from src.callbacks import register_callbacks

# 環境変数を読み込み
load_dotenv()

# Dashアプリを作成
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="BI Dashboard",
)

# 認証を設定
setup_auth(app)

# レイアウトを設定
app.layout = create_layout()

# コールバックを登録
register_callbacks()

# サーバーを公開（Gunicorn用）
server = app.server

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
