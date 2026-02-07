from dash import Dash
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

from src.auth.flask_login_setup import init_login_manager
from src.auth.login_callbacks import register_login_callbacks
from src.auth.layout_callbacks import register_layout_callbacks
from src.components.sidebar_callbacks import register_sidebar_callbacks
from src.core.cache import init_cache
from src.layout import create_layout
from src.data.config import settings

load_dotenv()

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="src/pages",
    external_stylesheets=[
        # Minimal Bootstrap - only for grid system and utilities
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
    ],
    title="BI Dashboard",
    suppress_callback_exceptions=True,
)

# Package-style pages require explicit import because Dash's page scanner
# skips __init__.py (starts with '_'). See: dash/_pages.py line 431
import src.pages.apac_dot_due_date  # noqa: F401

# Initialize Flask-Login
app.server.config["SECRET_KEY"] = settings.secret_key
init_login_manager(app.server)

# Register callbacks
register_login_callbacks(app)
register_layout_callbacks(app)
register_sidebar_callbacks(app)

# Initialize cache
init_cache(app.server)

# Set layout
app.layout = create_layout()

server = app.server

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
