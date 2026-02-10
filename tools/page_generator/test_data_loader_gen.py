"""Tests for data_loader.py.j2 template and generator."""
import ast
from pathlib import Path
import pytest

from tools.page_generator.parser import load_page_spec
from tools.page_generator.generators import generate_data_loader, generate_custom_logic


@pytest.fixture
def complex_spec():
    """Load test_complex.yaml as PageSpec."""
    yaml_path = Path(__file__).parent / "test_complex.yaml"
    return load_page_spec(yaml_path)


def test_generate_data_loader_syntax(complex_spec):
    """Test that generated _data_loader.py has valid Python syntax."""
    code = generate_data_loader(complex_spec)

    # Parse to check syntax
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated code has syntax error: {e}\n\nGenerated code:\n{code}")


def test_generate_data_loader_contains_functions(complex_spec):
    """Test that generated code contains expected functions."""
    code = generate_data_loader(complex_spec)

    # Check for required functions
    assert "def _prepare_base_df(df: pd.DataFrame) -> pd.DataFrame:" in code
    assert "def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:" in code
    assert "def load_and_filter_data(" in code

    # Check for build functions (components with data_transform)
    components_with_transform = [c for c in complex_spec.components if c.data_transform]
    assert len(components_with_transform) > 0, "Test spec should have components with data_transform"

    for component in components_with_transform:
        # Build function name removes prefix
        build_func = component.id.replace('-', '_').replace(complex_spec.metadata.id_prefix.replace('-', '_'), '')
        assert f"def build_{build_func}(df: pd.DataFrame) -> pd.DataFrame:" in code


def test_generate_data_loader_imports(complex_spec):
    """Test that generated code has correct imports."""
    code = generate_data_loader(complex_spec)

    # Required imports
    assert "import pandas as pd" in code
    assert "from src.data.parquet_reader import ParquetReader" in code
    assert "from src.core.cache import get_cached_dataset" in code
    assert "from src.utils.data_helpers import extract_unique_values" in code
    assert "from ._constants import COLUMN_MAP" in code


def test_generate_data_loader_derived_columns(complex_spec):
    """Test that derived columns are generated correctly."""
    code = generate_data_loader(complex_spec)

    # Check for derived column constants import
    if complex_spec.derived_columns:
        for col in complex_spec.derived_columns:
            col_name = col.name[1:].upper() if col.name.startswith('_') else col.name.upper()
            assert f"DERIVED_{col_name}" in code


def test_generate_data_loader_filter_operations(complex_spec):
    """Test that filter operations are generated correctly."""
    code = generate_data_loader(complex_spec)

    # Check for filter query operation
    has_filter = any(
        c.data_transform and c.data_transform.get('operations') and
        any(op.type == 'filter' for op in c.data_transform['operations'])
        for c in complex_spec.components if c.data_transform
    )

    if has_filter:
        # At least one filter operation should exist
        assert 'df.query(' in code or 'df[~df[' in code or 'df[df[' in code


def test_generate_data_loader_group_by_operations(complex_spec):
    """Test that group_by operations are generated correctly."""
    code = generate_data_loader(complex_spec)

    # Check for group_by operations
    has_groupby = any(
        c.data_transform and c.data_transform.get('operations') and
        any(op.type == 'group_by' for op in c.data_transform['operations'])
        for c in complex_spec.components if c.data_transform
    )

    if has_groupby:
        assert "df.groupby([" in code
        assert ".agg({" in code


def test_generate_data_loader_pivot_operations(complex_spec):
    """Test that pivot operations are generated correctly."""
    code = generate_data_loader(complex_spec)

    # Check for pivot operations
    has_pivot = any(
        c.data_transform and c.data_transform.get('operations') and
        any(op.type == 'pivot' for op in c.data_transform['operations'])
        for c in complex_spec.components if c.data_transform
    )

    if has_pivot:
        assert "df.pivot_table(" in code
        assert "index=[" in code
        assert "columns=[" in code
        assert "values=[" in code


def test_generate_data_loader_rename_operations(complex_spec):
    """Test that rename operations are generated correctly."""
    code = generate_data_loader(complex_spec)

    # Check for rename operations
    has_rename = any(
        c.data_transform and c.data_transform.get('operations') and
        any(op.type == 'rename' for op in c.data_transform['operations'])
        for c in complex_spec.components if c.data_transform
    )

    if has_rename:
        assert "df.rename(columns={" in code


def test_generate_data_loader_sort_operations(complex_spec):
    """Test that sort operations are generated correctly."""
    code = generate_data_loader(complex_spec)

    # Check for sort operations
    has_sort = any(
        c.data_transform and c.data_transform.get('operations') and
        any(op.type == 'sort' for op in c.data_transform['operations'])
        for c in complex_spec.components if c.data_transform
    )

    if has_sort:
        assert "df.sort_values(" in code


def test_generate_data_loader_add_column_operations(complex_spec):
    """Test that add_column operations are generated correctly."""
    code = generate_data_loader(complex_spec)

    # Check for add_column operations
    has_add_column = any(
        c.data_transform and c.data_transform.get('operations') and
        any(op.type == 'add_column' for op in c.data_transform['operations'])
        for c in complex_spec.components if c.data_transform
    )

    if has_add_column:
        # Should have column assignment
        assert 'df["' in code and '"] =' in code


def test_generate_data_loader_custom_operations(complex_spec):
    """Test that custom operations are generated correctly."""
    code = generate_data_loader(complex_spec)

    # Check for custom operations
    has_custom = False
    for c in complex_spec.components:
        if c.data_transform and c.data_transform.get('operations'):
            for op in c.data_transform['operations']:
                if op.type == 'custom' and op.custom_code:
                    has_custom = True
                    assert op.custom_code in code


def test_generate_data_loader_filter_application(complex_spec):
    """Test that filters are applied in load_and_filter_data."""
    code = generate_data_loader(complex_spec)

    # Check that each filter has corresponding application logic
    for filter_spec in complex_spec.filters:
        filter_id = filter_spec.id.replace('-', '_')
        assert f"{filter_id}_values" in code

        # Should have filter logic
        assert f"if {filter_id}_values:" in code


def test_generate_custom_logic_syntax(complex_spec):
    """Test that generated _custom_logic.py has valid Python syntax."""
    code = generate_custom_logic(complex_spec)

    # Parse to check syntax
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated code has syntax error: {e}\n\nGenerated code:\n{code}")


def test_generate_custom_logic_contains_examples(complex_spec):
    """Test that generated _custom_logic.py contains example functions."""
    code = generate_custom_logic(complex_spec)

    # Should contain example comments
    assert "# Example custom transformation function:" in code
    assert "import pandas as pd" in code


def test_generate_data_loader_with_no_derived_columns(complex_spec):
    """Test generation with spec that has no derived columns."""
    # Temporarily remove derived columns
    original_derived = complex_spec.derived_columns
    complex_spec.derived_columns = None

    code = generate_data_loader(complex_spec)

    # Should still generate valid code
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated code has syntax error: {e}")

    # Restore original
    complex_spec.derived_columns = original_derived


def test_generate_data_loader_with_no_data_transform(complex_spec):
    """Test generation with spec that has no data_transform on any component."""
    # Store original data_transforms
    original_transforms = {c.id: c.data_transform for c in complex_spec.components}

    # Remove data_transform from all components
    for comp in complex_spec.components:
        comp.data_transform = None

    code = generate_data_loader(complex_spec)

    # Should still generate valid code with basic functions
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated code has syntax error: {e}")

    # Should have basic functions but no build_* functions
    assert "def _prepare_base_df(df: pd.DataFrame) -> pd.DataFrame:" in code
    assert "def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:" in code
    assert "def load_and_filter_data(" in code
    # No build functions
    assert "def build_" not in code

    # Restore original data_transforms
    for comp in complex_spec.components:
        comp.data_transform = original_transforms[comp.id]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
