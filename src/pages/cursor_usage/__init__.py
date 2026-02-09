"""Cursor Usage Dashboard page."""
import dash

from ._layout import build_layout
from . import _callbacks  # noqa: F401


dash.register_page(
    __name__,
    path="/cursor-usage",
    name="Cursor Usage",
    order=1,
    layout=build_layout,
)
