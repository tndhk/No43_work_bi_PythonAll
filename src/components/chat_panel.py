"""Chat panel UI components for LLM interaction."""
from dash import dcc, html


def create_chat_panel() -> html.Div:
    """Create the chat side panel component.

    Returns:
        Div containing the chat panel with header, messages, and input area.
    """
    return html.Div(
        id="chat-panel",
        className="chat-panel",
        children=[
            # Header
            html.Div(
                className="chat-panel-header",
                children=[
                    html.Span(
                        "AI Data Assistant",
                        className="chat-panel-title",
                    ),
                    html.Button(
                        "x",
                        id="chat-close-button",
                        className="chat-close-button",
                        n_clicks=0,
                    ),
                ],
            ),
            # Messages area
            html.Div(
                id="chat-messages",
                className="chat-messages",
                children=[],
            ),
            # Input area
            html.Div(
                className="chat-input-area",
                children=[
                    dcc.Textarea(
                        id="chat-input",
                        className="chat-input",
                        placeholder="質問を入力... (Shift+Enterで送信)",
                        style={"resize": "none"},
                    ),
                    html.Button(
                        "Send",
                        id="chat-send-button",
                        className="chat-send-button",
                        n_clicks=0,
                    ),
                ],
            ),
        ],
    )


def create_chat_toggle_button() -> html.Button:
    """Create the floating toggle button for opening the chat panel.

    Returns:
        Button component for toggling the chat panel.
    """
    return html.Button(
        "AI",
        id="chat-toggle-button",
        className="chat-toggle-button",
        n_clicks=0,
    )
