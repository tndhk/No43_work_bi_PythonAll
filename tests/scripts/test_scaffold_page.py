"""Tests for scripts/scaffold_page.py scaffold generator."""
import ast
from pathlib import Path

import pytest
import yaml

# Import the scaffold function and TEMPLATES from the script
import sys

# Ensure project root is on sys.path so we can import the script module
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

from scaffold_page import scaffold_page, TEMPLATES  # noqa: E402


# ---------------------------------------------------------------------------
# Shared fixture: common scaffold arguments
# ---------------------------------------------------------------------------

@pytest.fixture()
def scaffold_args():
    """Return a dict of default scaffold arguments for tests."""
    return {
        "name": "sales_report",
        "title": "Sales Report Dashboard",
        "path": "/sales-report",
        "dataset_id": "sales-data",
        "prefix": "sr-",
    }


@pytest.fixture()
def scaffolded_dir(tmp_path, scaffold_args):
    """Run scaffold_page and return the generated package directory."""
    pages_dir = tmp_path / "src" / "pages"
    pages_dir.mkdir(parents=True)
    return scaffold_page(pages_dir=pages_dir, **scaffold_args)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


EXPECTED_FILES = [
    "__init__.py",
    "_constants.py",
    "_data_loader.py",
    "_filters.py",
    "_layout.py",
    "_callbacks.py",
    "_chart_builders.py",
    "SPEC.md",
    "data_sources.yml",
]


class TestScaffoldCreatesAllFiles:
    """test_scaffold_creates_all_files -- tmp_path に全9ファイルが生成される"""

    def test_scaffold_creates_all_files(self, scaffolded_dir):
        generated = sorted(f.name for f in scaffolded_dir.iterdir() if f.is_file())
        expected = sorted(EXPECTED_FILES)
        assert generated == expected


class TestScaffoldGeneratesValidPython:
    """test_scaffold_generates_valid_python -- 生成されたPythonファイルが ast.parse で構文チェックを通る"""

    @pytest.mark.parametrize(
        "filename",
        [f for f in EXPECTED_FILES if f.endswith(".py")],
    )
    def test_scaffold_generates_valid_python(self, scaffolded_dir, filename):
        source = (scaffolded_dir / filename).read_text(encoding="utf-8")
        # ast.parse raises SyntaxError if the source is invalid
        ast.parse(source, filename=filename)


class TestScaffoldIdPrefixSubstituted:
    """test_scaffold_id_prefix_substituted -- _constants.py に ID_PREFIX = "sr-" が含まれる"""

    def test_scaffold_id_prefix_substituted(self, scaffolded_dir):
        content = (scaffolded_dir / "_constants.py").read_text(encoding="utf-8")
        assert 'ID_PREFIX: str = "sr-"' in content


class TestScaffoldDatasetIdSubstituted:
    """test_scaffold_dataset_id_substituted -- _constants.py に DATASET_ID = "sales-data" が含まれる"""

    def test_scaffold_dataset_id_substituted(self, scaffolded_dir):
        content = (scaffolded_dir / "_constants.py").read_text(encoding="utf-8")
        assert 'DATASET_ID: str = "sales-data"' in content


class TestScaffoldRaisesOnExistingDir:
    """test_scaffold_raises_on_existing_dir -- 既存ディレクトリに対して SystemExit が発生"""

    def test_scaffold_raises_on_existing_dir(self, tmp_path, scaffold_args):
        pages_dir = tmp_path / "src" / "pages"
        pages_dir.mkdir(parents=True)

        # First scaffold should succeed
        scaffold_page(pages_dir=pages_dir, **scaffold_args)

        # Second scaffold to the same directory should raise SystemExit
        with pytest.raises(SystemExit):
            scaffold_page(pages_dir=pages_dir, **scaffold_args)


class TestScaffoldDataSourcesValidYaml:
    """test_scaffold_data_sources_valid_yaml -- data_sources.yml が有効なYAMLとしてパースできる"""

    def test_scaffold_data_sources_valid_yaml(self, scaffolded_dir):
        content = (scaffolded_dir / "data_sources.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert isinstance(data, dict)
        assert "charts" in data
        assert isinstance(data["charts"], dict)
        # Verify all chart IDs map to the correct dataset
        for chart_id, ds_id in data["charts"].items():
            assert chart_id.startswith("sr-"), f"Chart ID {chart_id} missing prefix"
            assert ds_id == "sales-data"


class TestScaffoldSpecMdHasJapaneseSections:
    """test_scaffold_spec_md_has_japanese_sections -- SPEC.mdに「概要」「データソース」「フィルタ」「チャート」を含む"""

    def test_scaffold_spec_md_has_japanese_sections(self, scaffolded_dir):
        content = (scaffolded_dir / "SPEC.md").read_text(encoding="utf-8")
        for section in ["概要", "データソース", "フィルタ", "チャート"]:
            assert section in content, f"SPEC.md missing section: {section}"
