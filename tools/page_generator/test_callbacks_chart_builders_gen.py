"""Tests for callbacks and chart_builders code generators.

Tests that generators can produce valid Python code for _callbacks.py
and _chart_builders.py from test_complex.yaml.
"""
import ast
from pathlib import Path
import pytest

from tools.page_generator.parser import load_page_spec
from tools.page_generator.generators import (
    generate_callbacks,
    generate_chart_builders,
)


@pytest.fixture
def complex_spec():
    """Load test_complex.yaml as PageSpec."""
    yaml_path = Path(__file__).parent / "test_complex.yaml"
    return load_page_spec(yaml_path)


# =============================================================================
# Callbacks Generator Tests
# =============================================================================

def test_generate_callbacks_valid_syntax(complex_spec):
    """Test that generate_callbacks produces valid Python syntax."""
    code = generate_callbacks(complex_spec)

    # Should be able to parse as valid Python
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated callbacks.py has invalid syntax: {e}\n\nGenerated code:\n{code}")

    # Should contain expected elements
    assert "Auto-generated from page_spec.yaml" in code
    assert "def update_dashboard(" in code
    assert "@callback" in code


def test_callbacks_has_required_imports(complex_spec):
    """Test that callbacks.py has all required imports."""
    code = generate_callbacks(complex_spec)

    # Core imports
    assert "from dash import callback, Input, Output" in code
    assert "import plotly.graph_objects as go" in code
    assert "from src.data.parquet_reader import ParquetReader" in code

    # Helper imports
    assert "from src.utils.callback_helpers import ensure_list" in code
    assert "from src.components.cards import create_kpi_card" in code

    # Local imports
    assert "from ._constants import" in code
    assert "from ._data_loader import" in code
    assert "from ._chart_builders import" in code


def test_callbacks_has_correct_outputs_inputs(complex_spec):
    """Test that callback has correct number of Outputs and Inputs."""
    code = generate_callbacks(complex_spec)

    # Count components (Outputs)
    kpi_count = len([c for c in complex_spec.components if c.type == "kpi"])
    chart_count = len([c for c in complex_spec.components if c.type == "chart"])
    table_count = len([c for c in complex_spec.components if c.type == "table"])
    total_outputs = kpi_count + chart_count + table_count

    # Count filters (Inputs)
    total_inputs = len(complex_spec.filters)

    # Check Output declarations
    assert code.count("Output(") == total_outputs, f"Expected {total_outputs} Output declarations"

    # Check Input declarations
    assert code.count("Input(") == total_inputs, f"Expected {total_inputs} Input declarations"


def test_callbacks_has_kpi_computation(complex_spec):
    """Test that callbacks includes KPI computation logic."""
    code = generate_callbacks(complex_spec)

    kpi_components = [c for c in complex_spec.components if c.type == "kpi"]
    if kpi_components:
        # Should have create_kpi_card calls
        assert "create_kpi_card" in code

        # Should have value computation based on agg_func
        for kpi in kpi_components:
            kpi_var = kpi.id.replace("-", "_")
            assert f"{kpi_var}_value" in code or f"{kpi_var}_card" in code


def test_callbacks_has_chart_builder_calls(complex_spec):
    """Test that callbacks calls chart builder functions."""
    code = generate_callbacks(complex_spec)

    chart_components = [c for c in complex_spec.components if c.type == "chart"]
    for chart in chart_components:
        func_name = f"build_{chart.id.replace('-', '_')}"
        assert func_name in code, f"Expected {func_name} call in callbacks"


def test_callbacks_has_table_builder_calls(complex_spec):
    """Test that callbacks calls table builder functions."""
    code = generate_callbacks(complex_spec)

    table_components = [c for c in complex_spec.components if c.type == "table"]
    for table in table_components:
        func_name = f"build_{table.id.replace('-', '_')}"
        assert func_name in code, f"Expected {func_name} call in callbacks"


def test_callbacks_has_data_transform_calls(complex_spec):
    """Test that callbacks calls data transform functions when needed."""
    code = generate_callbacks(complex_spec)

    components_with_transform = [c for c in complex_spec.components if c.data_transform]
    for component in components_with_transform:
        func_name = f"build_{component.id.replace('-', '_')}"
        # Should import and call the transform function
        assert func_name in code


def test_callbacks_has_error_handling(complex_spec):
    """Test that callbacks includes error handling."""
    code = generate_callbacks(complex_spec)

    assert "try:" in code
    assert "except Exception as exc:" in code
    assert "error_msg" in code or "error_fig" in code


def test_callbacks_returns_correct_tuple(complex_spec):
    """Test that callbacks returns tuple with all component outputs."""
    code = generate_callbacks(complex_spec)

    # Should have return statement in try block
    assert "return (" in code

    # Count return values in try block
    kpi_count = len([c for c in complex_spec.components if c.type == "kpi"])
    chart_count = len([c for c in complex_spec.components if c.type == "chart"])
    table_count = len([c for c in complex_spec.components if c.type == "table"])

    # Check for component references in return
    for component in complex_spec.components:
        comp_var = component.id.replace("-", "_")
        if component.type == "kpi":
            assert f"{comp_var}_card" in code
        elif component.type == "chart":
            assert f"{comp_var}_fig" in code
        elif component.type == "table":
            assert f"{comp_var}_table" in code


def test_callbacks_has_load_and_filter_data_call(complex_spec):
    """Test that callbacks calls load_and_filter_data."""
    code = generate_callbacks(complex_spec)

    assert "load_and_filter_data(" in code
    assert "filter_pairs = [" in code
    assert "ensure_list(" in code


def test_callbacks_clear_callbacks_registration(complex_spec):
    """Test that callbacks registers clear callbacks when needed."""
    code = generate_callbacks(complex_spec)

    has_clear_buttons = any(f.has_clear_button for f in complex_spec.filters)

    if has_clear_buttons:
        assert "register_clear_callbacks" in code
        assert "CLEAR_PAIRS" in code
    # If no clear buttons, may or may not include (template decision)


# =============================================================================
# Chart Builders Generator Tests
# =============================================================================

def test_generate_chart_builders_valid_syntax(complex_spec):
    """Test that generate_chart_builders produces valid Python syntax."""
    code = generate_chart_builders(complex_spec)

    # Should be able to parse as valid Python
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated chart_builders.py has invalid syntax: {e}\n\nGenerated code:\n{code}")

    # Should contain expected elements
    assert "Auto-generated from page_spec.yaml" in code


def test_chart_builders_has_required_imports(complex_spec):
    """Test that chart_builders.py has all required imports."""
    code = generate_chart_builders(complex_spec)

    # Core imports
    assert "import pandas as pd" in code
    assert "import plotly.graph_objects as go" in code

    # Chart/table builders
    assert "from src.charts.chart_builder import build_chart" in code
    assert "from src.charts.table_builder import build_table" in code
    assert "from src.charts.layout_helpers import apply_compact_chart_layout" in code

    # Local imports
    assert "from ._constants import" in code


def test_chart_builders_has_chart_functions(complex_spec):
    """Test that chart_builders.py has builder functions for all charts."""
    code = generate_chart_builders(complex_spec)

    chart_components = [c for c in complex_spec.components if c.type == "chart"]
    for chart in chart_components:
        func_name = f"def build_{chart.id.replace('-', '_')}(df: pd.DataFrame) -> go.Figure:"
        assert func_name in code, f"Expected {func_name} in chart_builders"

        # Should call build_chart
        spec_name = f"{chart.id.upper().replace('-', '_')}_SPEC"
        assert f"build_chart(df, {spec_name})" in code


def test_chart_builders_has_table_functions(complex_spec):
    """Test that chart_builders.py has builder functions for all tables."""
    code = generate_chart_builders(complex_spec)

    table_components = [c for c in complex_spec.components if c.type == "table"]
    for table in table_components:
        func_name = f"def build_{table.id.replace('-', '_')}(df: pd.DataFrame) -> tuple[str, Any]:"
        assert func_name in code, f"Expected {func_name} in chart_builders"

        # Should call build_table
        spec_name = f"{table.id.upper().replace('-', '_')}_SPEC"
        assert f"build_table(df, {spec_name})" in code


def test_chart_builders_applies_layout_adjustments(complex_spec):
    """Test that chart builders apply layout adjustments when specified."""
    code = generate_chart_builders(complex_spec)

    # Find components with layout_adjustments
    components_with_adjustments = [
        c for c in complex_spec.components
        if c.type == "chart" and hasattr(c, 'layout_adjustments') and c.layout_adjustments
    ]

    # If test_complex.yaml doesn't have layout_adjustments, skip specific checks
    if not components_with_adjustments:
        # Just verify the basic structure is present
        assert "apply_compact_chart_layout" in code or "def build_" in code
        return

    for component in components_with_adjustments:
        func_name = f"build_{component.id.replace('-', '_')}"

        # Check for specific adjustments
        if hasattr(component.layout_adjustments, "text_position") and component.layout_adjustments.text_position:
            assert "textposition=" in code

        if (hasattr(component.layout_adjustments, "margin") and component.layout_adjustments.margin) or \
           (hasattr(component.layout_adjustments, "legend") and component.layout_adjustments.legend):
            assert "apply_compact_chart_layout" in code


def test_chart_builders_has_correct_return_types(complex_spec):
    """Test that builder functions have correct return type annotations."""
    code = generate_chart_builders(complex_spec)

    chart_components = [c for c in complex_spec.components if c.type == "chart"]
    for chart in chart_components:
        # Should return go.Figure
        func_line = f"def build_{chart.id.replace('-', '_')}(df: pd.DataFrame) -> go.Figure:"
        assert func_line in code

    table_components = [c for c in complex_spec.components if c.type == "table"]
    for table in table_components:
        # Should return tuple[str, Any]
        func_line = f"def build_{table.id.replace('-', '_')}(df: pd.DataFrame) -> tuple[str, Any]:"
        assert func_line in code


def test_chart_builders_has_docstrings(complex_spec):
    """Test that all builder functions have docstrings."""
    code = generate_chart_builders(complex_spec)

    chart_and_table_components = [
        c for c in complex_spec.components
        if c.type in ["chart", "table"]
    ]

    for component in chart_and_table_components:
        # Each function should have a docstring with title
        assert f'"""Render {component.title}.' in code or f'Render {component.title}' in code


# =============================================================================
# Integration Tests
# =============================================================================

def test_callbacks_and_chart_builders_consistency(complex_spec):
    """Test that callbacks and chart_builders reference the same functions."""
    callbacks_code = generate_callbacks(complex_spec)
    builders_code = generate_chart_builders(complex_spec)

    # All chart/table builder function calls in callbacks should be defined in chart_builders
    chart_and_table = [c for c in complex_spec.components if c.type in ["chart", "table"]]

    for component in chart_and_table:
        func_name = f"build_{component.id.replace('-', '_')}"

        # Should be called in callbacks
        assert func_name in callbacks_code, f"{func_name} should be called in callbacks"

        # Should be defined in chart_builders
        assert f"def {func_name}(" in builders_code, f"{func_name} should be defined in chart_builders"


def test_complete_code_generation_pipeline(complex_spec):
    """Test that both generators produce valid code that could work together."""
    callbacks_code = generate_callbacks(complex_spec)
    builders_code = generate_chart_builders(complex_spec)

    # Both should be valid Python
    try:
        ast.parse(callbacks_code)
    except SyntaxError as e:
        pytest.fail(f"Callbacks code invalid: {e}")

    try:
        ast.parse(builders_code)
    except SyntaxError as e:
        pytest.fail(f"Chart builders code invalid: {e}")

    # Callbacks should import from chart_builders
    assert "from ._chart_builders import" in callbacks_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
