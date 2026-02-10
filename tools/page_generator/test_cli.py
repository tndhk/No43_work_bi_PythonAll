"""Tests for CLI module."""
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from .cli import main, generate_file, ALL_FILE_TYPES


def create_minimal_spec() -> str:
    """Create a minimal valid page_spec.yaml content.

    Returns:
        YAML string with minimal valid structure
    """
    return """
metadata:
  dashboard_id: test_page
  id_prefix: tp-
  title: Test Page
  dataset_id: test_dataset

column_map:
  date: date_column

filters: []

components: []

layout:
  sections: []
"""


def create_complex_spec() -> str:
    """Create a complex page_spec.yaml for comprehensive testing.

    Returns:
        YAML string with filters, components, and layout
    """
    return """
metadata:
  dashboard_id: test_page
  id_prefix: tp-
  title: Test Page
  dataset_id: test_dataset

column_map:
  date: date_column
  value: value_column
  count: count_column

filters:
  - id: tp-filter-date
    label: Date Range
    type: date
    column: date

components:
  - id: tp-kpi-total
    type: kpi
    title: Total Count
    spec:
      value_column: count
      agg_func: sum

  - id: tp-chart-line
    type: chart
    title: Trend
    spec:
      title: Trend Chart
      chart_type: line
      x_column: date
      y_columns: [value]

  - id: tp-table-main
    type: table
    title: Data Table
    spec:
      title: Data Table

layout:
  sections:
    - rows:
        - items:
            - component_id: tp-kpi-total
              md: 12
        - items:
            - component_id: tp-chart-line
              md: 12
        - items:
            - component_id: tp-table-main
              md: 12
"""


class TestCLIArgumentParsing:
    """Test CLI argument parsing."""

    def test_help_display(self, capsys):
        """Test --help displays usage information."""
        with pytest.raises(SystemExit) as exc_info:
            main(['--help'])

        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert 'Generate dashboard page from page_spec.yaml' in captured.out
        assert '--files' in captured.out
        assert '--dry-run' in captured.out
        assert 'Examples:' in captured.out

    def test_missing_page_dir_argument(self, capsys):
        """Test error when page_dir is not provided."""
        with pytest.raises(SystemExit) as exc_info:
            main([])

        assert exc_info.value.code != 0

    def test_invalid_file_type(self, capsys):
        """Test error when invalid --files value is provided."""
        with pytest.raises(SystemExit) as exc_info:
            main(['some_dir', '--files', 'invalid_file_type'])

        assert exc_info.value.code != 0


class TestFileGeneration:
    """Test file generation functionality."""

    def test_generate_single_file(self, tmp_path):
        """Test generating a single file."""
        # Create minimal page_spec.yaml
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        (page_dir / "page_spec.yaml").write_text(create_minimal_spec())

        # Generate constants file
        result = main([str(page_dir), '--files', 'constants'])

        assert result == 0
        assert (page_dir / "_constants.py").exists()

        content = (page_dir / "_constants.py").read_text()
        assert 'DASHBOARD_ID' in content and '"test_page"' in content
        assert 'DATASET_ID' in content and '"test_dataset"' in content

    def test_generate_multiple_files(self, tmp_path):
        """Test generating multiple specific files."""
        # Create minimal page_spec.yaml
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        (page_dir / "page_spec.yaml").write_text(create_minimal_spec())

        # Generate multiple files
        result = main([str(page_dir), '--files', 'constants', 'layout'])

        assert result == 0
        assert (page_dir / "_constants.py").exists()
        assert (page_dir / "_layout.py").exists()

    def test_generate_all_files_default(self, tmp_path):
        """Test generating all files (default behavior)."""
        # Create minimal page_spec.yaml
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        (page_dir / "page_spec.yaml").write_text(create_minimal_spec())

        # Generate all files (default)
        result = main([str(page_dir)])

        assert result == 0

        # Check all expected files exist
        expected_files = [
            "_constants.py",
            "_layout.py",
            "_filters.py",
            "_data_loader.py",
            "_custom_logic.py",
            "_callbacks.py",
            "_chart_builders.py",
        ]
        for filename in expected_files:
            assert (page_dir / filename).exists(), f"{filename} was not generated"

    def test_generate_all_files_explicit(self, tmp_path):
        """Test generating all files with --files all."""
        # Create minimal page_spec.yaml
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        (page_dir / "page_spec.yaml").write_text(create_minimal_spec())

        # Generate all files explicitly
        result = main([str(page_dir), '--files', 'all'])

        assert result == 0

        # Check all expected files exist
        expected_files = [
            "_constants.py",
            "_layout.py",
            "_filters.py",
            "_data_loader.py",
            "_custom_logic.py",
            "_callbacks.py",
            "_chart_builders.py",
        ]
        for filename in expected_files:
            assert (page_dir / filename).exists(), f"{filename} was not generated"


class TestDryRunMode:
    """Test dry run mode."""

    def test_dry_run_no_files_created(self, tmp_path, capsys):
        """Test that dry run does not create files."""
        # Create minimal page_spec.yaml
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        (page_dir / "page_spec.yaml").write_text(create_minimal_spec())

        # Run in dry-run mode
        result = main([str(page_dir), '--files', 'constants', '--dry-run'])

        assert result == 0

        # File should not be created
        assert not (page_dir / "_constants.py").exists()

        # But output should be printed
        captured = capsys.readouterr()
        assert '_constants.py' in captured.out
        assert 'DASHBOARD_ID' in captured.out and '"test_page"' in captured.out
        assert 'Dry run completed' in captured.out

    def test_dry_run_shows_output(self, tmp_path, capsys):
        """Test that dry run prints generated code to stdout."""
        # Create minimal page_spec.yaml
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        (page_dir / "page_spec.yaml").write_text(create_minimal_spec())

        # Run in dry-run mode
        result = main([str(page_dir), '--files', 'constants', '--dry-run'])

        assert result == 0

        captured = capsys.readouterr()
        assert '=' * 60 in captured.out
        assert 'DASHBOARD_ID' in captured.out
        assert 'DATASET_ID' in captured.out


class TestErrorHandling:
    """Test error handling."""

    def test_nonexistent_directory(self, capsys):
        """Test error when page directory does not exist."""
        result = main(['/nonexistent/directory'])

        assert result == 1

        captured = capsys.readouterr()
        assert 'Directory not found' in captured.err

    def test_missing_page_spec_yaml(self, tmp_path, capsys):
        """Test error when page_spec.yaml is missing."""
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        result = main([str(page_dir)])

        assert result == 1

        captured = capsys.readouterr()
        assert 'page_spec.yaml not found' in captured.err

    def test_invalid_yaml_syntax(self, tmp_path, capsys):
        """Test error when YAML syntax is invalid."""
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        # Create invalid YAML
        (page_dir / "page_spec.yaml").write_text("invalid: yaml: syntax: [")

        result = main([str(page_dir), '--files', 'constants'])

        assert result == 1

        captured = capsys.readouterr()
        assert 'Error loading' in captured.err

    def test_invalid_yaml_schema(self, tmp_path, capsys):
        """Test error when YAML schema validation fails."""
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        # Create YAML with missing required fields
        spec_content = """
metadata:
  page_id: test_page
  # Missing title and dataset_id

filters: []
"""
        (page_dir / "page_spec.yaml").write_text(spec_content)

        result = main([str(page_dir), '--files', 'constants'])

        assert result == 1

        captured = capsys.readouterr()
        assert 'Error loading' in captured.err


class TestGenerateFileFunction:
    """Test the generate_file function directly."""

    def test_generate_file_success(self, tmp_path):
        """Test generate_file returns True on success."""
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        (page_dir / "page_spec.yaml").write_text(create_minimal_spec())

        result = generate_file(page_dir, 'constants', dry_run=False)

        assert result is True
        assert (page_dir / "_constants.py").exists()

    def test_generate_file_missing_spec(self, tmp_path, capsys):
        """Test generate_file returns False when spec is missing."""
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        result = generate_file(page_dir, 'constants', dry_run=False)

        assert result is False

        captured = capsys.readouterr()
        assert 'Error loading' in captured.err

    def test_generate_file_dry_run(self, tmp_path, capsys):
        """Test generate_file in dry run mode."""
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        (page_dir / "page_spec.yaml").write_text(create_minimal_spec())

        result = generate_file(page_dir, 'constants', dry_run=True)

        assert result is True
        assert not (page_dir / "_constants.py").exists()

        captured = capsys.readouterr()
        assert 'DASHBOARD_ID' in captured.out


class TestAllFileTypes:
    """Test that all file types can be generated."""

    def test_all_file_types_in_generators(self):
        """Test that ALL_FILE_TYPES matches available generators."""
        from .cli import FILE_GENERATORS

        assert set(ALL_FILE_TYPES) == set(FILE_GENERATORS.keys())

    def test_each_file_type_generates(self, tmp_path):
        """Test that each file type can be generated individually."""
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        (page_dir / "page_spec.yaml").write_text(create_complex_spec())

        # Test each file type
        for file_type in ALL_FILE_TYPES:
            result = generate_file(page_dir, file_type, dry_run=False)
            assert result is True, f"Failed to generate {file_type}"

            filename = {
                'constants': '_constants.py',
                'layout': '_layout.py',
                'filters': '_filters.py',
                'data_loader': '_data_loader.py',
                'custom_logic': '_custom_logic.py',
                'callbacks': '_callbacks.py',
                'chart_builders': '_chart_builders.py',
            }[file_type]

            assert (page_dir / filename).exists(), f"{filename} was not created"


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def test_new_page_creation_workflow(self, tmp_path):
        """Test complete workflow of creating a new page."""
        page_dir = tmp_path / "my_new_page"
        page_dir.mkdir()

        # Minimal spec for new page - customize it
        spec_content = """
metadata:
  dashboard_id: my_new_page
  id_prefix: mnp-
  title: My New Page
  dataset_id: my_dataset

column_map:
  date: date_column

filters: []

components: []

layout:
  sections: []
"""
        (page_dir / "page_spec.yaml").write_text(spec_content)

        # Generate only custom_logic skeleton first
        result = main([str(page_dir), '--files', 'custom_logic'])
        assert result == 0
        assert (page_dir / "_custom_logic.py").exists()

        # Then generate all remaining files
        result = main([str(page_dir), '--files', 'constants', 'layout', 'filters',
                      'data_loader', 'callbacks', 'chart_builders'])
        assert result == 0

        # Verify all files exist
        expected_files = [
            "_constants.py",
            "_layout.py",
            "_filters.py",
            "_data_loader.py",
            "_custom_logic.py",
            "_callbacks.py",
            "_chart_builders.py",
        ]
        for filename in expected_files:
            assert (page_dir / filename).exists()

    def test_regenerate_after_spec_change(self, tmp_path):
        """Test regenerating files after spec changes."""
        page_dir = tmp_path / "test_page"
        page_dir.mkdir()

        # Initial spec
        spec_content_v1 = """
metadata:
  dashboard_id: test_page
  id_prefix: tp-
  title: Test Page v1
  dataset_id: test_dataset

column_map:
  date: date_column

filters: []

components: []

layout:
  sections: []
"""
        (page_dir / "page_spec.yaml").write_text(spec_content_v1)

        # Generate initial files
        result = main([str(page_dir)])
        assert result == 0

        initial_constants = (page_dir / "_constants.py").read_text()
        assert 'Test Page v1' in initial_constants

        # Update spec
        spec_content_v2 = """
metadata:
  dashboard_id: test_page
  id_prefix: tp-
  title: Test Page v2 Updated
  dataset_id: test_dataset

column_map:
  date: date_column

filters: []

components: []

layout:
  sections: []
"""
        (page_dir / "page_spec.yaml").write_text(spec_content_v2)

        # Regenerate
        result = main([str(page_dir), '--files', 'constants'])
        assert result == 0

        updated_constants = (page_dir / "_constants.py").read_text()
        assert 'Test Page v2 Updated' in updated_constants
        assert 'Test Page v1' not in updated_constants
