"""Tests for backend/scripts/load_csv.py -- generic CSV loader script.

These tests define the expected interface:
- load_config(config_path) -> dict  : parse YAML and return top-level dict
- load_dataset(dataset_config, dry_run=False) -> bool : resolve CSV -> CsvETL -> run
- CLI via argparse: --list, --dataset, --all, --dry-run
"""
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CONFIG = {
    "datasets": [
        {
            "name": "Test Dataset A",
            "minio_dataset_id": "test-a",
            "source_dir": "backend/data_sources",
            "file_pattern": "test-a-*.csv",
            "partition_column": "Date",
            "enabled": True,
            "description": "Dataset A for testing",
        },
        {
            "name": "Test Dataset B",
            "minio_dataset_id": "test-b",
            "source_dir": "backend/data_sources",
            "file_pattern": "test-b.csv",
            "partition_column": None,
            "enabled": False,
            "description": "Dataset B (disabled)",
        },
    ]
}


@pytest.fixture
def yaml_config_file(tmp_path):
    """Write a sample YAML config to a temporary file and return its Path."""
    config_path = tmp_path / "csv_datasets.yaml"
    config_path.write_text(yaml.dump(SAMPLE_CONFIG), encoding="utf-8")
    return config_path


@pytest.fixture
def empty_yaml_file(tmp_path):
    """Write a YAML config with no datasets."""
    config_path = tmp_path / "csv_datasets_empty.yaml"
    config_path.write_text(yaml.dump({"datasets": []}), encoding="utf-8")
    return config_path


# ---------------------------------------------------------------------------
# 1. load_config -- YAML parsing
# ---------------------------------------------------------------------------

class TestLoadConfig:
    """load_config(config_path) should parse YAML and return the full dict."""

    def test_parses_yaml_correctly(self, yaml_config_file):
        """load_config returns a dict containing 'datasets' list."""
        from backend.scripts.load_csv import load_config

        result = load_config(yaml_config_file)

        assert isinstance(result, dict)
        assert "datasets" in result
        assert len(result["datasets"]) == 2

    def test_dataset_fields_present(self, yaml_config_file):
        """Each dataset entry contains the required fields."""
        from backend.scripts.load_csv import load_config

        result = load_config(yaml_config_file)
        ds = result["datasets"][0]

        assert ds["name"] == "Test Dataset A"
        assert ds["minio_dataset_id"] == "test-a"
        assert ds["source_dir"] == "backend/data_sources"
        assert ds["file_pattern"] == "test-a-*.csv"
        assert ds["partition_column"] == "Date"
        assert ds["enabled"] is True

    def test_raises_on_missing_file(self, tmp_path):
        """load_config raises FileNotFoundError for a nonexistent path."""
        from backend.scripts.load_csv import load_config

        nonexistent = tmp_path / "no_such_file.yaml"
        with pytest.raises(FileNotFoundError):
            load_config(nonexistent)

    def test_raises_on_empty_datasets(self, empty_yaml_file):
        """load_config raises ValueError when datasets list is empty."""
        from backend.scripts.load_csv import load_config

        with pytest.raises(ValueError):
            load_config(empty_yaml_file)


# ---------------------------------------------------------------------------
# 2. load_dataset -- orchestration (resolve_csv_path -> CsvETL -> run)
# ---------------------------------------------------------------------------

class TestLoadDataset:
    """load_dataset(dataset_config, dry_run) orchestrates the ETL pipeline."""

    @patch("backend.scripts.load_csv.CsvETL")
    @patch("backend.scripts.load_csv.resolve_csv_path")
    def test_calls_resolve_then_etl_run(self, mock_resolve, mock_etl_cls):
        """Normal execution: resolve_csv_path -> CsvETL(path, ...) -> run(minio_id)."""
        from backend.scripts.load_csv import load_dataset

        # Setup
        mock_resolve.return_value = Path("/tmp/resolved/test-a-2025-01.csv")
        mock_etl_instance = MagicMock()
        mock_etl_cls.return_value = mock_etl_instance

        ds_config = SAMPLE_CONFIG["datasets"][0]

        # Execute
        result = load_dataset(ds_config, dry_run=False)

        # Verify
        assert result is True
        mock_resolve.assert_called_once()
        mock_etl_cls.assert_called_once()
        mock_etl_instance.run.assert_called_once_with("test-a")

    @patch("backend.scripts.load_csv.CsvETL")
    @patch("backend.scripts.load_csv.resolve_csv_path")
    def test_passes_partition_column_to_etl(self, mock_resolve, mock_etl_cls):
        """CsvETL is constructed with partition_column from config."""
        from backend.scripts.load_csv import load_dataset

        mock_resolve.return_value = Path("/tmp/resolved.csv")
        mock_etl_instance = MagicMock()
        mock_etl_cls.return_value = mock_etl_instance

        ds_config = SAMPLE_CONFIG["datasets"][0]

        load_dataset(ds_config, dry_run=False)

        # CsvETL should receive partition_column="Date"
        call_kwargs = mock_etl_cls.call_args
        # Check keyword arg or positional -- partition_column should be "Date"
        assert call_kwargs.kwargs.get("partition_column") == "Date" or \
               (len(call_kwargs.args) >= 2 and call_kwargs.args[1] == "Date")

    @patch("backend.scripts.load_csv.CsvETL")
    @patch("backend.scripts.load_csv.resolve_csv_path")
    def test_passes_csv_options_to_etl(self, mock_resolve, mock_etl_cls):
        """CsvETL receives csv_options when present in config."""
        from backend.scripts.load_csv import load_dataset

        mock_resolve.return_value = Path("/tmp/resolved.csv")
        mock_etl_instance = MagicMock()
        mock_etl_cls.return_value = mock_etl_instance

        ds_config = {
            **SAMPLE_CONFIG["datasets"][0],
            "csv_options": {"delimiter": ";", "encoding": "shift_jis"},
        }

        load_dataset(ds_config, dry_run=False)

        call_kwargs = mock_etl_cls.call_args
        assert "csv_options" in call_kwargs.kwargs or len(call_kwargs.args) >= 3

    @patch("backend.scripts.load_csv.CsvETL")
    @patch("backend.scripts.load_csv.resolve_csv_path")
    def test_returns_false_on_etl_error(self, mock_resolve, mock_etl_cls):
        """load_dataset returns False when ETL raises an exception."""
        from backend.scripts.load_csv import load_dataset

        mock_resolve.return_value = Path("/tmp/resolved.csv")
        mock_etl_instance = MagicMock()
        mock_etl_instance.run.side_effect = RuntimeError("S3 connection failed")
        mock_etl_cls.return_value = mock_etl_instance

        ds_config = SAMPLE_CONFIG["datasets"][0]

        result = load_dataset(ds_config, dry_run=False)

        assert result is False


# ---------------------------------------------------------------------------
# 3. --dry-run: ETL must NOT be executed
# ---------------------------------------------------------------------------

class TestDryRun:
    """--dry-run flag should prevent ETL execution."""

    @patch("backend.scripts.load_csv.CsvETL")
    @patch("backend.scripts.load_csv.resolve_csv_path")
    def test_dry_run_skips_etl(self, mock_resolve, mock_etl_cls):
        """With dry_run=True, CsvETL is never instantiated or run."""
        from backend.scripts.load_csv import load_dataset

        ds_config = SAMPLE_CONFIG["datasets"][0]

        result = load_dataset(ds_config, dry_run=True)

        assert result is True
        mock_etl_cls.assert_not_called()
        # resolve_csv_path may or may not be called (implementation choice)
        # but CsvETL.run must NOT be called

    @patch("backend.scripts.load_csv.CsvETL")
    @patch("backend.scripts.load_csv.resolve_csv_path")
    def test_dry_run_returns_true(self, mock_resolve, mock_etl_cls):
        """dry_run always returns True (success) without performing work."""
        from backend.scripts.load_csv import load_dataset

        ds_config = SAMPLE_CONFIG["datasets"][1]  # disabled dataset

        result = load_dataset(ds_config, dry_run=True)

        assert result is True


# ---------------------------------------------------------------------------
# 4. --list: dataset listing
# ---------------------------------------------------------------------------

class TestListDatasets:
    """--list displays configured datasets."""

    def test_list_datasets_prints_names(self, capsys):
        """list_datasets should print dataset names and status."""
        from backend.scripts.load_csv import list_datasets

        datasets = SAMPLE_CONFIG["datasets"]

        list_datasets(datasets)

        captured = capsys.readouterr().out
        assert "Test Dataset A" in captured
        assert "Test Dataset B" in captured

    def test_list_datasets_shows_enabled_count(self, capsys):
        """list_datasets should show enabled/disabled counts."""
        from backend.scripts.load_csv import list_datasets

        datasets = SAMPLE_CONFIG["datasets"]

        list_datasets(datasets)

        captured = capsys.readouterr().out
        # 1 enabled, 1 disabled
        assert "Enabled: 1" in captured or "Enabled" in captured

    def test_list_datasets_shows_source_info(self, capsys):
        """list_datasets should show source_dir and file_pattern."""
        from backend.scripts.load_csv import list_datasets

        datasets = SAMPLE_CONFIG["datasets"]

        list_datasets(datasets)

        captured = capsys.readouterr().out
        assert "backend/data_sources" in captured or "test-a-*.csv" in captured


# ---------------------------------------------------------------------------
# 5. CLI argument parsing (main function)
# ---------------------------------------------------------------------------

class TestCLI:
    """CLI argparse integration tests."""

    @patch("backend.scripts.load_csv.load_config")
    @patch("backend.scripts.load_csv.list_datasets")
    def test_list_flag_calls_list_datasets(self, mock_list, mock_config):
        """--list calls list_datasets and exits."""
        from backend.scripts.load_csv import main

        mock_config.return_value = {"datasets": SAMPLE_CONFIG["datasets"]}

        with pytest.raises(SystemExit) as exc_info:
            main(["--list"])

        assert exc_info.value.code == 0
        mock_list.assert_called_once()

    @patch("backend.scripts.load_csv.load_config")
    @patch("backend.scripts.load_csv.load_dataset")
    def test_dataset_flag_loads_specific(self, mock_load_ds, mock_config):
        """--dataset 'Name' loads only that dataset."""
        from backend.scripts.load_csv import main

        mock_config.return_value = {"datasets": SAMPLE_CONFIG["datasets"]}
        mock_load_ds.return_value = True

        main(["--dataset", "Test Dataset A"])

        mock_load_ds.assert_called_once()
        call_args = mock_load_ds.call_args
        assert call_args[0][0]["name"] == "Test Dataset A"

    @patch("backend.scripts.load_csv.load_config")
    @patch("backend.scripts.load_csv.load_dataset")
    def test_all_flag_loads_only_enabled(self, mock_load_ds, mock_config):
        """--all loads only enabled datasets."""
        from backend.scripts.load_csv import main

        mock_config.return_value = {"datasets": SAMPLE_CONFIG["datasets"]}
        mock_load_ds.return_value = True

        main(["--all"])

        # Only 1 dataset is enabled
        assert mock_load_ds.call_count == 1
        call_args = mock_load_ds.call_args
        assert call_args[0][0]["name"] == "Test Dataset A"

    @patch("backend.scripts.load_csv.load_config")
    @patch("backend.scripts.load_csv.load_dataset")
    def test_dry_run_flag_passed_through(self, mock_load_ds, mock_config):
        """--dry-run passes dry_run=True to load_dataset."""
        from backend.scripts.load_csv import main

        mock_config.return_value = {"datasets": SAMPLE_CONFIG["datasets"]}
        mock_load_ds.return_value = True

        main(["--all", "--dry-run"])

        call_args = mock_load_ds.call_args
        assert call_args[0][1] is True or call_args[1].get("dry_run") is True

    @patch("backend.scripts.load_csv.load_config")
    def test_no_flags_shows_help_and_exits(self, mock_config):
        """No action flags prints help and exits with error."""
        from backend.scripts.load_csv import main

        mock_config.return_value = {"datasets": SAMPLE_CONFIG["datasets"]}

        with pytest.raises(SystemExit) as exc_info:
            main([])

        assert exc_info.value.code == 1

    @patch("backend.scripts.load_csv.load_config")
    def test_unknown_dataset_exits_with_error(self, mock_config):
        """--dataset with nonexistent name exits with error."""
        from backend.scripts.load_csv import main

        mock_config.return_value = {"datasets": SAMPLE_CONFIG["datasets"]}

        with pytest.raises(SystemExit) as exc_info:
            main(["--dataset", "Nonexistent Dataset"])

        assert exc_info.value.code == 1
