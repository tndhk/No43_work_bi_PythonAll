"""Resolve the latest CSV file matching a glob pattern in a directory."""
from pathlib import Path


def resolve_csv_path(source_dir: str, file_pattern: str) -> Path:
    """Return the latest file matching *file_pattern* inside *source_dir*.

    Files are sorted in lexicographic order by name; the last entry is
    returned.  ISO-date suffixes (``YYYY-MM-DD``) therefore map to
    chronological order automatically.

    Raises
    ------
    FileNotFoundError
        If *source_dir* does not exist or no files match *file_pattern*.
    """
    dir_path = Path(source_dir)

    if not dir_path.is_dir():
        raise FileNotFoundError(
            f"Directory not found: {source_dir}"
        )

    matches = sorted(dir_path.glob(file_pattern))

    if not matches:
        raise FileNotFoundError(
            f"No files matching '{file_pattern}' in {source_dir}"
        )

    return matches[-1]
