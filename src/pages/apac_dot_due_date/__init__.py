"""APAC DOT Due Date Dashboard page."""
import dash

from src.pages.apac_dot_due_date._layout import build_layout

# Register page with Dash
dash.register_page(__name__, path="/apac-dot-due-date", name="APAC DOT Due Date", order=2)

# Import _callbacks to trigger callback registration via @callback decorator
from src.pages.apac_dot_due_date import _callbacks  # noqa: F401, E402


def layout():
    """APAC DOT Due Date Dashboard layout."""
    return build_layout()
