from dash import Dash
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

from src.auth.basic_auth import setup_auth
from src.core.cache import init_cache
from src.layout import create_layout

load_dotenv()

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="src/pages",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="BI Dashboard",
    suppress_callback_exceptions=True,
)

setup_auth(app)
init_cache(app.server)
app.layout = create_layout()

server = app.server

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
