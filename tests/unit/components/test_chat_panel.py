"""Tests for chat panel UI components."""
from dash import html


def _find_component_by_id(component, target_id):
    """Recursively search for a component by ID."""
    if hasattr(component, "id") and component.id == target_id:
        return component
    if hasattr(component, "children"):
        children = component.children
        if children is None:
            return None
        if not isinstance(children, list):
            children = [children]
        for child in children:
            result = _find_component_by_id(child, target_id)
            if result is not None:
                return result
    return None


def _find_component_by_class(component, target_class):
    """Recursively search for a component by CSS class name."""
    if (
        hasattr(component, "className")
        and component.className
        and target_class in component.className
    ):
        return component
    if hasattr(component, "children"):
        children = component.children
        if children is None:
            return None
        if not isinstance(children, list):
            children = [children]
        for child in children:
            result = _find_component_by_class(child, target_class)
            if result is not None:
                return result
    return None


class TestCreateChatPanel:
    """Tests for create_chat_panel."""

    def test_returns_div(self):
        """Div component should be returned."""
        from src.components.chat_panel import create_chat_panel

        panel = create_chat_panel()
        assert isinstance(panel, html.Div)

    def test_has_panel_id(self):
        """Panel should have the correct ID."""
        from src.components.chat_panel import create_chat_panel

        panel = create_chat_panel()
        assert panel.id == "chat-panel"

    def test_has_chat_class(self):
        """Panel should have the correct CSS class."""
        from src.components.chat_panel import create_chat_panel

        panel = create_chat_panel()
        assert "chat-panel" in panel.className

    def test_contains_header(self):
        """Panel should contain a header section."""
        from src.components.chat_panel import create_chat_panel

        panel = create_chat_panel()
        header_found = _find_component_by_class(panel, "chat-panel-header")
        assert header_found is not None

    def test_contains_messages_area(self):
        """Panel should contain a messages area."""
        from src.components.chat_panel import create_chat_panel

        panel = create_chat_panel()
        messages = _find_component_by_id(panel, "chat-messages")
        assert messages is not None

    def test_contains_input_area(self):
        """Panel should contain an input area."""
        from src.components.chat_panel import create_chat_panel

        panel = create_chat_panel()
        input_area = _find_component_by_id(panel, "chat-input")
        assert input_area is not None

    def test_contains_send_button(self):
        """Panel should contain a send button."""
        from src.components.chat_panel import create_chat_panel

        panel = create_chat_panel()
        send_btn = _find_component_by_id(panel, "chat-send-button")
        assert send_btn is not None

    def test_contains_close_button(self):
        """Panel should contain a close button."""
        from src.components.chat_panel import create_chat_panel

        panel = create_chat_panel()
        close_btn = _find_component_by_id(panel, "chat-close-button")
        assert close_btn is not None


class TestCreateChatToggleButton:
    """Tests for create_chat_toggle_button."""

    def test_returns_button(self):
        """Button component should be returned."""
        from src.components.chat_panel import create_chat_toggle_button

        button = create_chat_toggle_button()
        assert isinstance(button, html.Button)

    def test_has_toggle_id(self):
        """Button should have the correct ID."""
        from src.components.chat_panel import create_chat_toggle_button

        button = create_chat_toggle_button()
        assert button.id == "chat-toggle-button"

    def test_has_toggle_class(self):
        """Button should have the correct CSS class."""
        from src.components.chat_panel import create_chat_toggle_button

        button = create_chat_toggle_button()
        assert "chat-toggle-button" in button.className
