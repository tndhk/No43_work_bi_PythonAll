"""APAC DOT Due Date Dashboard page."""
import dash

from ._layout import build_layout
from . import _callbacks  # noqa: F401


dash.register_page(
    __name__,
    path="/apac-dot-due-date",
    name="APAC DOT Due Date",
    order=2,
    layout=build_layout,
)
