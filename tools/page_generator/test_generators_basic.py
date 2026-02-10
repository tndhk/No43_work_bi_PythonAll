"""Basic tests for code generators.

Tests that generators can produce valid Python code from test_complex.yaml.
"""
import ast
from pathlib import Path
import pytest

from tools.page_generator.parser import load_page_spec
from tools.page_generator.generators import (
    generate_constants,
    generate_layout,
    generate_filters,
)


@pytest.fixture
def complex_spec():
    """Load test_complex.yaml as PageSpec."""
    yaml_path = Path(__file__).parent / "test_complex.yaml"
    return load_page_spec(yaml_path)


def test_generate_constants_valid_syntax(complex_spec):
    """Test that generate_constants produces valid Python syntax."""
    code = generate_constants(complex_spec)

    # Should be able to parse as valid Python
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated constants.py has invalid syntax: {e}\n\nGenerated code:\n{code}")

    # Should contain expected elements
    assert "DASHBOARD_ID" in code
    assert "DATASET_ID" in code
    assert "ID_PREFIX" in code
    assert "COLUMN_MAP" in code
    assert "Auto-generated from page_spec.yaml" in code

    # Should contain filter IDs
    assert "FILTER_ID_" in code

    # Should contain component IDs
    assert any(x in code for x in ["CHART_ID_", "TABLE_ID_", "KPI_ID_"])

    # Should contain chart/table specs
    assert "_SPEC: ChartSpec" in code or "_SPEC: TableSpec" in code


def test_generate_layout_valid_syntax(complex_spec):
    """Test that generate_layout produces valid Python syntax."""
    code = generate_layout(complex_spec)

    # Should be able to parse as valid Python
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated layout.py has invalid syntax: {e}\n\nGenerated code:\n{code}")

    # Should contain expected elements
    assert "def build_layout()" in code
    assert "Auto-generated from page_spec.yaml" in code

    # Should contain helper functions
    assert "def _chart_card(" in code
    assert "def _table_card(" in code

    # Should contain dash components
    assert "dbc.Row" in code
    assert "dbc.Col" in code
    assert "dcc.Loading" in code

    # Should import from _constants and _filters
    assert "from ._constants import" in code
    assert "from ._filters import build_filter_layout" in code
    assert "from ._data_loader import load_filter_options" in code


def test_generate_filters_valid_syntax(complex_spec):
    """Test that generate_filters produces valid Python syntax."""
    code = generate_filters(complex_spec)

    # Should be able to parse as valid Python
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated filters.py has invalid syntax: {e}\n\nGenerated code:\n{code}")

    # Should contain expected elements
    assert "def build_filter_layout(" in code
    assert "Auto-generated from page_spec.yaml" in code

    # Should contain filter creation calls
    assert "create_slicer_filter" in code or "create_category_filter" in code or "create_chip_group_filter" in code

    # Should import from _constants
    assert "from ._constants import" in code


def test_constants_contains_all_filter_ids(complex_spec):
    """Test that constants.py contains all filter IDs from spec."""
    code = generate_constants(complex_spec)

    for filter_spec in complex_spec.filters:
        # Remove prefix to get the constant name
        filter_id_clean = filter_spec.id.replace(complex_spec.metadata.id_prefix, "")
        const_name = f"FILTER_ID_{filter_id_clean.upper().replace('-', '_')}"
        assert const_name in code, f"Expected {const_name} in generated constants"


def test_constants_contains_all_component_ids(complex_spec):
    """Test that constants.py contains all component IDs from spec."""
    code = generate_constants(complex_spec)

    for component in complex_spec.components:
        # Remove prefix to get the constant name
        comp_id_clean = component.id.replace(complex_spec.metadata.id_prefix, "")
        if component.type == "chart":
            const_name = f"CHART_ID_{comp_id_clean.upper().replace('-', '_')}"
        elif component.type == "table":
            const_name = f"TABLE_ID_{comp_id_clean.upper().replace('-', '_')}"
        elif component.type == "kpi":
            const_name = f"KPI_ID_{comp_id_clean.upper().replace('-', '_')}"
        else:
            continue

        assert const_name in code, f"Expected {const_name} in generated constants"


def test_constants_contains_chart_specs(complex_spec):
    """Test that constants.py contains ChartSpec definitions."""
    code = generate_constants(complex_spec)

    chart_components = [c for c in complex_spec.components if c.type == "chart"]
    if chart_components:
        assert "ChartSpec(" in code
        assert "chart_type=" in code
        assert "x_column=" in code
        assert "y_columns=" in code


def test_constants_contains_table_specs(complex_spec):
    """Test that constants.py contains TableSpec definitions."""
    code = generate_constants(complex_spec)

    table_components = [c for c in complex_spec.components if c.type == "table"]
    if table_components:
        assert "TableSpec(" in code
        assert "style_table=" in code or "sort_action=" in code


def test_layout_contains_all_components(complex_spec):
    """Test that layout.py references all components from spec."""
    code = generate_layout(complex_spec)

    for component in complex_spec.components:
        comp_id_clean = component.id.replace(complex_spec.metadata.id_prefix, "")
        if component.type == "chart":
            const_name = f"CHART_ID_{comp_id_clean.upper().replace('-', '_')}"
        elif component.type == "table":
            const_name = f"TABLE_ID_{comp_id_clean.upper().replace('-', '_')}"
        elif component.type == "kpi":
            const_name = f"KPI_ID_{comp_id_clean.upper().replace('-', '_')}"
        else:
            continue

        assert const_name in code, f"Expected {const_name} referenced in layout"


def test_filters_contains_all_filter_types(complex_spec):
    """Test that filters.py handles all filter types in spec."""
    code = generate_filters(complex_spec)

    filter_types = {f.type for f in complex_spec.filters}

    if "slicer" in filter_types:
        assert "create_slicer_filter" in code
    if "category" in filter_types or "dropdown" in filter_types:
        assert "create_category_filter" in code
    if "chip_group" in filter_types:
        assert "create_chip_group_filter" in code


def test_generated_code_imports_are_valid(complex_spec):
    """Test that all generated files have valid import statements."""
    for generator, filename in [
        (generate_constants, "constants.py"),
        (generate_layout, "layout.py"),
        (generate_filters, "filters.py"),
    ]:
        code = generator(complex_spec)

        # Should have at least some imports
        assert "import " in code or "from " in code, f"{filename} has no import statements"

        # The full code should parse without errors (includes multi-line imports)
        try:
            ast.parse(code)
        except SyntaxError as e:
            pytest.fail(f"{filename} has invalid syntax (possibly in imports): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
