"""Custom Plotly theme for Minimal Luxury dark theme."""
import plotly.graph_objects as go

# Color palette based on accent gold
PLOTLY_COLOR_PALETTE = [
    "#c9a55c",  # Warm gold (primary accent)
    "#3ecfb4",  # Teal/turquoise
    "#dbb76e",  # Lighter gold
    "#9a7d3f",  # Darker gold
    "#f0b429",  # Amber/yellow
    "#ef6461",  # Coral/red
]

# Plotly template configuration
PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        # Colors
        colorway=PLOTLY_COLOR_PALETTE,
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent to match card background
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent
        
        # Fonts
        font=dict(
            family="Plus Jakarta Sans, sans-serif",
            size=12,
            color="#8b8d9a",  # text-secondary
        ),
        title=dict(
            font=dict(
                family="Syne, sans-serif",
                size=18,
                color="#e8e6e1",  # text-primary
            ),
        ),
        
        # Axes
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.06)",  # border-subtle
            gridwidth=1,
            linecolor="rgba(255, 255, 255, 0.06)",
            zeroline=False,
            tickfont=dict(color="#8b8d9a"),
            titlefont=dict(color="#e8e6e1", family="Plus Jakarta Sans"),
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.06)",  # border-subtle
            gridwidth=1,
            linecolor="rgba(255, 255, 255, 0.06)",
            zeroline=False,
            tickfont=dict(color="#8b8d9a"),
            titlefont=dict(color="#e8e6e1", family="Plus Jakarta Sans"),
        ),
        
        # Legend
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255, 255, 255, 0.06)",
            borderwidth=1,
            font=dict(color="#8b8d9a", family="Plus Jakarta Sans"),
        ),
        
        # Hover
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#1c1c27",  # bg-card
            bordercolor="rgba(201, 165, 92, 0.3)",  # border-accent
            font=dict(color="#e8e6e1", family="Plus Jakarta Sans"),
        ),
    )
)


def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply custom theme to a Plotly figure.
    
    Args:
        fig: Plotly figure to style
        
    Returns:
        Styled figure
    """
    fig.update_layout(template=PLOTLY_TEMPLATE)
    return fig
