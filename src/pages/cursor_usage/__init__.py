"""Cursor Usage Dashboard page."""
import dash
from ._layout import build_layout


def layout():
    """Return Cursor Usage Dashboard layout."""
    return build_layout()


dash.register_page(__name__, path="/cursor-usage", name="Cursor Usage", order=1, layout=layout)

# Import callbacks to register them with Dash
from . import _callbacks  # noqa: F401, E402
