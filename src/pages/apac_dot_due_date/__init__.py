"""APAC DOT Due Date Dashboard page."""
import dash

from ._layout import build_layout


def layout():
    """APAC DOT Due Date Dashboard layout."""
    return build_layout()


# Register page with Dash - must come after layout() definition
dash.register_page(__name__, path="/apac-dot-due-date", name="APAC DOT Due Date", order=2, layout=layout)

# Import _callbacks to trigger callback registration via @callback decorator
from . import _callbacks  # noqa: F401
