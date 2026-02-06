"""Tests for resolve_csv_path utility."""
import pytest
from pathlib import Path

from backend.etl.resolve_csv_path import resolve_csv_path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def csv_dir_multiple(tmp_path):
    """Create a temp directory with multiple CSV files matching a glob pattern."""
    (tmp_path / "team-usage-events-2025-01.csv").write_text("h\n1")
    (tmp_path / "team-usage-events-2025-02.csv").write_text("h\n2")
    (tmp_path / "team-usage-events-2025-03.csv").write_text("h\n3")
    return tmp_path


@pytest.fixture
def csv_dir_single(tmp_path):
    """Create a temp directory with exactly one matching CSV file."""
    (tmp_path / "team-usage-events-2025-06.csv").write_text("h\n1")
    return tmp_path


@pytest.fixture
def csv_dir_empty(tmp_path):
    """Create a temp directory with no matching CSV files."""
    # unrelated file that should NOT match the pattern
    (tmp_path / "other-report.csv").write_text("h\n1")
    return tmp_path


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------


class TestResolveMultipleFiles:
    """glob パターンに一致する複数ファイルから最新（辞書順末尾）を返す。"""

    def test_returns_latest_by_lexicographic_order(self, csv_dir_multiple):
        # Given: 3 files matching the pattern (2025-01, 2025-02, 2025-03)
        pattern = "team-usage-events-*.csv"

        # When
        result = resolve_csv_path(str(csv_dir_multiple), pattern)

        # Then: the lexicographically last file (2025-03) is selected
        assert result == csv_dir_multiple / "team-usage-events-2025-03.csv"

    def test_return_type_is_path(self, csv_dir_multiple):
        # Given / When
        result = resolve_csv_path(str(csv_dir_multiple), "team-usage-events-*.csv")

        # Then
        assert isinstance(result, Path)


class TestResolveSingleFile:
    """一致ファイルが1つだけの場合はそれを返す。"""

    def test_returns_the_only_matching_file(self, csv_dir_single):
        # Given: 1 file matching the pattern
        pattern = "team-usage-events-*.csv"

        # When
        result = resolve_csv_path(str(csv_dir_single), pattern)

        # Then
        assert result == csv_dir_single / "team-usage-events-2025-06.csv"


class TestResolveNoMatch:
    """一致ファイルが0件の場合は FileNotFoundError。"""

    def test_raises_file_not_found_error(self, csv_dir_empty):
        # Given: no files match the pattern
        pattern = "team-usage-events-*.csv"

        # When / Then
        with pytest.raises(FileNotFoundError):
            resolve_csv_path(str(csv_dir_empty), pattern)

    def test_raises_on_nonexistent_directory(self, tmp_path):
        # Given: directory does not exist
        no_dir = str(tmp_path / "nonexistent")
        pattern = "team-usage-events-*.csv"

        # When / Then
        with pytest.raises(FileNotFoundError):
            resolve_csv_path(no_dir, pattern)


class TestResolveExactPath:
    """完全パス指定（globなし）の場合はそのまま返す。"""

    def test_returns_exact_path_when_no_glob(self, csv_dir_single):
        # Given: an exact filename with no glob metacharacters
        exact_name = "team-usage-events-2025-06.csv"

        # When
        result = resolve_csv_path(str(csv_dir_single), exact_name)

        # Then: the exact file is returned as-is
        assert result == csv_dir_single / exact_name

    def test_exact_path_missing_raises_error(self, tmp_path):
        # Given: exact filename that does not exist
        exact_name = "does-not-exist.csv"

        # When / Then
        with pytest.raises(FileNotFoundError):
            resolve_csv_path(str(tmp_path), exact_name)
