"""Tests for dashboard data source registry."""
from __future__ import annotations

from pathlib import Path
import pytest


def _write_yaml(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_load_dashboard_config_reads_charts(tmp_path, monkeypatch):
    import src.data.data_source_registry as registry

    pages_dir = tmp_path / "pages"
    _write_yaml(
        pages_dir / "sample" / registry.DASHBOARD_CONFIG_FILENAME,
        "charts:\n  chart-a: dataset-a\n",
    )

    monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
    registry.load_dashboard_config.cache_clear()

    config = registry.load_dashboard_config("sample")
    assert config["charts"]["chart-a"] == "dataset-a"


def test_load_dashboard_config_missing_file_raises(tmp_path, monkeypatch):
    import src.data.data_source_registry as registry

    pages_dir = tmp_path / "pages"
    monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
    registry.load_dashboard_config.cache_clear()

    with pytest.raises(FileNotFoundError):
        registry.load_dashboard_config("missing")


def test_load_dashboard_config_invalid_yaml_raises(tmp_path, monkeypatch):
    import src.data.data_source_registry as registry

    pages_dir = tmp_path / "pages"
    _write_yaml(
        pages_dir / "bad" / registry.DASHBOARD_CONFIG_FILENAME,
        "- not: a mapping\n- just: a list\n",
    )

    monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
    registry.load_dashboard_config.cache_clear()

    with pytest.raises(ValueError):
        registry.load_dashboard_config("bad")


def test_get_dataset_id_returns_value(tmp_path, monkeypatch):
    import src.data.data_source_registry as registry

    pages_dir = tmp_path / "pages"
    _write_yaml(
        pages_dir / "sample" / registry.DASHBOARD_CONFIG_FILENAME,
        "charts:\n  chart-a: dataset-a\n",
    )

    monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
    registry.load_dashboard_config.cache_clear()

    dataset_id = registry.get_dataset_id("sample", "chart-a")
    assert dataset_id == "dataset-a"


def test_get_dataset_id_missing_chart_returns_none(tmp_path, monkeypatch):
    import src.data.data_source_registry as registry

    pages_dir = tmp_path / "pages"
    _write_yaml(
        pages_dir / "sample" / registry.DASHBOARD_CONFIG_FILENAME,
        "charts:\n  chart-a: dataset-a\n",
    )

    monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
    registry.load_dashboard_config.cache_clear()

    dataset_id = registry.get_dataset_id("sample", "chart-missing")
    assert dataset_id is None


# ---- resolve_dataset_id tests ----


class TestResolveDatasetId:
    """Tests for resolve_dataset_id helper."""

    def test_returns_dataset_id_when_entry_exists(self, tmp_path, monkeypatch):
        """Registry has the entry -> return the dataset ID directly."""
        import src.data.data_source_registry as registry

        pages_dir = tmp_path / "pages"
        _write_yaml(
            pages_dir / "dash1" / registry.DASHBOARD_CONFIG_FILENAME,
            "charts:\n  chart-x: dataset-x\n",
        )
        monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
        registry.load_dashboard_config.cache_clear()

        result = registry.resolve_dataset_id("dash1", "chart-x")
        assert result == "dataset-x"

    def test_returns_fallback_when_entry_missing(self, tmp_path, monkeypatch):
        """Registry entry missing + fallback provided -> return fallback."""
        import src.data.data_source_registry as registry

        pages_dir = tmp_path / "pages"
        _write_yaml(
            pages_dir / "dash1" / registry.DASHBOARD_CONFIG_FILENAME,
            "charts:\n  chart-a: dataset-a\n",
        )
        monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
        registry.load_dashboard_config.cache_clear()

        result = registry.resolve_dataset_id(
            "dash1", "chart-missing", fallback="my-fallback"
        )
        assert result == "my-fallback"

    def test_raises_when_entry_missing_and_no_fallback(
        self, tmp_path, monkeypatch
    ):
        """Registry entry missing + no fallback -> raise ValueError."""
        import src.data.data_source_registry as registry

        pages_dir = tmp_path / "pages"
        _write_yaml(
            pages_dir / "dash1" / registry.DASHBOARD_CONFIG_FILENAME,
            "charts:\n  chart-a: dataset-a\n",
        )
        monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
        registry.load_dashboard_config.cache_clear()

        with pytest.raises(ValueError, match="Dataset ID not found"):
            registry.resolve_dataset_id("dash1", "chart-missing")

    def test_raises_when_entry_missing_and_fallback_explicitly_none(
        self, tmp_path, monkeypatch
    ):
        """Explicit fallback=None -> raise ValueError (same as default)."""
        import src.data.data_source_registry as registry

        pages_dir = tmp_path / "pages"
        _write_yaml(
            pages_dir / "dash1" / registry.DASHBOARD_CONFIG_FILENAME,
            "charts:\n  chart-a: dataset-a\n",
        )
        monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
        registry.load_dashboard_config.cache_clear()

        with pytest.raises(ValueError, match="Dataset ID not found"):
            registry.resolve_dataset_id("dash1", "chart-missing", fallback=None)

    def test_returns_registry_value_even_when_fallback_provided(
        self, tmp_path, monkeypatch
    ):
        """Registry has entry + fallback provided -> return registry value (not fallback)."""
        import src.data.data_source_registry as registry

        pages_dir = tmp_path / "pages"
        _write_yaml(
            pages_dir / "dash1" / registry.DASHBOARD_CONFIG_FILENAME,
            "charts:\n  chart-x: dataset-x\n",
        )
        monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
        registry.load_dashboard_config.cache_clear()

        result = registry.resolve_dataset_id(
            "dash1", "chart-x", fallback="should-not-use"
        )
        assert result == "dataset-x"

    def test_raises_when_config_file_missing_and_no_fallback(
        self, tmp_path, monkeypatch
    ):
        """Config file does not exist + no fallback -> propagate FileNotFoundError."""
        import src.data.data_source_registry as registry

        pages_dir = tmp_path / "pages"
        monkeypatch.setattr(registry, "DASHBOARD_PAGES_DIR", pages_dir)
        registry.load_dashboard_config.cache_clear()

        with pytest.raises(FileNotFoundError):
            registry.resolve_dataset_id("no-such-dashboard", "chart-a")
